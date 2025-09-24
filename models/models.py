from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from db import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False)
    
    game_states = relationship("GameState", back_populates="user")
    results = relationship("Result", back_populates="user")
    
    
class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=False)
    option_d = Column(Text, nullable=False)
    correct_option = Column(String(1), nullable=False)
    stage = Column(Integer, nullable=False)
    field = Column(String(50), nullable=False)
    
class Result(Base):
    __tablename__ = "results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    field = Column(String(50), nullable=False)
    score = Column(Integer,nullable=False, default=0)
    stage_reached = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="game_over")
    
    user = relationship("User", back_populates="results")
    
    
class GameState(Base):
    __tablename__ = "Game_state"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    stage = Column(Integer, default=1)
    current_question_index = Column(Integer, default=0)
    score = Column(Integer, default=0)
    field = Column(String(50), nullable=True)
    
    
    user = relationship("User", back_populates="game_states")
    
    
class Riddle(Base):
    __tablename__ = "riddles"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)