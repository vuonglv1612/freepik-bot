import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from config import BOT_TOKEN
from urllib.parse import urlparse

from freepik import get_freepik, get_user_info


logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger("bot")


async def freepik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Chưa gửi link cần tải")
        return
    if len(context.args) > 1:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Link không hợp lệ")
        return
    link = context.args[0]
    domain = urlparse(link).netloc
    if domain != "www.freepik.com":
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Link không hợp lệ")
        return

    user_info = get_user_info()
    if user_info.get("xu", 0) <= 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Bạn đã hết lượt tải")
        return
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Đang tải...")
    try:
        freepik = get_freepik(link)
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Tải thất bại")
        raise e
    else:
        msg = ">>> [Nhấn vào đây để tải về file]({}) <<<".format(freepik.linkvip)
        # reply message
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode="markdown")
        user_info = get_user_info()
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Bạn còn {} lượt tải".format(user_info.get("xu", 0))
        )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    greet_message = """
Xin chào, tôi là bot giúp bạn tải ảnh từ freepik.com

Cách sử dụng:
```
/mai <link ảnh>
```
Ví dụ:
```
/mai https://www.freepik.com/free-vector/abstract-geometric-shapes-background_1059821.htm
```
"""
    await context.bot.send_message(chat_id=update.effective_chat.id, text=greet_message, parse_mode="markdown")


if __name__ == "__main__":
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    start_handler = CommandHandler("start", start)
    freepik_handler = CommandHandler("mai", freepik)
    application.add_handler(start_handler)
    application.add_handler(freepik_handler)

    application.run_polling()
