import os
from dotenv import load_dotenv

load_dotenv() 

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")

    if not OPENAI_API_KEY:
        raise ValueError("No OpenAI API key set for Flask application")
    if not OPENWEATHER_API_KEY:
        raise ValueError("No OpenWeatherMap API key set for Flask application")