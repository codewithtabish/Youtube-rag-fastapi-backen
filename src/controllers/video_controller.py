from servives.video_servives import summarize_video_service
from schema.video import VideoRequest
from fastapi import Response
def summarize_video_controller(request:VideoRequest)->Response:
    return  summarize_video_service(request)
    
    
    # video_url = data.get("video_url")
    # language = data.get("language", "en")
    # return {"message": f"Video URL: {video_url}, Language: {language}"}
