# Fampay Assignment

## Description
1. Fetches videos from youtube api every `10` seconds, based on the queries user store. This is can be configured from env. Look bottom most section.
2. Stores fetched videos in database.
3. User can `query` and `search` videos from local.
4. User can store multiple `api-key` from google to fetch videos. If one failes other is used.

## Techstack
1. `Elastic Search`: It was mentioned in assignment, that user should be able to query, based on oneor two example, I went ahead with elastic, instead of manually writting any algorithm. 
2. `Sqlite`: I chose sqlite here, since it is only going to be used to stored video data and query based on id.
3. `Redis`: This is for queue mechanism, which is used by celery. Also, we are using it for maintaining lock.
4. `Celery`: Celery is for background tasks. It schedules task to fetch videos from youtube api every `10 seconds`
5. `Fastapi`: Fastapi is python web framework, it is quicker to make microservices with it.


## Installation

1. Clone the repository: `git clone [repository URL]`
2. Navigate to the project directory: `cd [project directory]`
3. Make sure you have docker installed.
4. Copy `.env.example` and make `.env` in the root folder of the project. You can change the given values.
4. `docker compose up` or `sudo docker compose up` if asks for permission

## Usage

1. once project is up and running, you can visit `http://localhost:8000/docs`
2. You will be able to see 3 apis here:
    - `POST` /api/api-key : You can add api keys here.
    - `POST` /api/queries: You can add different search terms which will be called after on reqgular interval seconds e.g: `cricket`, `tea`, `football`
    - `GET` /api/video: Based on interval you can try to query here. It also accepts `query` param. Based on the search results it will give you the list of videos containing multiple params order by `publishedDate` in descending .

## ENV
1. `QUERY_START`: 2024-01-01T00:00:00+0530 //this should be in ISO FORMAT
2. `INTERVAL_SECONDS`: 10 // how often do you want to run query