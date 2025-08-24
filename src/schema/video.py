from pydantic import BaseModel, Field

class VideoRequest(BaseModel):
    video_url: str = Field(..., description="URL of the video to be processed")
    language: str = Field(default="en", description="Language for processing (default: en)")

class VideoResponse(BaseModel):
    summary: str = Field(..., description="Summary of the video")
    language: str = Field(default="en", description="Language of the response (default: en)")
    title: str = Field(..., description="Title of the video")
