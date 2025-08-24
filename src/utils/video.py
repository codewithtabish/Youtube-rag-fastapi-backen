def extract_video_id(url: str):
    # Example for YouTube link
    import re
    match = re.search(r"v=([^&]+)", url)
    if match:
        return match.group(1)
    return None