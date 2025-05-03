from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

router = APIRouter(prefix="/generate", tags=["generate"])

quantization_config = BitsAndBytesConfig(load_in_8bit=True)

# 1) Point to your GPTQ folder
MODEL_DIR = Path(__file__).resolve().parent.parent.parent / "Qwen"

# 2) Load once at import time
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_DIR,
    trust_remote_code=True,
    local_files_only=True,
)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_DIR,
    quantization_config=quantization_config,
    trust_remote_code=True,
    local_files_only=True,
    device_map="auto", 
    torch_dtype=torch.bfloat16,           
)
model.eval()


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

    # Tokenize + send to device
    inputs = tokenizer(req.prompt, return_tensors="pt", padding=True).to(model.device)
    model = torch.compile(model)
    
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=req.max_new_tokens,
            temperature=req.temperature,
            eos_token_id=tokenizer.eos_token_id,
            do_sample=True,    # or False if you want greedy
            top_p=0.95,        # works if do_sample=True
        )

    full = tokenizer.decode(out[0], skip_special_tokens=True)
    # strip the prompt prefix
    return GenerateResponse(text=full[len(req.prompt):])
