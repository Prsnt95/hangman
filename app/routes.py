from app.models import Guess
from fastapi import APIRouter
import random

router=APIRouter()


WORDS={}

@router.get("/")

def read_root():
    return{"hello":"world"}



# @router.post("/start")
# def start_game():
#     pass



# @router.post("/guess/")
# def guess_letter(guess:Guess):
#     pass


    

   