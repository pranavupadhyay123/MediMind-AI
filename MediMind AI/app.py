import base64
import os
import tkinter as tk
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
from groq import Groq
from PIL import Image
import pytesseract
from llm import ChatBot
from prescription import parse_prescription
from dotenv import dotenv_values


# Get the parent directory path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from parent directory .env file
env_vars = dotenv_values(os.path.join(parent_dir, ".env"))

Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "MediMind AI")
GroqAPIKey = env_vars.get("GroqAPIKey", "YOUR_GROQ_API_KEY")

client = Groq(api_key=GroqAPIKey)

# Dark theme colors
BG_COLOR = "#1e1e1e"
TEXT_COLOR = "#ffffff"
BUTTON_COLOR = "#444"
BUTTON_HOVER = "#666"
USER_BG = "#128C7E"
BOT_BG = "#262626"
CHAT_WIDTH = 0.75  # 75% of the screen width for messages
BORDER_RADIUS = 15

# Chat history to maintain context
chat_history = []

def encode_image(image_path):
    try:
        if os.path.getsize(image_path) > 4 * 1024 * 1024:
            return None, "Error: Image size exceeds 4MB limit."
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8"), None
    except Exception as e:
        return None, f"Error encoding image: {e}"

def generate_context_prompt(query):
    """Generate a prompt that includes chat history context"""
    # Only use the last 5 exchanges (10 messages) to avoid making the prompt too long
    recent_history = chat_history[-10:] if len(chat_history) > 10 else chat_history
    
    context_prompt = "Previous conversation:\n"
    for msg in recent_history:
        role = "User" if msg["role"] == "user" else "Assistant"
        context_prompt += f"{role}: {msg['content']}\n"
    
    context_prompt += f" Current query: {query} "
    context_prompt += " Please respond to the current query with consideration of the conversation history."
    
    return context_prompt

def send_message():
    query = entry.get().strip()
    if not query:
        return
    
    # Add user message to chat history
    chat_history.append({"role": "user", "content": query})
    
    # Display user message in chat area
    chat_area.config(state=tk.NORMAL)
    chat_area.window_create(tk.END, window=create_chat_bubble(query, "user"))
    chat_area.insert(tk.END, "\n\n")
    chat_area.config(state=tk.DISABLED)
    entry.delete(0, tk.END)
    
    # Instead of modifying the ChatBot function, we'll create a contextual prompt
    if len(chat_history) > 1:  # If we have history
        contextual_query = generate_context_prompt(query)
        response = ChatBot(contextual_query)
    else:
        # If no history, just use the original query
        response = ChatBot(query)
    
    # Add AI response to chat history
    chat_history.append({"role": "assistant", "content": response})
    
    # Display AI response in chat area
    chat_area.config(state=tk.NORMAL)
    chat_area.window_create(tk.END, window=create_chat_bubble(response, "bot"))
    chat_area.insert(tk.END, "\n\n")
    chat_area.config(state=tk.DISABLED)
    chat_area.yview(tk.END)

def create_chat_bubble(text, sender):
    # Get current window width to calculate appropriate wraplength
    current_width = root.winfo_width()
    # Use a minimum width for cases when the function is called before window is fully rendered
    if current_width < 100:  # arbitrary small number
        current_width = 600  # default fallback width
    
    wrap_length = int(current_width * CHAT_WIDTH)
    
    bubble_frame = tk.Frame(chat_area, bg=USER_BG if sender == "user" else BOT_BG, bd=0, relief=tk.FLAT)
    bubble_label = tk.Label(
        bubble_frame,
        text=text,
        wraplength=wrap_length,
        justify=tk.LEFT if sender == "bot" else tk.RIGHT,
        bg=USER_BG if sender == "user" else BOT_BG,
        fg=TEXT_COLOR,
        padx=15, pady=10,
        font=("Arial", 12),
        bd=0,
        relief=tk.FLAT
    )
    bubble_label.pack(padx=10, pady=5)
    
    # Bind to configure event to update wraplength when window size changes
    def update_wraplength(event=None):
        new_width = root.winfo_width()
        if new_width > 100:  # Ignore spurious resize events
            bubble_label.config(wraplength=int(new_width * CHAT_WIDTH))
    
    root.bind("<Configure>", update_wraplength)
    
    return bubble_frame

def upload_prescription():
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp"), ("All files", "*.*")]
    )
    if file_path:
        try:
            img = Image.open(file_path)
            prescription_text = pytesseract.image_to_string(img) or "No text detected in image."
            
            # Add prescription upload to chat history
            upload_message = "I've uploaded a prescription image."
            chat_history.append({"role": "user", "content": upload_message})
            
            # Display user action in chat area
            chat_area.config(state=tk.NORMAL)
            chat_area.window_create(tk.END, window=create_chat_bubble(upload_message, "user"))
            chat_area.insert(tk.END, "\n\n")
            chat_area.config(state=tk.DISABLED)
            
            # Generate response that's aware of chat history
            if len(chat_history) > 1:
                contextual_query = f"{generate_context_prompt('Analyze this prescription.')} Prescription text: {prescription_text}"
                response = parse_prescription(prescription_text)  # Keep original parsing
            else:
                response = parse_prescription(prescription_text)
            
            # Add AI response to chat history
            chat_history.append({"role": "assistant", "content": response})
            
            # Display AI response
            chat_area.config(state=tk.NORMAL)
            chat_area.window_create(tk.END, window=create_chat_bubble(response, "bot"))
            chat_area.insert(tk.END, "\n\n")
            chat_area.config(state=tk.DISABLED)
            chat_area.yview(tk.END)
        except Exception as e:
            chat_area.config(state=tk.NORMAL)
            chat_area.insert(tk.END, f"Error processing image: {e}\n", "error")
            chat_area.config(state=tk.DISABLED)
            chat_area.yview(tk.END)

def upload_medical_image():
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp"), ("All files", "*.*")]
    )
    if file_path:
        image_base64, error = encode_image(file_path)
        if error:
            chat_area.config(state=tk.NORMAL)
            chat_area.insert(tk.END, f"{error}\n", "error")
            chat_area.config(state=tk.DISABLED)
            return

        # Add medical image upload to chat history
        upload_message = "I've uploaded a medical image for analysis."
        chat_history.append({"role": "user", "content": upload_message})
        
        # Display user action in chat area
        chat_area.config(state=tk.NORMAL)
        chat_area.window_create(tk.END, window=create_chat_bubble(upload_message, "user"))
        chat_area.insert(tk.END, "\n\n")
        chat_area.config(state=tk.DISABLED)
        
        # FIXED: Include context in the user message instead of system message
        context_text = ""
        if len(chat_history) > 2:
            # Extract recent conversation context (excluding the current upload)
            recent_msgs = chat_history[:-1]
            recent_msgs = recent_msgs[-6:] if len(recent_msgs) > 6 else recent_msgs
            context_text = "Based on our previous conversation: " + " ".join([f"{msg['role']}: {msg['content']}" for msg in recent_msgs]) + ". "
        
        prompt_text = f"{context_text}Analyze this medical image in depth. Identify all visible anatomical structures, potential abnormalities, and relevant medical findings. Compare it to normal medical standards. Explain possible conditions with causes, symptoms, and next diagnostic steps. Provide insights based on visual patterns, color variations, and any visible anomalies."
            
        chat_completion = client.chat.completions.create(
            model="llama-3.2-90b-vision-preview",
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                ]}
            ],
            max_tokens=1024
        )
        result = chat_completion.choices[0].message.content
        
        # Add AI response to chat history
        chat_history.append({"role": "assistant", "content": result})
        
        # Display AI response
        chat_area.config(state=tk.NORMAL)
        chat_area.window_create(tk.END, window=create_chat_bubble(result, "bot"))
        chat_area.insert(tk.END, "\n\n")
        chat_area.config(state=tk.DISABLED)
        chat_area.yview(tk.END)

# Function to save chat history
def save_chat():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if file_path:
        with open(file_path, "w") as file:
            for message in chat_history:
                role = "User" if message["role"] == "user" else "MediMind AI"
                file.write(f"{role}: {message['content']}\n\n")
        
        save_message = "Chat history saved successfully."
        chat_area.config(state=tk.NORMAL)
        chat_area.window_create(tk.END, window=create_chat_bubble(save_message, "bot"))
        chat_area.insert(tk.END, "\n\n")
        chat_area.config(state=tk.DISABLED)
        chat_area.yview(tk.END)

# Function to clear chat history
def clear_chat():
    global chat_history
    chat_history = []
    chat_area.config(state=tk.NORMAL)
    chat_area.delete(1.0, tk.END)
    chat_area.config(state=tk.DISABLED)
    
    # Add initial message
    welcome_message = "Chat history cleared. How can I help you today?"
    chat_area.config(state=tk.NORMAL)
    chat_area.window_create(tk.END, window=create_chat_bubble(welcome_message, "bot"))
    chat_area.insert(tk.END, "\n\n")
    chat_area.config(state=tk.DISABLED)
    chat_area.yview(tk.END)
    
    # Add welcome message to chat history
    chat_history.append({"role": "assistant", "content": welcome_message})

# Function to adjust UI for window resizing
def on_window_resize(event=None):
    window_width = root.winfo_width()
    
    # Only process legitimate resize events
    if window_width < 100:
        return
    
    # Adjust button layout based on window width
    if window_width < 700:  # For smaller screens
        # Stack buttons vertically
        entry.pack(side=tk.TOP, padx=5, pady=(0, 5), expand=True, fill=tk.X, ipady=10)
        send_button.pack(side=tk.TOP, padx=5, pady=(0, 5), fill=tk.X)
        upload_prescription_button.pack(side=tk.TOP, padx=5, pady=(0, 5), fill=tk.X)
        upload_medical_image_button.pack(side=tk.TOP, padx=5, fill=tk.X)
    else:  # For larger screens
        # Horizontal layout
        entry.pack(side=tk.LEFT, padx=(0, 5), expand=True, fill=tk.X, ipady=10)
        send_button.pack(side=tk.LEFT, padx=(0, 5))
        upload_prescription_button.pack(side=tk.LEFT, padx=(0, 5))
        upload_medical_image_button.pack(side=tk.LEFT)
    
    # Force update of all chat bubbles by recreating them
    update_all_chat_bubbles()

# Function to recreate all chat bubbles with proper wrapping
def update_all_chat_bubbles():
    if not chat_history:
        return
    
    chat_area.config(state=tk.NORMAL)
    chat_area.delete(1.0, tk.END)
    
    for message in chat_history:
        bubble = create_chat_bubble(message["content"], "user" if message["role"] == "user" else "bot")
        chat_area.window_create(tk.END, window=bubble)
        chat_area.insert(tk.END, "\n\n")
    
    chat_area.config(state=tk.DISABLED)
    chat_area.yview(tk.END)

# Function to set appropriate initial size based on screen dimensions
def set_initial_window_size():
    # Get screen dimensions
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Set initial size to 80% of screen dimensions
    width = min(int(screen_width * 0.8), 1200)  # Max width is 1200
    height = min(int(screen_height * 0.8), 800)  # Max height is 800
    
    # Set minimum size to 40% of screen or 600x400, whichever is larger
    min_width = max(int(screen_width * 0.4), 600)
    min_height = max(int(screen_height * 0.4), 400)
    
    # Apply settings
    root.geometry(f"{width}x{height}")
    root.minsize(min_width, min_height)
    
    # Center the window on screen
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    root.geometry(f"+{x}+{y}")

# Create UI
root = tk.Tk()
root.title("MediMind AI Chat")
root.configure(bg=BG_COLOR)

# Set initial window size based on screen dimensions
set_initial_window_size()

# Create and configure the chat area
chat_area = ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED, bg=BG_COLOR, fg=TEXT_COLOR, bd=0, relief=tk.FLAT)
chat_area.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)
chat_area.bind_all("<MouseWheel>", lambda event: chat_area.yview_scroll(-1*(event.delta//120), "units"))

# Menu bar for additional options
menubar = tk.Menu(root)
file_menu = tk.Menu(menubar, tearoff=0)
file_menu.add_command(label="Save Chat", command=save_chat)
file_menu.add_command(label="Clear Chat", command=clear_chat)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=file_menu)
root.config(menu=menubar)

# Create a frame for input elements that can adjust layout based on screen size
input_frame = tk.Frame(root, bg=BG_COLOR)
input_frame.pack(padx=10, pady=10, fill=tk.X)

# Create input elements
entry = tk.Entry(input_frame, bg="#333", fg=TEXT_COLOR, insertbackground=TEXT_COLOR, font=("Arial", 14), bd=0, relief=tk.FLAT)
entry.pack(side=tk.LEFT, padx=(0, 5), expand=True, fill=tk.X, ipady=10)
entry.bind("<Return>", lambda event: send_message())

def style_button(btn):
    btn.configure(bg=BUTTON_COLOR, fg=TEXT_COLOR, relief=tk.FLAT, activebackground=BUTTON_HOVER, padx=12, pady=8, bd=0, font=("Arial", 12, "bold"), cursor="hand2")
    btn.bind("<Enter>", lambda e: btn.config(bg=BUTTON_HOVER))
    btn.bind("<Leave>", lambda e: btn.config(bg=BUTTON_COLOR))

send_button = tk.Button(input_frame, text="Send", command=send_message)
style_button(send_button)
send_button.pack(side=tk.LEFT, padx=(0, 5))

upload_prescription_button = tk.Button(input_frame, text="Upload Prescription", command=upload_prescription)
style_button(upload_prescription_button)
upload_prescription_button.pack(side=tk.LEFT, padx=(0, 5))

upload_medical_image_button = tk.Button(input_frame, text="Upload Medical Image", command=upload_medical_image)
style_button(upload_medical_image_button)
upload_medical_image_button.pack(side=tk.LEFT)

# Bind the window resize event
root.bind("<Configure>", on_window_resize)

# Display welcome message
welcome_message = "Welcome to MediMind AI Chat. How can I help you today?"
chat_area.config(state=tk.NORMAL)
chat_area.window_create(tk.END, window=create_chat_bubble(welcome_message, "bot"))
chat_area.insert(tk.END, "\n\n")
chat_area.config(state=tk.DISABLED)

# Add welcome message to chat history
chat_history.append({"role": "assistant", "content": welcome_message})

# After window is fully loaded, trigger a resize event to properly layout elements
root.update()
root.after(100, on_window_resize)  # Short delay to ensure window is fully rendered

root.mainloop()