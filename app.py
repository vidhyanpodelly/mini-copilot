from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv("file.env")

app = Flask(__name__)

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    if request.method == "POST":
        prompt = request.form.get("prompt", "")
        try:
            # Try to list available models first
            try:
                models = genai.list_models()
                available_models = [model.name for model in models if 'generateContent' in model.supported_generation_methods]
                print(f"Available models: {available_models}")
            except Exception as e:
                print(f"Could not list models: {e}")
            
            # Create a model instance - use the most common model name
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Generate response
            response = model.generate_content(prompt)
            
            # Get the response text
            result = response.text
            
        except Exception as e:
            error_message = str(e)
            if "404" in error_message and "models" in error_message:
                result = "Error: Model not found. Please enable the Generative AI API at https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com"
            elif "quota" in error_message.lower() or "quota exceeded" in error_message.lower():
                result = "Error: You've exceeded your Google AI API quota. Please check your billing at https://console.cloud.google.com/billing"
            elif "invalid" in error_message.lower() and "key" in error_message.lower():
                result = "Error: Invalid Google API key. Please check your API key in the file.env file."
            elif "permission" in error_message.lower():
                result = "Error: Permission denied. Please check if the Generative AI API is enabled in your Google Cloud Console."
            else:
                result = f"Error: {error_message}"
    
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
