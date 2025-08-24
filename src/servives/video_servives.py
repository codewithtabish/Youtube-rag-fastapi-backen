# src/services/video_services.py

import json
from fastapi import Response, status
from pydantic import ValidationError
from langchain_core.prompts import PromptTemplate
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptList,
    Transcript,
    NoTranscriptFound,
    TranscriptsDisabled,
)
from schema.video import VideoRequest
from core import llm, output_parser
from utils import extract_video_id
import openai


def summarize_video_service(request: VideoRequest) -> Response:
    try:
        video_url = request.video_url
        target_language = request.language or "en"

        # 1. Extract video ID
        video_id = extract_video_id(video_url)
        if not video_id:
            return Response(
                content=json.dumps({"error": "Invalid YouTube URL"}),
                status_code=status.HTTP_400_BAD_REQUEST,
                media_type="application/json",
            )

        transcript_api: YouTubeTranscriptApi = YouTubeTranscriptApi()

        try:
            # 2. Get transcript list
            transcript_list: TranscriptList = transcript_api.list(video_id)

            # Debugging: print available transcripts
            for t in transcript_list:
                print(
                    "The language is ", t.language,
                    "The language code is ", t.language_code,
                    "Auto Generated", t.is_generated,
                    "Translation Available", t.translation_languages
                )

            # ✅ 3. Always just pick the first available transcript
            transcript_data: Transcript = next(iter(transcript_list), None)
            if not transcript_data:
                return Response(
                    content=json.dumps({"error": "No transcript found"}),
                    status_code=status.HTTP_404_NOT_FOUND,
                    media_type="application/json",
                )

            # 4. Fetch transcript data
            snippets = transcript_data.fetch()
            full_transcript_data = " ".join([single.text for single in snippets])

            if not full_transcript_data.strip():
                return Response(
                    content=json.dumps({"error": "Transcript is empty or unavailable"}),
                    status_code=status.HTTP_404_NOT_FOUND,
                    media_type="application/json",
                )

        except (NoTranscriptFound, TranscriptsDisabled):
            # ✅ Handle case when no transcript is available at all
            return Response(
                content=json.dumps({"error": "No subtitles/transcript available for this video"}),
                status_code=status.HTTP_404_NOT_FOUND,
                media_type="application/json",
            )

        # 5. Summarize with LLM
        try:
            prompt = PromptTemplate(
                template="Summarize the following transcript into {target_language}: \n\n{transcript}",
                input_variables=["transcript", "target_language"]
            )
            chain = prompt | llm | output_parser

            response = chain.invoke({
                "transcript": full_transcript_data,
                "target_language": target_language
            })

            return Response(
                content=json.dumps({"summarize transcript": response}),
                status_code=status.HTTP_200_OK,
                media_type="application/json",
            )

        # ✅ OpenAI / LLM Specific Error Handling
        except openai.AuthenticationError as auth_error:
            return Response(
                content=json.dumps({
                    "error": "Authentication with OpenAI failed",
                    "details": str(auth_error) or "Invalid or missing API key."
                }),
                status_code=status.HTTP_401_UNAUTHORIZED,
                media_type="application/json",
            )
        except openai.APITimeoutError as time_out_error:
            return Response(
                content=json.dumps({
                    "error": "Summarization failed due to OpenAI timeout",
                    "details": str(time_out_error) or "The request to OpenAI timed out. Please try again."
                }),
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                media_type="application/json",
            )
        except openai.APIConnectionError as conn_error:
            return Response(
                content=json.dumps({
                    "error": "Network issue while connecting to OpenAI",
                    "details": str(conn_error) or "Please check your internet connection and try again."
                }),
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                media_type="application/json",
            )
        except openai.RateLimitError as rate_error:
            return Response(
                content=json.dumps({
                    "error": "Rate limit exceeded for OpenAI API",
                    "details": str(rate_error) or "Too many requests. Please wait and try again."
                }),
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json",
            )
        except openai.APIError as api_error:
            return Response(
                content=json.dumps({
                    "error": "Unexpected error from OpenAI API",
                    "details": str(api_error) or "An unknown error occurred on OpenAI's side."
                }),
                status_code=status.HTTP_502_BAD_GATEWAY,
                media_type="application/json",
            )

    except ValidationError as e:
        return Response(
            content=json.dumps({"error": e.errors()}),
            status_code=status.HTTP_400_BAD_REQUEST,
            media_type="application/json",
        )
    except Exception as e:
        return Response(
            content=json.dumps({"error": str(e) ,"issue":"its network problem"}),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            media_type="application/json",
        )
