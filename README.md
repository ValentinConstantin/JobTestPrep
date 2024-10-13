Weather API Service

This repository contains a FastAPI-based weather API service that allows users to retrieve current weather data for a given city. The service fetches data from an external weather API and stores the results in AWS S3 and AWS DynamoDB. It also implements caching using S3 to reduce the number of API calls.

Features

	1.	FastAPI Setup:
	•	The service exposes a single endpoint: /weather.
	•	The endpoint accepts a GET request with a city query parameter.
	2.	Asynchronous Data Fetching:
	•	The service fetches weather data asynchronously from an external API using Python’s asyncio.
	•	It handles errors such as invalid city names or failures from the external API gracefully.
	3.	AWS S3 Integration:
	•	The fetched weather data is stored as a JSON file in an S3 bucket.
	•	The filename format is {city}_{timestamp}.json, where timestamp is the UTC time of the data retrieval.
	•	Asynchronous methods are used to interact with S3.
	4.	AWS DynamoDB Integration:
	•	After the weather data is saved in S3, an event is logged in a DynamoDB table.
	•	The log includes the city name, timestamp, and S3 URL of the JSON file.
	•	All interactions with DynamoDB are performed asynchronously.
	5.	Caching with S3:
	•	Before fetching weather data from the external API, the service checks if the data for the requested city has been cached in the S3 bucket within the last 5 minutes.
	•	If a cached file exists, the service retrieves the data from S3 directly without calling the external API.
	•	The cache expires after 5 minutes, and new data is fetched when the cache is stale.
	6.	Deployment:
	•	This service is containerized with Docker and can be deployed easily using Docker Compose.

Requirements

	•	Python 3.9+
	•	AWS S3 and DynamoDB
	•	Docker and Docker Compose (for deployment)

Python Libraries

The following Python libraries are required:

	•	fastapi
	•	aiohttp
	•	aioboto3
	•	uvicorn

You can install all dependencies by running:

pip install -r requirements.txt

Environment Variables

Set up the following environment variables to configure the application:

	•	WEATHER_KEY: Add your weather API key here.
	•	S3_BUCKET_NAME: Add your AWS S3 bucket name here.
	•	AWS_ACCESS_KEY_ID: Add your AWS access key here.
	•	AWS_SECRET_ACCESS_KEY: Add your AWS secret key here.
	•	AWS_REGION: Add your AWS region (e.g., us-west-2).
	•	DYNAMODB_TABLE_NAME: Add your AWS DynamoDB table name here.
	•	CACHE_EXPIRY_TIME: Cache expiry time in seconds (default is 3600 for 1 hour).

API Usage

Endpoint

GET /weather?city=<city_name>

	•	city: The name of the city to retrieve weather data for.

Example Request

GET /weather?city=London

Example Response


```json
{
  "coord": {
    "lon": 26.1063,
    "lat": 44.4323
  },
  "weather": [
    {
      "id": 800,
      "main": "Clear",
      "description": "clear sky",
      "icon": "01n"
    }
  ],
  "base": "stations",
  "main": {
    "temp": 289.86,
    "feels_like": 289.36,
    "temp_min": 287.09,
    "temp_max": 290.85,
    "pressure": 1016,
    "humidity": 68,
    "sea_level": 1016,
    "grnd_level": 1006
  },
  "visibility": 10000,
  "wind": {
    "speed": 1.54,
    "deg": 290
  },
  "clouds": {
    "all": 0
  },
  "dt": 1728837880,
  "sys": {
    "type": 2,
    "id": 2037828,
    "country": "RO",
    "sunrise": 1728793689,
    "sunset": 1728833702
  },
  "timezone": 10800,
  "id": 683506,
  "name": "Bucharest",
  "cod": 200
}

```

Deployment

Docker

To deploy the service using Docker, follow these steps:

	1.	Build the Docker image: docker build weather-api




	2.	Run the Docker container: docker up weather-api


Docker Compose

A docker-compose.yml file is provided for easy deployment. To deploy using Docker Compose, run:

docker-compose up --build

This will build the Docker image and run the container with all necessary services.

How It Works

Weather Data Fetching

	•	When a user requests weather data for a specific city, the service checks if there is a cached response in S3 from the last 5 minutes.
	•	If cached data is found, it is returned immediately.
	•	If no cache is found or the cache has expired, the service fetches fresh data from the external weather API.

S3 and DynamoDB Integration

	•	The weather data is stored in an S3 bucket as a JSON file with the format {city}_{timestamp}.json.
	•	The event is then logged into a DynamoDB table, recording the city name, timestamp, and the S3 URL of the stored file.

Caching

	•	Cached data in S3 is checked for each request. If the data is older than 5 minutes, a new request is made to the external API, and the cache is updated with the new data.

License

This project is licensed under the MIT License. See the LICENSE file for details.

Contributing

Contributions are welcome! Please open an issue or submit a pull request with any improvements, bug fixes, or feature requests.
