from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


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