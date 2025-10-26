
from typing import Any,Callable
from fastapi import FastAPI,status
from fastapi.requests import Request
from fastapi.responses import JSONResponse


class CustomException(Exception):
    """This is the base class for all Custom Exception Handeler"""
    pass 


#<----------------------app/internal/JWT.py-------------------------------->

class UserNotFound(CustomException):
    """User email is not found in database"""
    pass 

class UserIdNotFound(CustomException):
    """User found from database but may be problem with something else"""
    pass 


class ExpireToken(CustomException):
    """User Token has expire"""
    pass 

class Crediential(CustomException):
    """Could Decode Token From user Information"""
    pass

#<----------------------app/internal/signup.py-------------------------------->
class MailExistError(CustomException):
    pass 



# <-----------------------Exception Handeler Message------------------------------->
def create_exception_handler(status_code:int,
                    initial_details:Any)->Callable[[Exception,Request],JSONResponse]:
    async def exception_handeler(request:Request,exc:CustomException):
        return JSONResponse(
            content=initial_details,
            status_code=status_code
        )
    return exception_handeler




# <----------------------Add All the exception in Fastapi=app---------------------->
def register_all_errors(app:FastAPI):
    
    app.add_exception_handler(UserNotFound,create_exception_handler(
        status_code=status.HTTP_401_UNAUTHORIZED,
        initial_details={
            "message": "User not found. Please, provide right infomation.",
            "error_code" : "user not found"
        }
    ))

    app.add_exception_handler(UserIdNotFound,create_exception_handler(
        status_code=status.HTTP_401_UNAUTHORIZED,
        initial_details={
            "message": "Gmail not found. Please, create a new account",
            "error_code" : "gmail not found"
        }
    ))
    
    
    app.add_exception_handler(ExpireToken,create_exception_handler(
        status_code=status.HTTP_400_BAD_REQUEST,
        initial_details={
            "message":"Token has expire. Please, log in again",
            "error_code":"login again"
        }
    ))
    
    app.add_exception_handler(Crediential,create_exception_handler(
        status_code=status.HTTP_404_NOT_FOUND,
        initial_details={
            "message": "Can't identifing user from token",
            "error_code" : "login again"
        }
    ))
    
    app.add_exception_handler(MailExistError,create_exception_handler(
        status_code=status.HTTP_400_BAD_REQUEST,
        initial_details={
            "message":"With this email a account already exists. Try with another email",
            "error_code":"email exists"
        }
    ))


    
    