from fastapi import APIRouter , Response
from fastapi.concurrency import run_in_threadpool
from controllers.video_controller import summarize_video_controller
from schema.video import VideoRequest


video_router: APIRouter = APIRouter()

@video_router.post("/summarize-video")
async def summarize_video_router(request: VideoRequest)->Response:
    # Run blocking controller in threadpool
    response = await run_in_threadpool(summarize_video_controller, request)
    return response
