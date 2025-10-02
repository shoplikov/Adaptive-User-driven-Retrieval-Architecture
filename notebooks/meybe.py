from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch

# Path to your folder (base + LoRA)
model_dir = "inference/"   # adjust if base+adapter are in subfolders

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_dir)

# Load base model
base_model = AutoModelForCausalLM.from_pretrained(
    model_dir,
    torch_dtype=torch.bfloat16,   # or torch.float16 if GPU supports
    device_map="auto"
)

# Load and apply LoRA adapter
model = PeftModel.from_pretrained(base_model, model_dir)
model = model.merge_and_unload()   # (optional) merge LoRA into base for faster inference

# Example prompt (Hermes is chat-tuned, so use messages + chat_template)
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain quantum computing in simple terms."}
]

prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

# Tokenize
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

# Generate
outputs = model.generate(
    **inputs,
    max_new_tokens=256,
    temperature=0.7,
    top_p=0.9,
    do_sample=True
)

print(tokenizer.decode(outputs[0], skip_special_tokens=True))
