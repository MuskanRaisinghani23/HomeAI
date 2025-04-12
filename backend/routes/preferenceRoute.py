from connections import snowflake_connection
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

# Initialize the APIRouter
router = APIRouter()

# Model
class UserPreferenceUpdateRequest(BaseModel):
    user_email: str
    budget: Optional[int] = None
    room_type: Optional[str] = None
    region: Optional[str] = None
    people_count: Optional[int] = None

# Controller
@router.post("/update-preference")
async def update_preference(request: UserPreferenceUpdateRequest):
    """
    API route to update the user preference in Snowflake.

    Args:
        request (preferenceUpdateRequest): The request body containing User preference details.

    Returns:
        dict: A response indicating success or failure.
    """
    try:
        if request.user_email is None:
            raise HTTPException(status_code=400, detail="User email is required.")
        
        # Call the preference function
        response = update_user_preference(request)

        if response["status"] == "success":
            return {"status": "success", "message": response["message"]}
        else:
            raise HTTPException(status_code=400, detail=response["message"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get-preference/{user_email}")
async def get_preference(user_email: str):
    """
    API route to fetch the user preference from Snowflake.

    Args:
        user_email (str): The ID of the user whose preference is to be fetched.

    Returns:
        dict: A response containing the user preference data or an error message.
    """
    try:
        # Call the get preference function
        preference_data = get_user_preference(user_email)

        if preference_data:
            return {"status": "success", "data": preference_data}
        else:
            raise HTTPException(status_code=404, detail="preference not found.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# CRUD Function
def update_user_preference(request):
    try:
        conn = snowflake_connection()
        cursor = conn.cursor()

        update_fields = []
        update_values = []

        if hasattr(request, "budget"):
            update_fields.append("budget = %s")
            update_values.append(request.budget)
        if hasattr(request, "room_type"):
            update_fields.append("room_type = %s")
            update_values.append(request.room_type)
        if hasattr(request, "region"):
            update_fields.append("region = %s")
            update_values.append(request.region)
        if hasattr(request, "people_count"):
            update_fields.append("people_count = %s")
            update_values.append(request.people_count)

        if not update_fields:
            return {"status": "error", "message": "No fields provided for update."}

        # Construct the final SQL query
        update_query = f"""
        UPDATE USER_PREFERENCE
        SET {', '.join(update_fields)}
        WHERE user_email = %s
        """

        update_values.append(request.user_email)

        cursor.execute(update_query, tuple(update_values))
        conn.commit()

        cursor.close()
        conn.close()

        return {"status": "success", "message": "User preference updated successfully."}

    except Exception as e:
        return {"status": "error", "message": f"Error updating user preference: {str(e)}"}


def get_user_preference(user_email):
    """
    Fetches the user preference from the Snowflake table.

    Args:
        user_email (str): The ID of the user whose preference is to be fetched.

    Returns:
        dict: A dictionary containing the user preference data.
    """
    try:
        # Connect to Snowflake
        conn = snowflake_connection()
        cursor = conn.cursor()

        # Query to fetch the preference
        query = """
        SELECT budget, room_type, region, people_count
        FROM USER_PREFERENCE
        WHERE user_email = %s
        """
        cursor.execute(query, (user_email,))
        result = cursor.fetchone()

        # Close the connection
        cursor.close()
        conn.close()

        if result:
            return {
                "budget": result[0],
                "room_type": result[1],
                "region": result[2],
                "people_count": result[3]
            }
        else:
            return None

    except Exception as e:
        raise Exception(f"Error fetching preference: {str(e)}")