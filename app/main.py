from fastapi import FastAPI, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import auth
from .database import get_db, engine
from .services import get_or_create_pokemon_of_the_day
from . import models


models.Base.metadata.create_all(bind=engine)

app = FastAPI(root_path="/api")
app.include_router(auth.router)

    
# CORS middleware
app.add_middleware( 
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://pokeparty.ressca.dev"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ROUTES
@app.get("/")
def hello_world():
    return {"Hello, Worlddddddddddddddd!"}


# pokemon of the day route
@app.get("/pokemon-otd", status_code=status.HTTP_200_OK)
def get_pokemon_of_the_day(db: Session = Depends(get_db)):
    potd = get_or_create_pokemon_of_the_day(db)
    
    return {"pokemon_of_the_day": {"day_date": potd.day_date, "pokemon_id": potd.pokemon_id}}