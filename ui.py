import tkinter as tk
from tkinter import scrolledtext, END
import requests
import json
import os
from RAG.main import RAG
from wildfeedback.praise import PraisePipeline

# CONFIGURATION
LMSTUDIO_ENDPOINT = "http://localhost:1234/v1/chat/completions"  # Change if needed
CONV_PATH = os.path.join("wildfeedback", "data", "conversations_raw.json")
STRATEGY_PATH = os.path.join("wildfeedback", "data", "strategies.json")
CLASSIFIER_PATH = os.path.join("wildfeedback", "praise_classifier.pkl")

# Load RAG and Feedback pipeline
rag = RAG(docs_path=os.path.join("RAG", "documents.json"))
feedback = PraisePipeline(STRATEGY_PATH, CLASSIFIER_PATH)

# Load or initialize conversation history
if os.path.exists(CONV_PATH):
    with open(CONV_PATH, "r", encoding="utf-8") as f:
        conversations = json.load(f)
else:
    conversations = []

current_convo = {"conversation_id": None, "turns": []}

# --- UI ---
class ChatUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AURA Chat (Hermes 3)")
        self.root.option_add('*Font', 'TkDefaultFont')  # Ensure default font supports Unicode
        self.chat = scrolledtext.ScrolledText(root, state='disabled', width=80, height=25, wrap='word', font=('TkDefaultFont', 10))
        self.chat.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        self.entry = tk.Entry(root, width=70, font=('TkDefaultFont', 10))
        self.entry.grid(row=1, column=0, padx=10, pady=5, sticky='w')
        self.entry.bind('<Return>', self.send)
        self.send_btn = tk.Button(root, text="Send", command=self.send)
        self.send_btn.grid(row=1, column=1, padx=5, pady=5, sticky='e')
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def display(self, who, text):
        self.chat.config(state='normal')
        try:
            # Ensure text is properly decoded as UTF-8
            if isinstance(text, bytes):
                text = text.decode('utf-8')
            self.chat.insert(END, f"{who}: {text}\n")
        except Exception as e:
            print(f"Display error: {e}")
            self.chat.insert(END, f"{who}: [Error displaying message]\n")
        self.chat.see(END)
        self.chat.config(state='disabled')

    def send(self, event=None):
        user_msg = self.entry.get().strip()
        if not user_msg:
            return
        self.display("You", user_msg)
        self.entry.delete(0, END)
        # RAG retrieval
        docs = rag.query(user_msg)
        context = "\n".join([doc['content'] for doc in docs])
        prompt = f"[CONTEXT]\n{context}\n[USER]\n{user_msg}"
        # Call LM Studio endpoint
        ai_reply = self.query_ai(prompt)
        self.display("Hermes 3", ai_reply)
        # Classify feedback and select highest probability label
        sat_dsat = None
        try:
            feedback_result = feedback.classify(user_msg)
            print("Feedback classification:", feedback_result)
            sat_dsat = max(feedback_result, key=feedback_result.get)  # 'SAT', 'DSAT', or 'Neutral'
        except Exception as e:
            print("Feedback error:", e)
        # Save turn with sat_dsat metric
        current_convo["turns"].append({
            "role": "user",
            "text": user_msg,
            "sat_dsat": sat_dsat
        })
        current_convo["turns"].append({
            "role": "assistant",
            "text": ai_reply
        })

    def query_ai(self, prompt):
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": "hermes-3-llama-3.2-3b",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 512,
            "temperature": 0.7
        }
        try:
            resp = requests.post(LMSTUDIO_ENDPOINT, headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"[Error contacting AI: {e}]"

    def on_close(self):
        # Save conversation if any turns
        if current_convo["turns"]:
            import uuid
            current_convo["conversation_id"] = str(uuid.uuid4())
            conversations.append(current_convo)
            with open(CONV_PATH, "w", encoding="utf-8") as f:
                json.dump(conversations, f, indent=2, ensure_ascii=False)
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    # Set default encoding for Tkinter
    import sys
    if sys.platform.startswith('win'):
        root.option_add('*Dialog.msg.font', 'TkDefaultFont')
        root.option_add('*Dialog.msg.wrapLength', '6i')
    app = ChatUI(root)
    root.mainloop()
