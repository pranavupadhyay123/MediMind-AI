import os
import datetime
import json
from groq import Groq
from dotenv import dotenv_values

# Get the parent directory path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from parent directory .env file
env_vars = dotenv_values(os.path.join(parent_dir, ".env"))

Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "DoctorAI")
GroqAPIKey = env_vars.get("GroqAPIKey", "YOUR_GROQ_API_KEY")

client = Groq(api_key=GroqAPIKey)

# Define the path for the chat log
chat_log_path = os.path.join(parent_dir, "Data", "ChatLog.json")
# Ensure the Data directory exists
os.makedirs(os.path.dirname(chat_log_path), exist_ok=True)

# Load or initialize the chat log
try:
    with open(chat_log_path, "r") as f:
        messages = json.load(f)
except FileNotFoundError:
    messages = []
    with open(chat_log_path, "w") as f:
        json.dump([], f)

def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    
    data = f"Please use this real-time information if needed, \n"
    data += f"Day: {day}, Date: {date} {month} {year}, Time: {hour} hours {minute} minutes {second} seconds.\n"
    return data

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in all language***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SystemChatBot = [
    {"role": "system", "content": System}
]

def ChatBot(Query):
    global messages
    try:
        # Load the existing chat log
        with open(chat_log_path, "r") as f:
            messages = json.load(f)

        # Append the user's query to the chat log
        messages.append({"role": "user", "content": Query})

        # Request a response from the Groq-based chatbot
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages = SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )
        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
        Answer = Answer.replace("</s>", "")

        # Append the assistant's response and update the chat log
        messages.append({"role": "assistant", "content": Answer})
        with open(chat_log_path, "w") as f:
            json.dump(messages, f, indent=4)

        return AnswerModifier(Answer)
    
    except Exception as e:
        print(f"Error: {e}")
        with open(chat_log_path, "w") as f:
            json.dump([], f, indent=4)
        return ChatBot(Query)
