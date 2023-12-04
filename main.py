from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import OAuth2, APIKeyHeader
from openai import AsyncOpenAI
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from starlette import status

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

api_key = os.environ.get('API_KEY')

app = FastAPI()
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)
oauth2_scheme = OAuth2()


def get_api_key(api_key_header: str = Security(api_key_header),) -> str:
    if api_key_header in api_key:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )


openai_api_key = os.environ.get('OPENAI_API_KEY')

chat_gpt = AsyncOpenAI(
    api_key=openai_api_key
)


class ChatGpt(BaseModel):
    message: list


@app.post("/chatgpt")
async def ask_chatgpt(item: ChatGpt, api_key: str = Security(get_api_key)):
    if api_key not in api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Forbidden"
        )
    gpt_response = await chat_gpt.chat.completions.create(
        model="gpt-4",
        messages=item.message
    )
    return gpt_response
