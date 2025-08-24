from fastapi import FastAPI
from fastapi import Response
from dotenv import load_dotenv
from routers.video_router import video_router
from langchain_openai import ChatOpenAI

load_dotenv()

# llm=ChatOpenAI(model='gpt-5')

app:FastAPI = FastAPI(title="YouTube Multi-Language Summarizer")

@app.get("/")
def read_root():
    return Response(
        content="Welcome to YouTube Multi-Language Summarizer API. Visit /docs for API documentation again.",
        media_type="text/plain",
        status_code=200
        
    )

@app.get("/health")
def health_check():
    return Response(
        content="Health check OK",
        media_type="text/plain",
        status_code=200
    )
    

app.include_router(router=video_router, prefix="/video", tags=["Video"])    