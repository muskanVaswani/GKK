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
def checking_answers(payload: Answer, db: Session = Depends(get_db)):
    game = user_game.get(payload.user_id)

    if not game:
        raise HTTPException(status_code=400, detail="No active game found. Start again from /home")

    # Current question
    current_q = game["questions"][game["current_question_index"]]

    # --- Fetch correct answer safely ---
    correct_label = current_q.correct_option.upper()   # e.g. "C"
    correct_answer = getattr(current_q, f"option_{correct_label.lower()}")  # e.g. "Paris"

    # --- Normalize user input ---
    user_input = payload.answer.strip().upper()
    labels = ["A", "B", "C", "D"]
    options = [current_q.option_a, current_q.option_b, current_q.option_c, current_q.option_d]

    if user_input in labels:  # user answered with letter
        idx = labels.index(user_input)
        if idx < len(options):
            user_answer = options[idx]
        else:
            return {"message": "Invalid option"}
    else:  # user typed full text
        user_answer = payload.answer.strip()

    # --- Check correctness ---
    if user_answer.lower() == correct_answer.lower():
        game["current_question_index"] += 1

        # ✅ Update score (cumulative across stages)
        game["score"] = (game["stage"] - 1) * 5 + game["current_question_index"]

        # Stage complete
        if game["current_question_index"] >= len(game["questions"]):
            stage = game["stage"] + 1

            if stage > 4:  # All stages done
                final_score = game["score"]
                new_result = Result(
                    user_id=payload.user_id,
                    field=game["field"],
                    score=final_score,
                    stage=game["stage"]
                )
                db.add(new_result)
                db.commit()
                user_game.pop(payload.user_id, None)
                return {
                    "message": "🎉 Congratulations! You have completed all stages!",
                    "final_score": final_score,
                    "play_again": True
                }

            # Load next stage
            game["stage"] = stage
            game["current_question_index"] = 0
            game["questions"] = get_questions_stagewise(stage, game["field"], db)

            next_q = game["questions"][0]
            options_with_labels = {
                label: getattr(next_q, f"option_{label.lower()}")
                for label in labels
            }

            return {
                "message": f"✅ Stage {stage-1} cleared! Welcome to Stage {stage}.",
                "stage": stage,
                "question": next_q.question,
                "options": options_with_labels,
                "play_again": False
                
            }

        # ✅ Next question in same stage
        next_q = game["questions"][game["current_question_index"]]
        options_with_labels = {
            label: getattr(next_q, f"option_{label.lower()}")
            for label in labels
        }

        return {
            "message": "✅ Correct!",
            "stage": game["stage"],
            "score": game["score"],
            "question": next_q.question,
            "options": options_with_labels,
            "play_again": False
        }

    # ❌ Wrong answer → Game over
    else:
        final_score = game["score"]
        new_result = Result(
            user_id=payload.user_id,
            field=game["field"],
            score=final_score,
            stage_reached=game["stage"]
        )
        db.add(new_result)
        db.commit()

        user_game.pop(payload.user_id, None)
        return {
            "message": f"❌ Wrong! Game Over. Correct answer was: {correct_answer}",
            "final_score": final_score,
            "play_again": True
        }


    
@router.post("/restart/{user_id}")

def restart_game(user_id: int, db: Session = Depends(get_db)):
    user_game.pop(user_id, None)
    # Fetch last completed game for this user
    last_result = db.query(Result).filter(Result.user_id == user_id).order_by(Result.id.desc()).first()
    if not last_result:
        return {"message": "No previous game found for this user."}
    # Start a new game with the same field
    payload = FieldSelection(user_id=user_id, field=last_result.field)
    game_response = start_game(payload, db)
    return game_response  

#game home page
@router.get("/{user_id}")
def game_homepage(user_id:int):
    fields = ["developer", "marketing", "finance", "general","law" ] 
    user_game.pop(user_id,None)
    return {"fields":fields, "user_id":user_id}
    
    
    

