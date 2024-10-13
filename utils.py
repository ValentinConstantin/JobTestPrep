import aioboto3
import json
from fastapi import HTTPException
from datetime import datetime, timedelta


# Asynchronously upload weather data to S3
async def upload_weather_data_to_s3(city: str, weather_data: dict, s3_bucket_name: str):
    # Get the current timestamp
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')

    # Create filename based on city and timestamp
    file_name = f"{city}_{timestamp}.json"

    # Convert weather data to JSON
    weather_json = json.dumps(weather_data)

    # Initialize aioboto3 session and upload file
    session = aioboto3.Session()
    async with session.client('s3') as s3:
        try:
            await s3.put_object(
                Bucket=s3_bucket_name,  # S3 bucket name
                Key=file_name,  # S3 file key (name)
                Body=weather_json,  # The file content
                ContentType="application/json"
            )
            s3_file_url = f"https://{s3_bucket_name}.s3.amazonaws.com/{file_name}"
            return s3_file_url
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload to S3: {str(e)}")


# Asynchronously log event to DynamoDB
async def log_event_to_dynamodb(city: str, s3_url: str, dynamodb_table_name: str, aws_region: str):
    timestamp = datetime.utcnow().isoformat()

    # Initialize aioboto3 session with the region
    session = aioboto3.Session()
    async with session.resource('dynamodb', region_name=aws_region) as dynamodb:
        table = await dynamodb.Table(dynamodb_table_name)
        print(table)
        try:
            await table.put_item(
                Item={
                    'city': city,
                    'timestamp': timestamp,
                    's3_url': s3_url
                }
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to log event to DynamoDB: {str(e)}")


async def download_weather_data_from_s3(city: str, s3_bucket_name: str, cache_expiry_time: int):
    session = aioboto3.Session()
    file_prefix = f"{city}_"

    async with session.client('s3') as s3:
        try:
            response = await s3.list_objects_v2(Bucket=s3_bucket_name, Prefix=file_prefix)
            if "Contents" not in response:
                return None

            latest_object = sorted(response['Contents'], key=lambda obj: obj['Key'], reverse=True)[0]
            file_name = latest_object['Key']
            file_response = await s3.get_object(Bucket=s3_bucket_name, Key=file_name)
            file_content = await file_response['Body'].read()
            weather_data = json.loads(file_content)

            timestamp_str = file_name.split('_')[-1].replace('.json', '')
            file_timestamp = datetime.strptime(timestamp_str, '%Y%m%d%H%M%S')

            if datetime.utcnow() - file_timestamp > timedelta(seconds=cache_expiry_time):
                print(f"Cached data for {city} has expired.")
                return None

            print(f"Using cached weather data for {city}.")
            return weather_data

        except s3.exceptions.NoSuchKey:
            return None
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to download from S3: {str(e)}")
