from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters

TOKEN = "8438241153:AAFBpkWysLkcdCha9ymVMo4cdkmrAaL0NiY"

COURSE = [
    {
        "level": "A1",
        "title": "Basics",
        "lessons": [
            {
                "title": "Lesson 1 — Sentence Order (SOV)",
                "teach": "Azerbaijani often uses: Subject + Object + Verb (verb at the end).\n\nExample:\nMən kitab oxuyuram. (I am reading a book.)",
                "practice": [
                    ("I drink tea.", "Mən çay içirəm."),
                    ("I read a book.", "Mən kitab oxuyuram."),
                    ("I watch TV.", "Mən TV-yə baxıram.")
                ],
            },
            {
                "title": "Lesson 2 — Personal Pronouns",
                "teach": "Pronouns:\nMən = I\nSən = you (singular)\nO = he/she/it\nBiz = we\nSiz = you (plural/polite)\nOnlar = they",
                "practice": [
                    ("We drink tea.", "Biz çay içirik."),
                    ("They read.", "Onlar oxuyurlar."),
                ],
            },
            {
                "title": "Lesson 3 — Present Tense (very basic)",
                "teach": "Present tense examples:\n-iRam / -irəm (I)\n-irsən (you)\n-ir (he/she)\n\nExample:\nMən gəlirəm. (I am coming.)\nSən gəlirsən. (You are coming.)\nO gəlir. (He/She is coming.)",
                "practice": [
                    ("I come.", "Mən gəlirəm."),
                    ("You come.", "Sən gəlirsən."),
                    ("He comes.", "O gəlir."),
                ],
            },
        ],
    }
]

# user progress memory (in RAM; resets if PC restarts)
USER_STATE = {}

def get_state(user_id: int):
    if user_id not in USER_STATE:
        USER_STATE[user_id] = {"level": 0, "lesson": 0, "mode": "teach"}  # mode: teach/practice
    return USER_STATE[user_id]

def lesson_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Back", callback_data="back"),
         InlineKeyboardButton("Next ➡️", callback_data="next")],
        [InlineKeyboardButton("📝 Practice", callback_data="practice"),
         InlineKeyboardButton("📘 Teach", callback_data="teach")],
        [InlineKeyboardButton("🏠 Course", callback_data="course")]
    ])

async def show_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    s = get_state(user_id)
    level = COURSE[s["level"]]
    lesson = level["lessons"][s["lesson"]]

    if s["mode"] == "teach":
        text = f"📘 {level['level']} — {lesson['title']}\n\n{lesson['teach']}"
    else:
        # show 1 practice item based on a counter
        p_index = s.get("p_index", 0) % len(lesson["practice"])
        q, a = lesson["practice"][p_index]
        text = (
            f"📝 Practice — {lesson['title']}\n\n"
            f"Translate:\n{q}\n\n"
            f"Reply with your answer.\n"
            f"(Tip: type /answer to reveal)"
        )
        s["current_answer"] = a
        s["current_question"] = q

    # send
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=lesson_keyboard())
    else:
        await update.message.reply_text(text, reply_markup=lesson_keyboard())

async def course_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    s = get_state(user_id)
    level = COURSE[s["level"]]
    lesson = level["lessons"][s["lesson"]]
    await update.message.reply_text(
        f"🏠 Course\n\nCurrent: {level['level']} — {lesson['title']}\n\n"
        "Use buttons: Next / Back\n"
        "Or type: /lesson to continue."
    )

async def lesson_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await show_lesson(update, context, user_id)

async def answer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    s = get_state(user_id)
    ans = s.get("current_answer")
    if not ans:
        await update.message.reply_text("No active practice question. Tap 📝 Practice first.")
        return
    await update.message.reply_text(f"✅ Suggested answer:\n{ans}")

async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    s = get_state(user_id)
    level = COURSE[s["level"]]
    lessons = level["lessons"]

    if query.data == "next":
        s["lesson"] = (s["lesson"] + 1) % len(lessons)
        s["p_index"] = 0
    elif query.data == "back":
        s["lesson"] = (s["lesson"] - 1) % len(lessons)
        s["p_index"] = 0
    elif query.data == "practice":
        s["mode"] = "practice"
        s["p_index"] = s.get("p_index", 0)
    elif query.data == "teach":
        s["mode"] = "teach"
    elif query.data == "course":
        await query.edit_message_text("Type /course to see your course home.")
        return

    await show_lesson(update, context, user_id)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salam! 🇦🇿\n\n"
        "I am your Azerbaijani grammar-first teacher.\n\n"
        "Available commands:\n"
        "/grammar – Grammar lesson\n"
        "/verbs – Verb basics\n"
        "/practice – Practice exercises\n"
        "/help – How to study\n"
    )


async def grammar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📘 GRAMMAR LESSON 1\n\n"
        "Azerbaijani sentence order:\n"
        "Subject + Object + Verb\n\n"
        "Example:\n"
        "Mən kitab oxuyuram.\n"
        "(I am reading a book.)\n\n"
        "The verb comes at the end."
    )


async def verbs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔤 VERB BASICS\n\n"
        "Verb: getmək (to go)\n\n"
        "Mən gedirəm – I go\n"
        "Sən gedirsən – You go\n"
        "O gedir – He/She goes"
    )


async def practice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✍️ PRACTICE\n\n"
        "Translate to Azerbaijani:\n"
        "I am reading a book.\n\n"
        "Answer:\n"
        "Mən kitab oxuyuram."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 HOW TO STUDY\n\n"
        "1️⃣ Start with /grammar\n"
        "2️⃣ Learn verbs using /verbs\n"
        "3️⃣ Practice daily with /practice\n\n"
        "Study slowly and carefully."
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    s = get_state(user_id)
    text = (update.message.text or "").strip().lower()

    # Natural navigation
    if text in ["next", "another", "another please", "continue", "more", "again"]:
        level = COURSE[s["level"]]
        s["lesson"] = (s["lesson"] + 1) % len(level["lessons"])
        s["mode"] = "teach"
        await show_lesson(update, context, user_id)
        return

    if text in ["back", "previous"]:
        level = COURSE[s["level"]]
        s["lesson"] = (s["lesson"] - 1) % len(level["lessons"])
        s["mode"] = "teach"
        await show_lesson(update, context, user_id)
        return

    # Practice answer checking
    if s.get("mode") == "practice" and s.get("current_answer"):
        correct = s["current_answer"].lower()
        user_ans = text.lower()

        if user_ans == correct:
            await update.message.reply_text("✅ Correct. Tap Next ➡️ for the next lesson or 📝 Practice again.")
        else:
            await update.message.reply_text(
                "Not quite.\n\n"
                f"Your answer: {update.message.text}\n"
                f"Suggested: {s['current_answer']}\n\n"
                "Try another one: tap 📝 Practice."
            )
        return

    # Default guidance
    await update.message.reply_text(
        "Use:\n"
        "/course — course home\n"
        "/lesson — continue lesson\n"
        "Or tap Next ➡️ / 📝 Practice buttons."
    )

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("grammar", grammar))
app.add_handler(CommandHandler("verbs", verbs))
app.add_handler(CommandHandler("practice", practice))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(CommandHandler("course", course_command))
app.add_handler(CommandHandler("lesson", lesson_command))
app.add_handler(CommandHandler("answer", answer_command))

app.add_handler(CallbackQueryHandler(on_button))

print("Bot is running...")
app.run_polling()
worker: python bot.py
python-telegram-bot==20.7
