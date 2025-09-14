from db import Base, engine
from models.models import User, Question, Result, GameState

print("creating")
Base.metadata.create_all(bind=engine)
print("created")