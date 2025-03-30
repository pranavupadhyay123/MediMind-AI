# Medical Image Analysis Chatbot

## 📌 Overview
This project is a **Medical Image Analysis Chatbot** that allows users to upload medical images and receive AI-generated diagnoses. It also answers medical-related text queries while blocking non-medical questions.

## 🚀 Features
- **Medical Image Upload:** Users can upload medical images for analysis.
- **AI-Powered Diagnosis:** Uses Groq API to analyze medical images and provide insights.
- **Context Awareness:** AI considers past conversation history for better responses.
- **Non-Medical Query Filtering:** Rejects questions unrelated to healthcare.
- **Graphical User Interface (GUI):** Built with Tkinter for an interactive experience.

## 🛠️ Installation
### **1. Clone the Repository**
```sh
git clone https://github.com/your-username/medical-chatbot.git
cd medical-chatbot
```

### **2. Create a Virtual Environment (Optional but Recommended)**
```sh
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate  # On Windows
```

### **3. Install Dependencies**
```sh
pip install -r requirements.txt
```

## 📦 Dependencies
The project requires the following Python packages:
- **groq** – For AI-powered responses.
- **python-dotenv** – For managing API keys securely.
- **pillow** – For image processing.
- **pytesseract** – For extracting text from images.
- **tkhtmlview** – For rendering formatted text in the chat window.

## 🔧 Configuration
1. **Set Up API Keys:** Create a `.env` file in the root directory and add your API key:
   ```sh
   GROQ_API_KEY=your_groq_api_key_here
   ```
2. **Ensure Tesseract OCR is Installed:**
   - Install [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) and add it to your system path.

## 🎮 Usage
Run the application with:
```sh
python app.py
```
### **How It Works:**
1. Upload a medical image for AI analysis.
2. Ask medical-related questions in the chat.
3. The AI will refuse to answer non-medical queries.

## 🤖 How It Works
- The chatbot interacts with **Llama-based AI models** via **Groq API**.
- It encodes images in **Base64 format** and sends them for analysis.
- It filters user queries to ensure only medical-related topics are processed.

## 📜 License
This project is licensed under the **MIT License**.
