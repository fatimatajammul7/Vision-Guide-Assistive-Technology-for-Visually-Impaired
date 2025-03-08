from pydantic import BaseModel, validator, EmailStr, Field



class WelcomeMessage(BaseModel):
    Welcome: str


class Message(BaseModel):
    message: str
    
class VideoPath(BaseModel):
    path: str
    

class Prompt(BaseModel):
    prompt: str
