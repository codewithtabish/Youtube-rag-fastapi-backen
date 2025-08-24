from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    OPEN_API_KEY:str = os.getenv("OPEN_API_KEY")
    MODEL_NAME:str = os.getenv("MODEL_NAME", "gpt-5")
    
 
settings=Settings()    
    
    

