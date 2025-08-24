from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

try:
    llm=ChatOpenAI(model='gpt-5')

    
except Exception as e:
    print("The api key is not defined ....")
    
output_parser = StrOutputParser()

# prompt_template = PromptTemplate(template="Summarize the following video: {video_url}")
