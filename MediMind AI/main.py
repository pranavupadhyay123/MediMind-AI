from diagnosis import analyze_symptoms
from prescription import parse_prescription
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py [diagnose|parse]")
        sys.exit(1)
    
    mode = sys.argv[1].lower()
    
    if mode == "diagnose":
        symptoms = input("Enter your symptoms: ")
        result = analyze_symptoms(symptoms)
        print("\nDiagnosis and recommended cure:")
        print(result)
        
    elif mode == "parse":
        prescription_text = input("Enter your prescription text: ")
        result = parse_prescription(prescription_text)
        print("\nParsed prescription details:")
        print(result)
        
    else:
        print("Invalid mode. Use 'diagnose' or 'parse'.")

if __name__ == "__main__":
    main()
