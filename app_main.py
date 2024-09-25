from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import logging
from user_profile_setting import init_db, get_user_profile
from language_learning_manager import LanguageLearningManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()  # Load environment variables from .env file

app = FastAPI()

# Initialize the database
init_db()

class Message(BaseModel):
    user_id: int
    message: str

@app.get("/")
async def root():
    return {"message": "Welcome to the Chatbot API. Use the /chatbot endpoint to interact with the chatbot."}

@app.post("/chatbot")
async def chatbot_endpoint(message: Message):
    try:
        chatbot = LanguageLearningManager(message.user_id)
        response = chatbot.process_message(message.message)
        logger.info(f"Chatbot response: {response}")
        return {"response": response}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.post("/set_daily_target")
async def set_daily_target(user_id: int, target: int):
    chatbot = LanguageLearningManager(user_id)
    return {"message": chatbot.set_daily_target(target)}

@app.get("/get_profile")
async def get_profile(user_id: int):
    profile = get_user_profile(user_id)
    return profile

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)