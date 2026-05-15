# Code Review Agent

A Streamlit app for AI-powered code review using the Groq API.

## Setup (Local)

1. Create a Python virtual environment and activate it:

```powershell
cd C:\Users\shain\OneDrive\Desktop\Code-Review-Agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and add your API key:

```powershell
copy .env.example .env
```

Then edit `.env` and replace `your_groq_api_key_here` with your real key.

> Do not commit `.env` to GitHub. `.gitignore` is configured to exclude it.

4. Run the app:

```powershell
python -m streamlit run app.py
```

## GitHub deployment

1. Initialize the repository:

```powershell
git init
git add .
git commit -m "Initial commit"
```

2. Create a new GitHub repo on github.com.
3. Add the GitHub remote and push:

```powershell
git remote add origin https://github.com/<your-username>/<repo-name>.git
git branch -M main
git push -u origin main
```

## Keeping the API key secret

- Never upload `.env`
- Use `.env.example` for the repo instead
- On Streamlit Cloud or other hosts, set `GROQ_API_KEY` as an environment secret, not in source code

## Optional Streamlit Cloud deploy

- Push your repo to GitHub
- Create a new app on Streamlit Cloud
- Set the main file to `app.py`
- Add a secret named `GROQ_API_KEY`
- Deploy
