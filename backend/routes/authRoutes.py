from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from passlib.context import CryptContext
from connections import snowflake_connection
import configparser
import json

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

config = configparser.ConfigParser()
config.read('./configuration.properties')

class SignupUser(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str

class LoginUser(BaseModel):
    email: str
    password: str

# 🔥 Helper Functions
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

@router.post("/signup")
async def signup(user: SignupUser):
    conn = snowflake_connection()
    cur = conn.cursor()

    try:
        # Check if email already exists
        cur.execute("SELECT COUNT(*) FROM USER_PROFILE WHERE USER_EMAIL = %s", (user.email,))
        if cur.fetchone()[0] > 0:
            raise HTTPException(status_code=400, detail="Email already registered.")

        hashed_password = get_password_hash(user.password)

        cur.execute("""
            INSERT INTO USER_PROFILE (FIRST_NAME, LAST_NAME, USER_EMAIL, USER_PASSWORD)
            VALUES (%s, %s, %s, %s)
        """, (user.first_name, user.last_name, user.email, hashed_password))

        conn.commit()
        return {"message": "Signup successful!"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

# 🔥 Login Endpoint
@router.post("/login")
async def login(user: LoginUser):
    conn = snowflake_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT FIRST_NAME, LAST_NAME, USER_EMAIL, USER_PASSWORD
            FROM USER_PROFILE
            WHERE USER_EMAIL = %s
        """, (user.email,))
        result = cur.fetchone()

        if not result:
            raise HTTPException(status_code=400, detail="Invalid email or password.")

        first_name, last_name, user_email, user_password = result

        if not verify_password(user.password, user_password):
            raise HTTPException(status_code=400, detail="Invalid email or password.")

        return {
            "first_name": first_name,
            "last_name": last_name,
            "email": user_email
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()
