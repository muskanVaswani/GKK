from fastapi import FastAPI
from routers import auth
from routers import game
from routers import result
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(auth.router)
app.include_router(game.router)
app.include_router(result.router)


@app.get("/")
def homepage():
    return {"welcome to GOI!"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

