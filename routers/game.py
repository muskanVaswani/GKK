from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from models.models import Question, Result
import random
from pydantic import BaseModel


router = APIRouter(prefix="/game", tags=["game"])

user_game = {}
user_results = {}

class Answer(BaseModel):
    user_id: int
    answer: str
    
class FieldSelection(BaseModel):
    user_id: int
    field: str


#stage wise questions
def get_questions_stagewise(stage:int,field:str, db: Session):
    questions = db.query(Question).filter(
        Question.stage == stage,
        Question.field == field
    ).all()
    if not questions:
        raise HTTPException(status_code=404, detail="No questions found for this stage and field.")
    
    return random.sample(questions, min(5,len(questions)))
    

#start game logic
@router.post("/start")
def start_game(payload: FieldSelection, db: Session = Depends(get_db)):
        field = payload.field.lower()
        selected = get_questions_stagewise(1,field, db)
    
        user_game[payload.user_id] ={
            "stage":1,
            "questions" : selected,
            "current_question_index":0,
            "score":0,
            "field":field
            }
        first_q = selected[0]
        labels = ["A", "B", "C", "D"]
        options_with_labels = {"A": first_q.option_a, "B": first_q.option_b, "C": first_q.option_c, "D": first_q.option_d}
   

        return {"stage":1, "question":first_q.question, "options": options_with_labels }

@router.post("/answer")
def checking_answers(payload: Answer, db:Session = Depends(get_db)):
    game = user_game.get(payload.user_id)
    
    if not game:
        raise HTTPException(status_code=400, detail = "No active game found.")
    
    current_q = game["questions"][game["current_question_index"]]
    correct_answer = current_q.correct_option.upper()
   
    
    #Normalize answers for comparison
    user_input = payload.answer.strip().upper()
    labels = ["A","B","C","D"]
    if user_input not in ["A","B","C","D"]:
        return {"message": "Please answer with A, B, C, or D"}
    
    
    if user_input == correct_answer:
        game["current_question_index"] +=1
        
        #Stage complete
        if game["current_question_index"] >= len(game["questions"]):
            stage = game["stage"] + 1

            if stage > 4:
                # save result in DB
                new_result = Result(
                    user_id=payload.user_id,
                    field=game["field"],
                    score=game["current_question_index"] * 10,  # or however you score
                    stage=game["stage"]
                )
                db.add(new_result)
                db.commit()
                db.refresh(new_result)
                return{"Message": "congratulations! you have Completed all stages of the game!",}
               
            #fetch new stage questions
            game["stage"] = stage
            game["current_question_index"] = 0
            game["questions"] = get_questions_stagewise(stage, game["field"], db)
            
            next_q = game["questions"][0]
            return{
                "message": f"Stage {stage-1} cleared! Welcome to Stage {stage}.",
                "question": next_q.question,
                "options": {
                    "A": next_q.option_a,
                    "B": next_q.option_b,
                    "C": next_q.option_c,
                    "D": next_q.option_d,
                }
            }
        
        #next question
        next_q = game["questions"][game["current_question_index"]]
        return{
            "message": "correct answer",
            "stage": game["stage"],
            "question": next_q.question,
            "options": {
                "A": next_q.option_a,
                "B": next_q.option_b,
                "C": next_q.option_c,
                "D": next_q.option_d
        }
        }
        
    else:
        # #store results 
        # user_results[payload.user_id]={
        #     "field": game.get("field", "Not slected"),
        #     "score": game["current_question_index"] * 10,
        #     "stage": game["stage"]
        # }
        # save result in DB
        new_result = Result(
            user_id=payload.user_id,
            field=game["field"],
            score=game["current_question_index"] * 10,  # or however you score
            stage=game["stage"]
        )
        db.add(new_result)
        db.commit()
        db.refresh(new_result)
        user_game.pop(payload.user_id,None)
        return{"message": f"Wrong! Game Over. Correct answer was {correct_answer}",
               "play_again": True}


    
@router.post("/restart/{user_id}")
def restart_game(user_id:int, db:Session = Depends(get_db)):
    user_game.pop(user_id, None)
    return start_game(user_id)


#game home page
@router.get("/{user_id}")
def game_homepage(user_id:int):
    fields = ["developer", "marketing", "finance", "general", ] 
    user_game.pop(user_id,None)
    return {"fields":fields, "user_id":user_id}
    
    
    

