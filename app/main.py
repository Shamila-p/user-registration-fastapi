import bcrypt
from fastapi import UploadFile
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from app.database import pg_conn, mongo_collection

app = FastAPI()

class User(BaseModel):
    first_name: str
    password: str
    email: str
    phone: str
    profile_picture: UploadFile


@app.post("/register/")
async def register_user(
    first_name: str,
    password: str,
    email: str,
    phone: str,
    profile_picture: UploadFile
):
    # Check if the email and phone already exist 
    pg_cursor = pg_conn.cursor()
    pg_cursor.execute("SELECT user_id FROM Users WHERE email = %s OR phone = %s", (email, phone))
    existing_user = pg_cursor.fetchone()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email or phone already exists")
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Insert user data into table
    pg_cursor.execute(
        "INSERT INTO Users (first_name, password, email, phone) VALUES (%s, %s, %s, %s) RETURNING user_id",
        (first_name,hashed_password.decode('utf-8'),email, phone),
    )
    user_id = pg_cursor.fetchone()[0]

    image_path = f"images/{user_id}_{profile_picture.filename}"
    with open(image_path, "wb") as image_file:
        image_file.write(profile_picture.file.read())

    profile_data = {
        "user_id": user_id,
        "profile_picture": image_path
    }
    mongo_collection.insert_one(profile_data)
    pg_conn.commit()
    pg_cursor.close()
    return {"user_id": user_id,"message":"User registered successfully"}


@app.get("/user/{user_id}/")
async def get_user_details(user_id: int):
    # Fetch user details from PostgreSQL
    pg_cursor = pg_conn.cursor()
    pg_cursor.execute("SELECT first_name, email, phone FROM users WHERE user_id = %s", (user_id,))
    user_data = pg_cursor.fetchone()
    pg_cursor.close()

    if user_data is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Fetch user's profile picture from MongoDB
    profile_data = mongo_collection.find_one({"user_id": user_id})

    return {
        "user_id": user_id,
        "first_name": user_data[0],
        "email": user_data[1],
        "phone": user_data[2],
        "profile_picture": profile_data["profile_picture"]
    }