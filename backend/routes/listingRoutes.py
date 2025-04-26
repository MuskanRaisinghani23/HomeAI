from snowflake.connector import DictCursor
from snowflake.snowpark import Session
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
from pydantic import BaseModel
from connections import snowflake_connection, load_snowflake_config
import json
from typing import Optional

router = APIRouter()

config = load_snowflake_config()

session = Session.builder.configs(config).create()

class SearchParams(BaseModel):
    q: str
    k: int = 10
    
class FeedbackParams(BaseModel):
    user_email: str
    comments: str
    room_id: int

class PreferenceParams(BaseModel):
    user_email: str
    room_type:  Optional[str] = None
    city:       Optional[str] = None
    location:   Optional[str] = None
    amenities:  Optional[bool] = None
    getalerts:  Optional[bool] = None
    bedroom:    Optional[int]  = None
    bathroom:   Optional[int]  = None
    minprice:   Optional[int]  = None
    maxprice:   Optional[int]  = None

class AskRequest(BaseModel):
    query: str

# @router.post("/ask")
# async def ask(req: AskRequest):
#     """
#     Takes the user's free-text query, feeds it into the Cortex Agent,
#     and returns a natural-language reply—using only Snowflake LLMs & Search.
#     """
#     try:
#         reply = agent(req.query)
#         return {"reply": reply}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
    # # (Optional) If you also want to run SQL on structured data:
# analyst_tool = CortexAnalystTool(
#     snowflake_connection=session,
#     semantic_model="MY_SCHEMA.MY_ANALYST_MODEL"
# )

@router.get("/get-listings")
async def get_filtered_listings(
    location: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    room_type: Optional[str] = Query(None, regex="^(Shared|Private)$"),
    laundry_availability: Optional[bool] = None,
):
    """
    Get filtered room listings.
    """
    try:
        conn = snowflake_connection()
        cursor = conn.cursor()

        query = """
        SELECT 
            room_id, location, listing_url, listing_date, price, description_summary,
            image_url, source, other_details,
            room_count, bath_count, people_count, contact,
            report_count, room_type, laundry_available
        FROM ROOMS_LISTINGS
        WHERE report_count < 3
        """

        filters = []
        params = []

        if location:
            filters.append("LOWER(location) LIKE LOWER(%s)")
            params.append(f"%{location.strip()}%")

        if min_price is not None:
            filters.append("price >= %s")
            params.append(min_price)

        if max_price is not None:
            filters.append("price <= %s")
            params.append(max_price)

        if room_type:
            filters.append("LOWER(room_type) = LOWER(%s)")
            params.append(room_type.strip())

        if laundry_availability is not None:
            filters.append("laundry_available = %s")
            params.append(laundry_availability)

        if filters:
            query += " AND " + " AND ".join(filters)

        query += " ORDER BY listing_date DESC LIMIT 10"

        cursor.execute(query, tuple(params))
        results = cursor.fetchall()

        listings = [
            {   
                "ROOM_ID": row[0],
                "LOCATION": row[1],
                "LISTING_URL": row[2],
                "LISTING_DATE": row[3],
                "PRICE": row[4],
                "DESCRIPTION_SUMMARY": row[5],
                "IMAGE_URL": row[6],
                "SOURCE": row[7],
                "OTHER_DETAILS": row[8],
                "ROOM_COUNT": row[9],
                "BATH_COUNT": row[10],
                "PEOPLE_COUNT": row[11],
                "CONTACT": row[12],
                "REPORT_COUNT": row[13],
                "ROOM_TYPE": row[14],
                "LAUNDRY_AVAILABLE": row[15],
            }
            for row in results
        ]

        cursor.close()
        conn.close()

        return {"status": "success", "data": listings}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching listings: {str(e)}")


@router.post("/search-listings", response_model=List[Dict])
async def search_listings(params: SearchParams):
    service = "HOME_AI_SCHEMA.MY_LISTINGS_SEARCH"
    fetch_limit = max(params.k * 3, 20)

    conn = snowflake_connection()
    cur = conn.cursor(DictCursor)

    try:
        classification_prompt = (
            f"Classify the following input into one of these categories:\n"
            f"- greeting\n"
            f"- listing_question\n"
            f"- unrelated_question\n\n"
            f"Only return one word: greeting, listing_question, or unrelated_question.\n\n"
            f"Input: {params.q}"
        )

        classify_sql = """
        SELECT SNOWFLAKE.CORTEX.COMPLETE('claude-3-5-sonnet', %s)
        """
        cur.execute(classify_sql, (classification_prompt,))
        classify_row = cur.fetchone()
        classification = classify_row[list(classify_row.keys())[0]].strip().lower()

        if "greeting" in classification:
            return [{"response": "Hi! I'm here to assist you in finding rooms. Please type your preferred location, budget, or other needs."}]
        
        elif "unrelated_question" in classification:
            return [{"response": "Sorry, I'm unable to answer that question. I'm here to assist you in finding rooms. Please type your preferred location, budget, or other needs."}]
        
        elif "listing_question" in classification:
            payload = {
                "query": params.q,
                "columns": [
                    "ROOM_ID", "LISTING_URL", "LOCATION", "PRICE", "LISTING_DATE", "DESCRIPTION_SUMMARY",
                    "ROOM_COUNT", "BATH_COUNT", "PEOPLE_COUNT",
                    "SOURCE", "CONTACT", "LAUNDRY_AVAILABLE",
                    "REPORT_COUNT", "IMAGE_URL", "ROOM_TYPE", "OTHER_DETAILS"
                ],
                "limit": fetch_limit
            }

            search_sql = """
            SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(%s, %s)
            """
            cur.execute(search_sql, (service, json.dumps(payload)))
            row = cur.fetchone()

            if not row or row[list(row.keys())[0]] is None:
                return []

            preview_json = json.loads(row[list(row.keys())[0]])
            results = preview_json.get("results", [])

            # Filter: report_count <= 2
            filtered = []
            for item in results:
                if int(item.get("REPORT_COUNT", 0) or 0) > 2:
                    continue
                filtered.append(item)

            listings = filtered[: params.k]
            return [{"response": listings}]

        else:
            return [{"response": "Sorry, I didn't understand that. Please type your room search preferences!"}]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@router.post(
    "/user-feedback",
    response_model=Dict[str, str],
    status_code=201,
    summary="Add user feedback and increment report count"
)
async def add_user_feedback(params: FeedbackParams):
    """
    Add a row to USER_FEEDBACK if one doesn't already exist for the same user_email & room_id.
    On successful insert, increment REPORT_COUNT in ROOMS_LISTINGS for that room_id.
    """
    try:
        conn = snowflake_connection()
        cur = conn.cursor(DictCursor)

        # 1) Check if feedback already exists
        exists_sql = """
        SELECT COUNT(*) AS cnt
          FROM HOME_AI_SCHEMA.USER_FEEDBACK
         WHERE USER_EMAIL = %s
           AND ROOM_ID    = %s
        """
        cur.execute(exists_sql, (params.user_email, params.room_id))
        row = cur.fetchone()
        if row and row["CNT"] > 0:
            raise HTTPException(
                status_code=409,
                detail="Feedback already exists for this user and room."
            )

        # 2) Insert new feedback
        insert_sql = """
        INSERT INTO HOME_AI_SCHEMA.USER_FEEDBACK (USER_EMAIL, COMMENTS, ROOM_ID)
        VALUES (%s, %s, %s)
        """
        cur.execute(insert_sql, (params.user_email, params.comments, params.room_id))

        # 3) Increment report_count in ROOMS_LISTINGS
        update_sql = """
        UPDATE HOME_AI_SCHEMA.ROOMS_LISTINGS
           SET REPORT_COUNT = REPORT_COUNT + 1
         WHERE ROOM_ID = %s
        """
        cur.execute(update_sql, (params.room_id,))

        # 4) Commit and close
        conn.commit()
        cur.close()
        conn.close()

        return {"status": "success", "message": "Feedback recorded and report count updated."}

    except HTTPException:
        # pass through 409
        raise
    except Exception as e:
        # any other error
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get(
    "/get-user-feedback",
    response_model=Dict[str, List[int]],
    summary="Get list of room_ids this user has reported"
)
async def get_user_feedback(user_email: str = Query(..., description="Email of the user")):
    """
    Returns a JSON object with `reported_room_ids`, an array of integers
    for all ROOM_IDs the given user_email has reported.
    """
    try:
        conn = snowflake_connection()
        cur = conn.cursor(DictCursor)

        sql = """
        SELECT ROOM_ID
          FROM HOME_AI_SCHEMA.USER_FEEDBACK
         WHERE USER_EMAIL = %s
        """
        cur.execute(sql, (user_email,))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        # Extract the ROOM_ID values
        reported = [row["ROOM_ID"] for row in rows]
        return {"reported_room_ids": reported}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/user-preferences",
    response_model=Dict[str,str],
    status_code=201,
    summary="Upsert user property preferences"
)
async def upsert_user_preferences(params: PreferenceParams):
    """
    Update existing USER_PREFERENCE row if one exists for user_email,
    otherwise insert a new row.
    """
    try:
        conn = snowflake_connection()
        cur = conn.cursor(DictCursor)

        merge_sql = """
        MERGE INTO HOME_AI_SCHEMA.USER_PREFERENCE tgt
        USING (
          SELECT
            %s AS USER_EMAIL,
            %s AS ROOM_TYPE,
            %s AS CITY,
            %s AS LOCATION,
            %s AS AMENITIES,
            %s AS GETALERTS,
            %s AS BEDROOM,
            %s AS BATHROOM,
            %s AS MINPRICE,
            %s AS MAXPRICE
        ) src
        ON tgt.USER_EMAIL = src.USER_EMAIL
        WHEN MATCHED THEN
          UPDATE SET
            ROOM_TYPE = src.ROOM_TYPE,
            CITY      = src.CITY,
            LOCATION  = src.LOCATION,
            AMENITIES = src.AMENITIES,
            GETALERTS = src.GETALERTS,
            BEDROOM   = src.BEDROOM,
            BATHROOM  = src.BATHROOM,
            MINPRICE  = src.MINPRICE,
            MAXPRICE  = src.MAXPRICE
        WHEN NOT MATCHED THEN
          INSERT (USER_EMAIL, ROOM_TYPE, CITY, LOCATION,
                  AMENITIES, GETALERTS, BEDROOM, BATHROOM, MINPRICE, MAXPRICE)
          VALUES
                  (src.USER_EMAIL, src.ROOM_TYPE, src.CITY, src.LOCATION,
                   src.AMENITIES, src.GETALERTS, src.BEDROOM, src.BATHROOM, src.MINPRICE, src.MAXPRICE);
        """
        print("Get Alerts SQL:", params.getalerts)
        print("Get Alerts SQL:", params.amenities)
        cur.execute(
            merge_sql,
            (
                params.user_email,
                params.room_type,
                params.city,
                params.location,
                params.amenities,
                params.getalerts,
                params.bedroom,
                params.bathroom,
                params.minprice,
                params.maxprice,
            )
        )

        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success", "message": "Preferences saved."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get(
    "/user-preferences",
    response_model=Dict[str, Any],
    summary="Fetch user property preferences"
)
async def get_user_preferences(
    user_email: str = Query(..., description="Email of the user")
):
    """
    Return the row from USER_PREFERENCE for this user_email,
    or {} if no preferences are saved yet.
    """
    try:
        conn = snowflake_connection()
        cur = conn.cursor(DictCursor)

        sql = """
        SELECT
          USER_EMAIL,
          ROOM_TYPE,
          CITY,
          LOCATION,
          AMENITIES,
          GETALERTS,
          BEDROOM,
          BATHROOM,
          MINPRICE,
          MAXPRICE
        FROM HOME_AI_SCHEMA.USER_PREFERENCE
        WHERE USER_EMAIL = %s
        """
        cur.execute(sql, (user_email,))
        row = cur.fetchone()

        cur.close()
        conn.close()

        if not row:
            return {}
        # row is already a dict thanks to DictCursor
        return row

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
