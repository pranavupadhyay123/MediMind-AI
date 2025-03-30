from llm import ChatBot

def parse_prescription(prescription_text):
    prompt = f"Parse the following prescription text and list the medication, dosage, and timing details: {prescription_text}"
    response = ChatBot(prompt)
    return response
