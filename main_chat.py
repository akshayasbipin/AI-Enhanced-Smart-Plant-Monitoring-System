import requests
import streamlit as st
import json
from dotenv import load_dotenv
import os

# Load environment variables (in case you want to use them later)
load_dotenv()

# Function to get plant care response from Ollama
def get_response(query):  
    full_response = ""
    try:
        OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")
        MODEL_NAME = os.getenv("MODEL_NAME")

        print(query)  # Optional: Debug log

        user_input = f'''
You are a friendly and knowledgeable assistant for a smart plant monitoring app. Your goal is to help users keep their plants healthy and thriving. You have access to real-time sensor data (such as soil moisture, temperature, humidity, and light exposure), plant species information, and care recommendations.

You can assist with:

- Interpreting sensor data
- Sending watering reminders
- Diagnosing common plant problems (e.g., yellowing leaves, drooping stems)
- Giving personalized plant care tips
- Notifying users when thresholds are crossed (e.g., soil too dry, low light levels)
- Providing info about specific plant types
- Answering general plant care questions

Always be encouraging and helpful, even if the plant is struggling. Use casual, friendly language while being clear and informative.

User Query: {query}

If the query is not related to plant care, monitoring, or something you understand, respond politely with something like:
“Sorry, I couldn't understand your question. Could you rephrase it or ask something related to your plant’s health or setup?”
Otherwise, respond with clear, actionable advice based on the user’s concern and available plant data.
'''

        payload = {
            "model": MODEL_NAME,
            "prompt": user_input,
            "stream": True,
            "options": {
                "max_tokens": 100
            }
        }   

        with st.chat_message("assistant"):
            response_box = st.empty()
            with requests.post(OLLAMA_API_URL, json=payload, stream=True) as response:
                skip = False
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode("utf-8"))
                            response_chunk = data.get("response", "")
                            if response_chunk == "<think>":
                                skip = True
                                continue
                            if skip:
                                if response_chunk == "</think>":
                                    skip = False
                                continue
                            full_response += response_chunk
                            # Optionally show partial response in real-time
                            # response_box.markdown(full_response + "▌")
                        except Exception as e:
                            st.error(f"Error decoding response: {e}")
    except Exception as e:
        print("Error parsing response:", e)
    return full_response

# For CLI testing
if __name__ == "__main__":
    query = input("🌱 Ask your plant care question: ")
    response = get_response(query)
    print("\n🌿 FINAL RESPONSE:\n", response)
