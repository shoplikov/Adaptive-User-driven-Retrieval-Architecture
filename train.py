import os
import json
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
import config

# --- Настройки ---
MODEL_NAME = "NousResearch/Hermes-3-Llama-3.2-3b"  # 3B модель
DATA_PATH = "wildfeedback/data/conversations_raw.json"
OUTPUT_DIR = config.LORA_PATH

# --- Загружаем датасет ---
def load_dataset(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    samples = []
    for convo in data:
        dialog_text = ""
        for turn in convo["turns"]:
            role = turn["role"]
            text = turn["text"].strip()
            if role == "user":
                dialog_text += f"User: {text}\n"
            else:
                dialog_text += f"Assistant: {text}\n"
        samples.append({"text": dialog_text})
    return Dataset.from_list(samples)

dataset = load_dataset(DATA_PATH)

# --- Токенизация ---
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
tokenizer.pad_token = tokenizer.eos_token

def tokenize_fn(example):
    enc = tokenizer(
        example["text"],
        truncation=True,
        padding="max_length",
        max_length=512  # уменьшаем для 5ГБ VRAM
    )
    enc["labels"] = enc["input_ids"].copy()  # нужно для Causal LM
    return enc

dataset = dataset.map(tokenize_fn, batched=True)

# --- Загружаем модель в 8-бит ---
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    load_in_8bit=True,
    device_map="auto"
)

# --- Подготовка модели для LoRA ---
model = prepare_model_for_kbit_training(model)

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)

# --- Настройки тренинга ---
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    num_train_epochs=2,
    logging_dir="./logs",
    logging_steps=5,
    save_strategy="epoch",
    fp16=True,
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    tokenizer=tokenizer
)

# --- Обучение ---
print("Начало обучения LoRA...")
trainer.train()

# --- Сохраняем веса ---
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
print(f"LoRA training finished. Weights saved to {OUTPUT_DIR}")
