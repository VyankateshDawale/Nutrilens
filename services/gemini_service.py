import os
import requests
import json

def analyze_meal(meal_text):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY is not set.")
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    prompt = f"""Analyze this meal: {meal_text}
Return ONLY a JSON object with these exact keys:
calories (int), protein_g (float), carbs_g (float), fat_g (float),
fiber_g (float), sugar_g (float), meal_summary (one line string)"""

    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "response_mime_type": "application/json"
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result_json = response.json()
        
        # Extract the text and parse JSON
        text_response = result_json.get("candidates", [])[0].get("content", {}).get("parts", [])[0].get("text", "")
        return json.loads(text_response)
        
    except requests.exceptions.RequestException as e:
        print(f"API Request failed: {e}")
        return None
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"Failed to parse API response: {e}")
        return None
