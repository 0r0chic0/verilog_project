import torch
from transformers import AutoModelForCausalLM

# 1) load in the same dtype you’ll use in prod
model = AutoModelForCausalLM.from_pretrained(
    "./Qwen",
    #torch_dtype=torch.float16,      # or torch.float32 for full-precision
    device_map="auto",
)

# 2) compute total bytes
total_params = sum(p.numel() for p in model.parameters())
bytes_per_param = next(model.parameters()).element_size()
total_bytes = total_params * bytes_per_param

print(f"Theoretical model size: {total_bytes/1024**3:.2f} GB")