from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import ollama
import re

def normalize_verilog(text: str) -> str:
    # Lowercase, remove all whitespace and semicolons for comparison
    return re.sub(r"[\s;]", "", text).lower()

def clean_completion(response_text: str, prompt: str) -> str:
    code = response_text

    # Remove ```verilog and trailing ```
    if code.startswith("```verilog"):
        code = code[len("```verilog"):].lstrip("\r\n ")
    if code.endswith("```"):
        code = code[:-3].rstrip("\r\n ")

    # Normalize for fuzzy prefix comparison
    normalized_code = normalize_verilog(code)
    normalized_prompt = normalize_verilog(prompt)

    if normalized_code.startswith(normalized_prompt):
        # Remove approximate prompt match from original code
        index = len(prompt)
        code = code[index:].lstrip("\r\n ")

    # Fallback: try to extract meaningful Verilog lines
    if not any(kw in code for kw in ["module", "input", "output", "always", "endmodule"]):
        lines = response_text.splitlines()
        verilog_lines = [
            line for line in lines
            if line.strip().startswith(("module", "input", "output", "always", "endmodule", "reg", "wire", "assign"))
        ]
        code = "\n".join(verilog_lines).strip()

    return code


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
    
    prompt = (
        req.prompt.strip()
        + "\n\n"
        + "// Continue this Verilog code. ONLY output the rest of the code—no comments or explanation.\n"
    )
    
    response = ollama.generate(
        "codeqwen:latest", prompt
    )
    code = response["response"].strip()

    return GenerateResponse(text=code)