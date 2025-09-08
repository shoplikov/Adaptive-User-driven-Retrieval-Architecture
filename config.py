import os
from dotenv import load_dotenv

load_dotenv()


BASE_MODEL_PATH = os.getenv("BASE_MODEL_PATH")
LORA_PATH = os.getenv("LORA_PATH")
OUTPUT_PATH = os.getenv("OUTPUT_PATH")
