import requests
import json
from config import GEMINI_API_KEY

def generate_filename(prompt: str) -> str:
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{
                "parts": [{
                    "text": f"Generate a short, lowercase, underscore_separated, English-only filename for: {prompt}. No punctuation, no special characters, only ASCII letters."
                }]
            }]
        }

        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        filename = result['candidates'][0]['content']['parts'][0]['text'].strip()
        return filename
    except Exception as e:
        print(f"❌ Gemini hata: {e}")
        return "dosya_adi_bulunamadi"
