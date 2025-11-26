# PokeParty Backend

## Overview

PokeParty Backend is a FastAPI-based application providing API endpoints
for the PokeParty project. It runs on Uvicorn and supports
environment-based configuration and Docker deployment.

## Requirements

-   Python 3.9+
-   pip
-   FastAPI & Uvicorn (installed via requirements.txt)
-   (optional) Docker

## Installation (Local)

### 1. Clone the repository

``` bash
git clone https://github.com/ressca/pokeparty-backend.git
cd pokeparty-backend
```

### 2. Create a virtual environment (recommended)

``` bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate    # Windows
```

### 3. Install dependencies

``` bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example file:

``` bash
cp env.example .env
```

Fill required values inside `.env`.

## Running the API with Uvicorn

### Development (auto-reload)

``` bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production

``` bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### API Documentation

-   Swagger UI: http://localhost:8000/docs\
-   ReDoc: http://localhost:8000/redoc

## Running with Docker

### Build image

``` bash
docker build -t pokeparty-backend .
```

### Run container

``` bash
docker run --env-file .env -p 8000:8000 pokeparty-backend
```

## Running Tests

``` bash
pytest
```

## Notes

-   Ensure `.env` is properly configured.
-   Uvicorn is the recommended server for development and production.
-   API docs are auto-generated and available after startup.
