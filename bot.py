import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
data = {
    "model": "llama3-70b-8192",
    "messages": [
        {"role": "user", "content": user_text}
    ],
    "temperature": 0.7,
    "max_tokens": 512
}

    r = requests.post(url, headers=headers, json=data)

    if r.status_code != 200:
        reply = f"错误代码: {r.status_code} 内容: {r.text}"
    else:
        result = r.json()
        try:
            reply = result["choices"][0]["message"]["content"]
        except:
            reply = str(result)

    await update.message.reply_text(reply)


app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT, handle))

app.run_polling()
