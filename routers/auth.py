from fastapi import APIRouter
from random import randrange
from pathlib import Path 
from typing import List
import json
import random
from pydantic import BaseModel

#temp storage for riddles
user_riddles={}
router = APIRouter(prefix="/auth", tags=["auth"])

#loading riddles for screening round
def loading_riddles():
    riddles_file = Path(__file__).parent.parent / "data" / "riddles.json"
    with open(riddles_file, "r") as file:
        return json.load(file)
    
class User_details(BaseModel):
    user_name: str
    
class Login_details(BaseModel):
    user_name:str
    user_id:int

class screening_answers(BaseModel):
    user_id:int
    answer : List[str]
    
    

registered_users = [{"user_name": "muskan" , "user_id": 123}]

@router.post("/registration")
def user_registration(user_details: User_details):
    user_id = randrange(1,100000)
    registered_users.append({"user_name" : user_details.user_name, "user_id" : user_id})
    return{f"{user_details.user_name} your are successfully registered, and here's your user id: {user_id}"}

@router.get("/registered_users")
def get_user():
    return registered_users

@router.post("/login")
def user_login(login : Login_details):
    for user in registered_users:
        if user["user_name"] == login.user_name and int(user["user_id"]) == int(login.user_id):
            return {f"Welcome back to the game {login.user_name}!"}
   
@router.get("/riddles/{user_id}")
def get_riddles(user_id:int):
    riddles = random.sample(loading_riddles(),3)
    user_riddles[user_id] = riddles
    return {"riddles": [r["question"] for r in riddles]}
    

@router.post("/check")
def check_riddles(payload: screening_answers):
    riddles = user_riddles.get(payload.user_id)
    
    if not riddles:
        return {"No riddles found for this user. Please start again."}
    
    score = 0
    for user_ans, riddle in zip(payload.answer, riddles):
        if user_ans.lower().strip() == riddle["answer"].lower().strip():
            score += 1
    
    if score == 3:
        return {"Congratulations! you Passed! Welcome to the original game."}
    return {f"""Sorry, you failed the screening round. Better luck next time!
            Your Score: {score}/3"""}
                
    

    
     
    