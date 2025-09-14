from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from models.models import User,Riddle
import random
from pydantic import BaseModel
from typing import List


router = APIRouter(prefix="/auth", tags=["auth"])
user_riddles = {}

#pydantic schemas
class User_details(BaseModel):
    user_name: str
    
class Login_details(BaseModel):
    user_name:str
    user_id:int

class UserResponse(BaseModel):
    username: str
    id:int

    class Config:
        from_attributes = True
        
class ScreeningAnswers(BaseModel):
    user_id: int
    answer: List[str]


@router.post("/registration", response_model=UserResponse)
def user_registration(user: User_details, db: Session = Depends(get_db)):
    new_user = User(username=user.user_name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return{"message": "you are registered!",
           "username": new_user.username,
           "id": new_user.id
    }
           

@router.post("/login")
def user_login(payload: Login_details, db:Session = Depends(get_db)):
    
    #find by id
    db_user = db.query(User).filter(User.id == payload.user_id).first()
    
    if not db_user:
        raise HTTPException(status_code=404, details="User ID not found.")
    
    if db_user.username.lower().strip() != payload.user_name.lower().strip():
        raise HTTPException(status_code=400, details="User ID and name do not match.")
    
    return{"message": f"Welcome to the game, {db_user.username}!"}
    
@router.get("/users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.delete("/delete/{user_id}")
def delete_user(user_id:int, db:Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    db.delete(db_user)
    db.commit()
    return {"message": f"User with ID {user_id} has been deleted."}

   
@router.get("/riddles/{user_id}")
def get_riddles(user_id:int, db: Session = Depends(get_db)):
    riddles = db.query(Riddle).all()
    if not riddles:
        raise HTTPException(status_code=404, details="No riddles in DB!")
    
    selected = random.sample(riddles, min(3, len(riddles)))
    user_riddles[user_id] = selected
    
    return{
        "user_id": user_id,
        "riddles": [{"id": r.id, "question": r.question} for r in selected]
    }
   
    

@router.post("/check_riddles")
def check_riddles(payload: ScreeningAnswers):
    riddles = user_riddles.get(payload.user_id)
    
    if not riddles:
        raise HTTPException(status_code=400, detail="No riddles found for this user.")
    
    score = 0
    for user_ans, riddle in zip(payload.answer, riddles):
        if user_ans.lower().strip() == riddle.answer.lower().strip():
            score += 1
    
    if score == len(riddles):
        return {"Congratulations! you Passed! Welcome to the original game."}
    return {f"""Sorry, you failed the screening round. Better luck next time!
            Your Score: {score}/{len(riddles)}"""}
                
    

    
     
    