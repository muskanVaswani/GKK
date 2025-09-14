from fastapi import APIRouter,Depends, HTTPException
from .game import user_game,user_results
from models.models import Result
from sqlalchemy.orm import Session
from db import get_db

router = APIRouter(prefix = "/results", tags = ["results"])


@router.get("/{user_id}")
def game_results(user_id:int, db:Session = Depends(get_db)):
    game = user_game.get(user_id)
    
    if game:  
        return{
            "field": game.get("field","Not selected"),
            "Stage": game["stage"],
            "score": game["stage"]-1 * 5,
            "progess": f"{game['current_question_index']}/5",
            "status": "in_progress",
            "options": {
                "play_again": f"/game/restart/{user_id}",
                "go_home": f"/game/home/{user_id}"
            }
        }
        
                
    db_result = db.query(Result).filter(Result.user_id == user_id).order_by(Result.user_id.desc()).first()
    if db_result:
        return{
            "field": db_result.field,
            "final_score": db_result.score,
            "stage_reached": db_result.stage,
            "status": "game_over",
            "options": {
                "play_again": f"/game/restart/{user_id}",
                "go_home": f"/game/home/{user_id}"
            }
        }
    
    return{"message": "No game data found. Start a new game!"}
        
    
        
    
    

