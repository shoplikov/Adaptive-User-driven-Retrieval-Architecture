import torch
from transformers import AutoModelForCausalLM
from peft import PeftModel
import config  

base_model = AutoModelForCausalLM.from_pretrained(
    config.BASE_MODEL_PATH,
    torch_dtype=torch.float16,
    device_map={"": "cpu"},
    low_cpu_mem_usage=False
)

model = PeftModel.from_pretrained(
    base_model,
    config.LORA_PATH,
    device_map={"": "cpu"}
)

model = model.merge_and_unload()
model.save_pretrained(config.OUTPUT_PATH, max_shard_size="1GB")
