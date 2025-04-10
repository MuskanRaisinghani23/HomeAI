from fastapi import APIRouter, HTTPException
from connections import snowflake_connection

router = APIRouter()

@router.get("/get-listings")
async def get_listings():
    """
    API route to fetch all listings from the database.

    Returns:
        dict: A response containing the listings data or an error message.
    """
    try:
        # Connect to Snowflake
        conn = snowflake_connection()
        cursor = conn.cursor()

        # Query to fetch listings
        query = """
        SELECT listing_url, price, location, description_summary
        FROM ROOMS_LISTINGS LIMIT 10
        """
        cursor.execute(query)
        results = cursor.fetchall()

        # Close the connection
        cursor.close()
        conn.close()

        # Map results to a list of dictionaries
        listings = [
            {
                "listing_url": row[0],
                "price": row[1],
                "location": row[2],
                "description_summary": row[3]
            }
            for row in results
        ]

        return {"status": "success", "data": listings}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching listings: {str(e)}")