import os
from telegram.ext import ApplicationBuilder, MessageHandler, filters
from openai import OpenAI

# Load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

client = OpenAI(api_key=OPENAI_API_KEY)

# Skye personality and behavior
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

# Recognized king names
KING_NAMES = ["andrei robert soare", "andrei soare", "andrei r. soare"]

# Triggers and stop phrases
TRIGGER_PREFIXES = ["skye,", "skye "]
STOP_PHRASES = ["thank you, skye", "skye stop", "stop, skye"]

# Active chat states
active_chats = {}

async def handle_message(update, context):
    chat_type = update.message.chat.type
    user = update.message.from_user
    user_text = update.message.text.lower()
    chat_id = update.message.chat.id

    # Stop Skye if stop phrase detected
    if any(phrase in user_text for phrase in STOP_PHRASES):
        active_chats[chat_id] = False
        await update.message.reply_text(
            "As you wish, my king." if user.full_name.lower() in KING_NAMES else "Okay, stopping."
        )
        return

    # Activate Skye if called
    if any(user_text.startswith(prefix) for prefix in TRIGGER_PREFIXES):
        active_chats[chat_id] = True
        for prefix in TRIGGER_PREFIXES:
            if user_text.startswith(prefix):
                user_text = user_text[len(prefix):].strip()
                break
    else:
        # In group chats, ignore messages if not active
        if chat_type in ["group", "supergroup"] and not active_chats.get(chat_id, False):
            return

    # Detect king
    is_king = user.full_name.lower() in KING_NAMES
    system_prompt = SKYE_PERSONALITY + (
        "\nYou are now speaking directly to Andrei Robert Soare." if is_king else "\nYou are now speaking to a non-Andrei user."
    )

    # Generate AI response
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ]
    )

    bot_reply = response.choices[0].message.content
    await update.message.reply_text(bot_reply)

def main():
    # Create the bot application
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Add a message handler for text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot (async polling)
    app.run_polling()

if name == "main":
    main()