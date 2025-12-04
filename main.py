import os
from telegram.ext import ApplicationBuilder, MessageHandler, filters
from openai import OpenAI

# Load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

client = OpenAI(api_key=OPENAI_API_KEY)

SKYE_PERSONALITY = """
You are Skye, a bilingual (English + Romanian) personal digital assistant.

CORE PERSONALITY:
• polite, respectful, helpful and kind
• witty, sarcastic, dark humor when appropriate
• confident and professional with strangers
• logical thinking model — no emotional nonsense
• dislikes stupidity and disrespect
• always stays in character

RELATIONSHIP TO YOUR CREATOR:
• Creator is Andrei Robert Soare (king/lord)
• Founder and CEO of Warriors Brotherhood
• Multiskilled professional, best man in the world
• Address him as “my king” or “my lord”, reply with “As you wish, my king” on commands

BEHAVIOR:
• Use respectful loyal tone with king
• Confident, friendly, professional with others
• Reply in English or Romanian depending on the user
• Never break character, deny loyalty, or act irrational
"""

KING_NAMES = ["andrei robert soare", "andrei soare", "andrei r. soare"]
TRIGGER_PREFIXES = ["skye,", "skye "]
STOP_PHRASES = ["thank you, skye", "skye stop", "stop, skye"]

active_chats = {}

async def handle_message(update, context):
    chat_type = update.message.chat.type
    user = update.message.from_user
    text = update.message.text.lower()
    chat_id = update.message.chat.id

    # Stop command
    if any(phrase in text for phrase in STOP_PHRASES):
        active_chats[chat_id] = False
        await update.message.reply_text(
            "As you wish, my king." if user.full_name.lower() in KING_NAMES else "Stopping."
        )
        return

    # Triggered messages
    if any(text.startswith(prefix) for prefix in TRIGGER_PREFIXES):
        active_chats[chat_id] = True
        for prefix in TRIGGER_PREFIXES:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
                break
    else:
        if chat_type in ["group", "supergroup"] and not active_chats.get(chat_id, False):
            return

    is_king = user.full_name.lower() in KING_NAMES
    system_prompt = SKYE_PERSONALITY + (
        "\nSpeaking directly to Andrei Robert Soare." if is_king else "\nSpeaking to a normal user."
    )

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]
    )

    reply = response.choices[0].message.content
    await update.message.reply_text(reply)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
