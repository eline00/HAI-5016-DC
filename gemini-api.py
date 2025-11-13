# Minimal script that reads GEMINI_API_KEY from a .env file and calls the API.
from dotenv import load_dotenv
import os
import sys
from google import genai
import json
from pathlib import Path
import datetime  # added so we can tell the model today's date

# Load variables from .env into the environment
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not set. Put GEMINI_API_KEY=your_key in a .env file or export it.")
    sys.exit(1)

# Pass the api_key explicitly to the client
client = genai.Client(api_key=api_key)

# New: simple file-backed memory to remember recent exchanges
MEMORY_FILE = Path(__file__).parent / "memory.json"
MAX_MEMORY = 10  # keep last N exchanges

def load_memory():
    if MEMORY_FILE.exists():
        try:
            return json.loads(MEMORY_FILE.read_text(encoding="utf-8")) or []
        except Exception:
            return []
    return []

def save_memory(mem):
    try:
        MEMORY_FILE.write_text(json.dumps(mem, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        # ignore save errors for now
        pass

memory = load_memory()

try:
    # Make a loop that asks for the user's input and sends it to the model until the user types 'exit'
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue

        # control commands
        cmd = user_input.lower()
        if cmd == 'exit':
            break
        if cmd == 'show memory':
            # print a short view of stored memory
            if not memory:
                print("[memory empty]")
            else:
                for i, ex in enumerate(memory[-MAX_MEMORY:], start=1):
                    print(f"{i}. User: {ex.get('user')}\n   AI: {ex.get('ai')}\n")
            continue
        if cmd == 'forget':
            memory = []
            save_memory(memory)
            print("Memory cleared.")
            continue

        # Build a simple conversation string from recent memory + current input
        # Add the current date/time so the model knows today's date
        current_dt = datetime.datetime.now().astimezone().isoformat()
        convo_parts = [f"Current date: {current_dt}"]
        for ex in memory[-MAX_MEMORY:]:
            convo_parts.append(f"User: {ex.get('user')}\nAI: {ex.get('ai')}")
        convo_parts.append(f"User: {user_input}")
        prompt = "\n\n".join(convo_parts)

        # Send combined prompt to the model so it can use recent context
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        ai_text = getattr(response, "text", str(response))

        # Print and store exchange
        print("AI:", ai_text)

        memory.append({"user": user_input, "ai": ai_text})
        # keep memory size bounded
        memory = memory[-MAX_MEMORY:]
        save_memory(memory)

except Exception as e:
    # Simple error message; inspect exception for details
    print("API call failed:", e)