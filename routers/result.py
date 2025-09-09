from fastapi import APIRouter, HTTPException
from .game import user_game,user_results

router = APIRouter(prefix = "/results", tags = ["results"])


@router.get("/{user_id}")
def game_results(user_id:int):
    game = user_game.get(user_id)
    
    if game:  
        return{
            "field": game.get("field","Not selected"),
            "Stage": game["stage"],
            "score": game["current_question_index"] * 10,
            "progess": f"{game['current_question_index']}/5"
        }
        
                
    result = user_results.get(user_id)
    if result:
        return{
            "field": result["field"],
            "final_score": result["score"],
            "status": "game_over"
            }
        
    
        
    
    

