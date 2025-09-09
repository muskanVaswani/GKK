from fastapi import APIRouter
import random
from random import sample
from pathlib import Path
from pydantic import BaseModel
import json

router = APIRouter(prefix="/game", tags=["game"])

user_game = {}
user_results = {}

class Answer(BaseModel):
    user_id: int
    answer: str
    
class FieldSelection(BaseModel):
    user_id: int
    field: str

#load questions from json file
def loading_questions(field:str):
    questions_file = Path(__file__).parent.parent / "data"/f"{field}_questions.json"
    with open(questions_file, "r", encoding="utf8") as file:
        return json.load(file)

#stage wise questions
def get_questions_stagewise(stage:int,field:str):
    all_questions = loading_questions(field)
    stage_questions = [q for q in all_questions if q["stage"] == stage]
    selected = random.sample(stage_questions, min(5, len(stage_questions)))
    return selected

#start game logic
@router.post("/start/{user_id}")
def start_game(payload: FieldSelection):
    field = payload.field.lower()
    
    selected = get_questions_stagewise(1,field)
    
    user_game[payload.user_id] ={
        "stage":1,
        "questions" : selected,
        "current_question_index":0,
        "score":0,
        "field":field
    }
    
    labels = ["A", "B", "C", "D"]
    options_with_labels = {label: opt for label, opt in zip(labels, selected[0]["options"])}
   

    return {"stage":1, "question":selected[0]["question"],"options": options_with_labels }

@router.post("/answer")
def checking_answers(payload: Answer):
    game = user_game.get(payload.user_id)
    
    if not game:
        return{"message": "no active game found. start from beginning"}
    
    current_q = game["questions"][game["current_question_index"]]
    correct_answer = current_q["answer"]
    options = current_q["options"]
    
    #Normalize answers for comparison
    user_input = payload.answer.strip().upper()
    labels = ["A","B","C","D"]
    
    
    if user_input in labels:
        idx = labels.index(user_input)
        if idx < len(options):
            user_answer = options[idx]
        else:
            return{"message": "invalid option"}
    else:
        user_answer = payload.answer.strip()
        
        
    if user_answer.strip().lower() == correct_answer.strip().lower():
        game["current_question_index"] +=1
        
        #Stage complete
        if game["current_question_index"] >= len(game["questions"]):
            stage = game["stage"] + 1

            if stage > 4:
                user_results[payload.user_id] = {
                    "field": game.get("field", "Not selected"),
                    "score": game["current_question_index" ] * 10,
                    "stage": game["stage"]
                    
                    
                }
                user_game.pop(payload.user_id, None)
                return{"message":"congratulations! you have Completed all stages of the game!",
                       "play_again": True
                       }
            
            game["stage"] = stage
            game["current_question_index"] = 0
            game["questions"] = get_questions_stagewise(stage)
            
            next_q = game["questions"][0]
            labels = ["A","B", "C", "D"]
            options_with_labels = {label: opt for label, opt in zip(labels, next_q["options"])}
            
            return{
                "message": f"You cleared stage {stage -1} welcome to stage {stage}",
                'question': next_q["question"],
                "options": options_with_labels
            }
        
        #next question
        next_q = game["questions"][game["current_question_index"]]
        labels = ["A","B","C","D"]
        options_with_labels = {label:opt for label, opt in zip(labels, next_q["options"])}
        

        return{
            "message": "correct answer",
            "stage": game["stage"],
            "question": next_q["question"],
            "options": options_with_labels
        }
        
    else:
        #store results 
        user_results[payload.user_id]={
            "field": game.get("field", "Not slected"),
            "score": game["current_question_index"] * 10,
            "stage": game["stage"]
        }
        user_game.pop(payload.user_id,None)
        return{"message": f"Wrong! Game Over. Correct answer was {correct_answer}",
               "play_again": True}


    
@router.post("/restart/{user_id}")
def restart_game(user_id:int):
    user_game.pop(user_id, None)
    return start_game(user_id)


#game home page
@router.get("/{user_id}")
def game_homepage(user_id:int):
    fields = ["developer", "marketing", "finance", "general", ] 
    user_game.pop(user_id,None)
    return {"fields":fields, "user_id":user_id}
    
    
    

