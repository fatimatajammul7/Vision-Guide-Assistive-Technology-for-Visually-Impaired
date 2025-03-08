# uvicorn main:app --env-file .env --reload
import routes.user
import routes.llm

from models.main import WelcomeMessage
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv
load_dotenv()


# Import routes

tags_metadata = [
    {
        "name": "Home",
        "description": "Displays Welcome Message.",
    },

    {
        "name": "User",
        "description": "User related routes.",
    }
]

description = """
Vision Guide API 🚀
"""

app = FastAPI(
    title="Vision Guide",
    description=description,
    summary="See what is in front of you with our eyes",
    version="APLHA",
    tags_metadata=tags_metadata
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.user.router)
# app.include_router(routes.llm.router)



@app.get("/", tags=['Home'])
def welcome_to_the_API() -> WelcomeMessage:
    return {"Welcome": "VisionGuide"}


if __name__ == '__main__':
    uvicorn.run("__main__:app")
    
    
# https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4
