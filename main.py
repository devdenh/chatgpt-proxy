import os
from typing import List, Dict, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Security
from fastapi.security import OAuth2, APIKeyHeader
from openai import AsyncOpenAI
from pydantic import BaseModel
from starlette import status

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

env_api_key = os.environ.get('API_KEY')

app = FastAPI()
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)
oauth2_scheme = OAuth2()


def get_api_key(api_key_header: str = Security(api_key_header),) -> str:
    if not env_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )
    return api_key_header


openai_api_key = os.environ.get('OPENAI_API_KEY')

chat_gpt = AsyncOpenAI(
    api_key=openai_api_key
)


class ChatGptWithTools(BaseModel):
    messages: List
    tools: Optional[List[dict]] = None  # Добавляем поле tools для передачи параметров функции


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/chatgpt_with_tools")
def ask_chatgpt_with_tools(item: ChatGptWithTools, header_api_key: str = Security(get_api_key)):
    if header_api_key != env_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Forbidden"
        )

    kwargs = {
        "model": "gpt-4",
        "messages": item.messages
    }
    if item.tools:
        kwargs = {
            "model": "gpt-4",
            "messages": item.messages,
            "tools": item.tools
        }
    # Вызываем функцию с использованием tools
    gpt_response = chat_gpt.chat.completions.create(**kwargs)

    return gpt_response
