import os
import aiohttp
from fastapi import FastAPI, HTTPException, Query
from utils import upload_weather_data_to_s3, log_event_to_dynamodb, download_weather_data_from_s3

app = FastAPI()


WEATHER_API_KEY = os.getenv("WEATHER_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME")
AWS_REGION = os.getenv("AWS_REGION")
CACHE_EXPIRY_TIME = os.getenv("CACHE_EXPIRY_TIME")


if not all([WEATHER_API_KEY, S3_BUCKET_NAME, DYNAMODB_TABLE_NAME, AWS_REGION]):
    raise RuntimeError("One or more environment variables are missing. Please set them before starting the app.")

@app.get("/weather")
async def fetch_weather_data(city: str = Query(..., description="City name to fetch weather data for")):
    # Fetch API key from environment variables

    if not WEATHER_API_KEY:
        raise HTTPException(status_code=500, detail="API key not found")

    # If cache exists and not expired, return cached data
    cached_data = await download_weather_data_from_s3(city, S3_BUCKET_NAME, int(CACHE_EXPIRY_TIME))

    if cached_data:
        return cached_data

    # Construct the URL for the OpenWeatherMap API
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                weather_data = await response.json()
                # Store fetched weather data in S3
                s3_file_url = await upload_weather_data_to_s3(city, weather_data, S3_BUCKET_NAME)
                # Log the event in DynamoDB
                await log_event_to_dynamodb(city, s3_file_url, DYNAMODB_TABLE_NAME, AWS_REGION)
                return weather_data
            else:
                raise HTTPException(status_code=response.status, detail="City not found or API error")





