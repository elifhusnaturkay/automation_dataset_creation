import requests
from config import GEMINI_API_KEY

def generate_filename(prompt: str) -> str:
    try:
        response = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
            params={"key": GEMINI_API_KEY},
            json={
                "contents": [
                    {
                        "parts": [{"text": f"Create a short, lowercase, underscore_separated, English-only ASCII but Turkish filename for: {prompt}. Do not add extension."}]
                    }
                ]
            }
        )
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print(f"❌ Gemini hata: {e}")
        return "dosya_adi_bulunamadi"
