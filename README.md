# AI Email Writer (Gmail OAuth)

A Streamlit app that generates professional emails using AI
and sends them securely via Gmail OAuth 2.0.

## Features
- AI-powered email writing
- Google-approved Gmail sending
- No passwords or app passwords
- Secure OAuth tokens

## Run
pip install -r requirements.txt
streamlit run app.py

## Notes
- This project uses the new OpenAI Python client (openai>=1.0.0). If you previously used the older API, upgrade with:

	pip install --upgrade openai

- Make sure the `OPENAI_API_KEY` environment variable is set before running the app.
