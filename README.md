# NutriLens

NutriLens is an AI-powered nutritional analysis tool powered by a dual-AI architecture. It utilizes **Gemini 1.5** to perform fast, highly-accurate macro and nutritional extraction directly from unstructured meal descriptions. It then hands this data off securely to **Claude Opus** to naturally operate as a personalized health coach—yielding uniquely tailored, contextual health advice against personal daily goals.

## Architecture

```text
+-------------------+       +-----------------------+
|   User Input      | ----> |     NutriLens App     |
| (Meal & Goals)    |       |   (Flask Backend)     |
+-------------------+       +-----------------------+
                                |               |
         +----------------------+               +-----------------------+
         |                                                              |
         v                                                              v
+-------------------+                                           +-------------------+
|  Gemini 1.5 API   |                                           |  Claude Opus 4.5  |
| (Nutrition Macro  |                                           | (Personal Health  |
|    Extraction)    |                                           |      Coach)       |
+-------------------+                                           +-------------------+
         |                                                              |
         +----------------------+               +-----------------------+
                                |               |
                                v               v
                            +-----------------------+
                            |   Firestore Database  |
                            |     (Meal Logs)       |
                            +-----------------------+
```

## Setup & Running Locally

1. Set up a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, utilize `.\venv\Scripts\activate`
   ```

2. Install dependencies: 
   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and fill in your active API keys:
   ```bash
   copy .env.example .env
   ```

4. Run the application:
   ```bash
   python app.py
   ```
   Navigate to `http://127.0.0.1:5000` to begin interacting with the AI health coach.

## Testing

NutriLens implements automated routing and integration unit tests via Python's built-in `unittest` mock injection.

1. Ensure your active environment matches development:
   ```bash
   python -m unittest test_app.py
   ```
