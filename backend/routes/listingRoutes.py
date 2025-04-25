from snowflake.connector import DictCursor
from snowflake.snowpark import Session
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict
from pydantic import BaseModel
from connections import snowflake_connection, load_snowflake_config
import json
from typing import Optional

router = APIRouter()

config = load_snowflake_config()

session = Session.builder.configs(config).create()

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

        # Base query with report_count filter
        query = """
        SELECT 
            id, location, listing_url, listing_date, price, description_summary,
            image_url, source, other_details,
            room_count, bath_count, people_count, contact,
            report_count, room_type, laundry_available
        FROM ROOMS_LISTINGS_NEW
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
                "ID": row[0],
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

class SearchParams(BaseModel):
    q: str
    k: int = 10

@router.post("/search-listings", response_model=List[Dict])
async def search_listings(params: SearchParams):
    service = "HOME_AI_SCHEMA.MY_LISTINGS_SEARCH"
    fetch_limit = max(params.k * 3, 20)

    query = params.q + "Strictly follow my question to get the response by checking all the details in the listing." 

    payload = {
        "query":   query,
        "columns": [
            "ID", "LISTING_URL","LOCATION","PRICE","LISTING_DATE", "DESCRIPTION_SUMMARY", 
            "ROOM_COUNT","BATH_COUNT","PEOPLE_COUNT",
            "SOURCE","CONTACT","LAUNDRY_AVAILABLE",
            "REPORT_COUNT","IMAGE_URL","ROOM_TYPE","OTHER_DETAILS"
        ],
        "limit": fetch_limit
    }

    sql = """
    SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(%s, %s)
    """
    try:
        conn = snowflake_connection()
        cur = conn.cursor(DictCursor)
        cur.execute(sql, (service, json.dumps(payload)))
        row = cur.fetchone()
        if not row or row[list(row.keys())[0]] is None:
            return []

        preview_json = json.loads(row[list(row.keys())[0]])
        # 3) Extract the "results" array
        results = preview_json.get("results", [])

        filtered = []
        for item in results:
            # report_count must be ≤ 3
            if int(item.get("REPORT_COUNT", 0) or 0) > 2:
                continue
            filtered.append(item)
        
        cur.close()
        conn.close()

        listings = filtered[: params.k]
        return listings

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    