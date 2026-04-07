import os
import datetime
import re
from flask import Flask, render_template, request, make_response
from dotenv import load_dotenv
from google.cloud import firestore

from services.gemini_service import analyze_meal
from services.claude_service import get_health_advice, get_weekly_insight

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Initialize Firestore using GOOGLE_APPLICATION_CREDENTIALS safely
db = None
if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
    try:
        db = firestore.Client()
        print("Firestore client initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize Firestore: {e}")
else:
    print("Warning: GOOGLE_APPLICATION_CREDENTIALS not found in environment.")

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST', 'GET'])
def analyze():
    if request.method == 'POST':
        raw_description = request.form.get('meal_description', '')
        
        # Security: Strip HTML tags and limit length
        clean_description = re.sub(r'<[^>]+>', '', raw_description)
        meal_description = clean_description[:500].strip()
        
        if not meal_description:
            return "Error: Invalid or empty meal description.", 400
            
        calorie_goal = request.form.get('calorie_goal', '')
        protein_goal = request.form.get('protein_goal', '')
        water_goal = request.form.get('water_goal', '')
        
        user_goals_string = f"Calories: {calorie_goal}, Protein: {protein_goal}g, Water: {water_goal}L"
        # Type conversions for Firestore dictionary
        user_goals_dict = {
            "calories": int(calorie_goal) if calorie_goal.isdigit() else calorie_goal,
            "protein": int(protein_goal) if protein_goal.isdigit() else protein_goal,
            "water": float(water_goal) if water_goal.replace('.', '', 1).isdigit() else water_goal
        }
        
        # 1. Analyze nutrition with Gemini
        nutrition_data = analyze_meal(meal_description)
        if not nutrition_data:
            nutrition_data = {"error": "Failed to analyze meal."}
        
        # 2. Get Coaching advice with Claude
        advice = get_health_advice(nutrition_data, user_goals_string)
        
        # 3. Save to Firestore gracefully
        db_log_entry = {
            "meal_text": meal_description,
            "nutrition": nutrition_data,
            "health_advice": advice,
            "user_goals": user_goals_dict,
            "timestamp": firestore.SERVER_TIMESTAMP
        }
        
        if db:
            try:
                db.collection("meal_logs").add(db_log_entry)
            except Exception as e:
                print(f"Firestore save error: {e}")
        
        # Remap for local UI templates to prevent breaking the view model
        ui_log_entry = {
            "meal_description": meal_description,
            "calorie_goal": calorie_goal,
            "user_goals": user_goals_string,
            "nutrition_data": nutrition_data,
            "advice": advice,
            "timestamp": datetime.datetime.now(datetime.timezone.utc)
        }
        
        return render_template('result.html', data=ui_log_entry)
        
    return render_template('index.html')

@app.route('/history')
def history():
    meal_history = []
    if db:
        try:
            docs = db.collection("meal_logs").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(7).stream()
            for doc in docs:
                db_data = doc.to_dict()
                
                # Transform the DB schema back to UI expectation
                goals = db_data.get('user_goals', {})
                if isinstance(goals, dict):
                    goals_string = f"Calories: {goals.get('calories')}, Protein: {goals.get('protein')}g, Water: {goals.get('water')}L"
                else:
                    goals_string = str(goals)
                
                ts = db_data.get('timestamp')
                # Avoid crashing strftime if firestore server timestamp isn't loaded correctly
                if not ts:
                    ts = datetime.datetime.now(datetime.timezone.utc)
                    
                meal_history.append({
                    "meal_description": db_data.get('meal_text', ''),
                    "user_goals": goals_string,
                    "nutrition_data": db_data.get('nutrition', {}),
                    "advice": db_data.get('health_advice', ''),
                    "timestamp": ts
                })
        except Exception as e:
            print(f"Firestore read error: {e}")
            
    weekly_insight = get_weekly_insight(meal_history) if meal_history else "No history available to analyze."
    
    return render_template('history.html', meal_history=meal_history, insight=weekly_insight)

if __name__ == '__main__':
    app.run(debug=True)
