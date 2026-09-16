# 🔍 AI Code Review Agent

A Streamlit app for AI-powered code review using the Groq API.


---

## ✨ Features

✅ **AI-powered code analysis** powered by Groq AI
🔒 **Security vulnerability detection**
🐛 **Bug identification and fixes**
⚡ **Performance optimization tips**
💾 **Review history tracking**
📥 **Export reviews**
💬 **Chat assistant for follow-up questions**

---

## 🎯 Supported Languages

• Python • JavaScript • Java • C/C++ • Go • Rust • PHP • Ruby

---

## 🚀 Setup (Local)

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

---

## 📦 GitHub Deployment

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

---

## 🔐 Keeping the API Key Secret

- Never upload `.env`
- Use `.env.example` for the repo instead
- On Streamlit Cloud or other hosts, set `GROQ_API_KEY` as an environment secret, not in source code

---

## 🌐 Streamlit Cloud Deployment

- Push your repo to GitHub
- Create a new app on Streamlit Cloud
- Set the main file to `app.py`
- Add a secret named `GROQ_API_KEY`
- Deploy

---

## 📚 How to Use

1. **Paste your code** in the left box
2. **Click "Analyze"** to get AI review
3. **View improved code** on the right
4. **Copy & use** the corrected code
5. **Chat with AI** for follow-up questions

---

## 🛠️ Technologies Used

- **Streamlit** - Web app framework
- **Groq API** - AI-powered code analysis
- **Python** - Backend
- **Python-dotenv** - Environment variables

---

## 📝 License

This project is open source and available for educational and commercial use.

---

## 👤 Author

**Shainaz361**

---

## 🤝 Contributing

Contributions are welcome! Feel free to fork and submit pull requests.

---

## 📞 Support

For issues or questions, please open an GitHub issue or contact the author.

---

**Made with ❤️ using Groq AI**
