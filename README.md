# PokeParty Backend

### Project Description
PokeParty allows users to:

- Browse a list of Pokémon.  
- Add Pokémon to their favorites.  
- Vote for Pokémon to indicate which one they like more.  
- See rankings based on votes.  

This makes PokeParty an interactive Pokémon platform combining collection, preference voting, and rankings in a fun UI.

## Overview
**PokeParty** is a full-stack Pokémon-themed application consisting of:

- **Backend**: FastAPI + Uvicorn providing API endpoints.  
- **Frontend**: React application for interacting with the backend.  

You can find the frontend repository here: [PokeParty Frontend](https://github.com/ressca/pokeparty-frontend)

This README covers the backend setup, running, and deployment instructions.

---

## Requirements
- Python 3.9+
- pip
- FastAPI & Uvicorn (installed via `requirements.txt`)
- (Optional) Docker & Docker Compose

---

## Installation (Local)

### 1. Clone the repository
```bash
git clone https://github.com/ressca/pokeparty-backend.git
cd pokeparty-backend
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy .env.example to .env and fill required values (database URL, secrets, etc.):
```bash
cp env.example .env
```

## Running the API with Uvicorn

### Development (auto-reload)
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Documentation
```markdown
Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc
```

## Running with Docker

### Build image
```bash
docker build -t pokeparty-backend .
```

### Run container
```bash
docker run --env-file .env -p 8000:8000 pokeparty-backend pokeparty-backend
```

## Running Tests
```bash
pytest
```
