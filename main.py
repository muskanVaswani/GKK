from fastapi import FastAPI
from routers import auth
from routers import game
from routers import result

app = FastAPI()

app.include_router(auth.router)
app.include_router(game.router)
app.include_router(result.router)


@app.get("/")
def homepage():
    return {"welcome to GKK!"}

