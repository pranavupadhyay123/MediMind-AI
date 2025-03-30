from llm import ChatBot

def analyze_symptoms(symptoms):
    prompt = f"Patient symptoms: {symptoms}. Provide a possible diagnosis and recommended cure."
    response = ChatBot(prompt)
    return response
