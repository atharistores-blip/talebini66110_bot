import logging
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, ContextTypes, filters

BOT_TOKEN = "8834601896:AAFm7nsNDmt0RI23YJWD4j_qBELiWVswZQQ"
OWNER_CHAT_ID = 31667723

ABJAD_TABLE = {
    'ا': 1, 'ب': 2, 'ج': 3, 'د': 4, 'ه': 5, 'و': 6, 'ز': 7, 'ح': 8, 'ط': 9,
    'ی': 10, 'ک': 20, 'ل': 30, 'م': 40, 'ن': 50, 'س': 60, 'ع': 70, 'ف': 80, 'ص': 90,
    'ق': 100, 'ر': 200, 'ش': 300, 'ت': 400, 'ث': 500, 'خ': 600, 'ذ': 700, 'ض': 800, 'ظ': 900, 'غ': 1000,
    'پ': 0, 'چ': 0, 'ژ': 0, 'گ': 0
}


def abjad_value(text: str) -> int:
    text = text.strip().replace(' ', '').replace('ي', 'ی').replace('ك', 'ک')
    total = 0
    for char in text:
        total += ABJAD_TABLE.get(char, 0)
    return total


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

G_NAME, G_MOTHER, B_NAME, B_MOTHER = range(4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "سلام! 🌟\n\nبه ربات طالع‌بینی ازدواج با حروف ابجد خوش آمدی.\n\n"
        "لطفاً نام کوچک دختر را وارد کن:",
        reply_markup=ReplyKeyboardRemove()
    )
    return G_NAME


async def get_girl_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['girl_name'] = update.message.text.strip()
    await update.message.reply_text("عالی! حالا نام مادر دختر را وارد کن:")
    return G_MOTHER


async def get_girl_mother(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['girl_mother'] = update.message.text.strip()
    await update.message.reply_text("حالا نام کوچک پسر را وارد کن:")
    return B_NAME


async def get_boy_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['boy_name'] = update.message.text.strip()
    await update.message.reply_text("و در آخر، نام مادر پسر را وارد کن:")
    return B_MOTHER


async def calculate_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    boy_mother = update.message.text.strip()
    data = context.user_data

    girl_total = abjad_value(data['girl_name']) + abjad_value(data['girl_mother'])
    boy_total = abjad_value(data['boy_name']) + abjad_value(boy_mother)
    total_sum = girl_total + boy_total
    remainder = total_sum % 5

    if remainder in (1, 3):
        result_text = "💚 سازگاری کامل!\nستاره‌های شما با هم جفت است و زندگی خوبی خواهید داشت."
    elif remainder in (2, 4):
        result_text = "💔 عدم سازگاری\nستاره‌های شما با هم جفت نیست و احتمال جدایی وجود دارد."
    else:
        result_text = "🤔 نتیجه نامشخص\nمحاسبه دقیقاً بر ۵ بخش‌پذیر شد."

    report = (
        f"📊 نتیجه محاسبات ابجد\n\n"
        f"👧 دختر: {data['girl_name']} {data['girl_mother']}\n"
        f"👦 پسر: {data['boy_name']} {boy_mother}\n\n"
        f"🔢 مجموع ابجد کل: {total_sum}\n"
        f"➗ باقی‌مانده تقسیم بر ۵: {remainder}\n\n"
        f"{result_text}"
    )

    await update.message.reply_text(report)
    try:
        await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=report)
    except Exception as e:
        logger.error(f"خطا در ارسال به مالک: {e}")

    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text("لغو شد. برای شروع دوباره /start را بزنید.")
    return ConversationHandler.END


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            G_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_girl_name)],
            G_MOTHER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_girl_mother)],
            B_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_boy_name)],
            B_MOTHER: [MessageHandler(filters.TEXT & ~filters.COMMAND, calculate_and_send)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv_handler)
    print("🤖 ربات ابجد روشن شد...")
    app.run_polling()


if __name__ == "__main__":
    main()
