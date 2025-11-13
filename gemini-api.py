# Minimal script that reads GEMINI_API_KEY from a .env file and calls the API.
from dotenv import load_dotenv
import os
import sys
from google import genai

# Load variables from .env into the environment
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not set. Put GEMINI_API_KEY=your_key in a .env file or export it.")
    sys.exit(1)

# Pass the api_key explicitly to the client
client = genai.Client(api_key=api_key)

try:
    # Make a loop that asks for the user's input and sends it to the model until the user types 'exit'
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_input
        )
        print("AI:", response.text)
except Exception as e:
    # Simple error message; inspect exception for details
    print("API call failed:", e)