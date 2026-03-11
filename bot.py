import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# 读取 Skill
with open("./Skill.md", "r", encoding="utf-8") as f:
    system_prompt = f.read()

# 简单对话记忆
memory = {}

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message or not update.message.text:
        return

    user_id = update.message.chat_id
    user_text = update.message.text

    if user_id not in memory:
        memory[user_id] = []

    memory[user_id].append({
        "role": "user",
        "content": user_text
    })

    messages = [{"role": "system", "content": system_prompt}]
    messages += memory[user_id][-10:]   # 保留最近10轮

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 512
    }

    try:

        r = requests.post(url, headers=headers, json=data)

        if r.status_code != 200:
            reply = f"API错误 {r.status_code}\n{r.text}"
        else:
            result = r.json()
            reply = result["choices"][0]["message"]["content"]

            memory[user_id].append({
                "role": "assistant",
                "content": reply
            })

    except Exception as e:
        reply = f"系统错误: {str(e)}"

    await update.message.reply_text(reply)


app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

print("Bot running...")

app.run_polling()
