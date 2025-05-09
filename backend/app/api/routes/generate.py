from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import ollama

router = APIRouter(prefix="/generate", tags=["generate"])

class GenerateRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 256
    temperature: float = 0.7

class GenerateResponse(BaseModel):
    text: str

@router.post("/", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    if not req.prompt.strip():
        raise HTTPException(400, "Prompt must not be empty")
    
    response = ollama.chat(
        model="codeqwen:latest",
        messages=[
            {"role": "user", "content": req.prompt}
        ]
    )

    return GenerateResponse(text=response["message"]["content"])
