# handler.py
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

def model_fn(model_dir):
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForCausalLM.from_pretrained(
        model_dir,
        trust_remote_code=True,
        torch_dtype=torch.float16  # or float32 if CPU
    )
    model.eval()
    return (model, tokenizer)

def predict_fn(data, model_tokenizer):
    model, tokenizer = model_tokenizer
    prompt = data.get("prompt", "")
    inputs = tokenizer(prompt, return_tensors="pt")
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=100)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)
