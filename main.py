import re
import logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Replace with your actual bot token
TOKEN = "7718900835:AAGIrZdH5_XETNUBfV0AqhkQt0UydDvIw-I"

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌟 <b>Bot is running!</b> 🌟\n\n"
        "I automatically reformat video and PDF captions to the preferred style.\n\n"
        "<b>Supported Formats:</b>\n"
        "1. Original Video Format\n"
        "2. New Index/Title Format\n"
        "3. PDF Format",
        parse_mode='HTML'
    )

# Generate formatted caption
def create_formatted_caption(data: dict, file_type: str):
    common = (
        f"<b>📝 Title: {data.get('title', 'Untitled')}</b>\n\n"
        f"<b>📚 Batch Name: {data.get('batch', 'Unknown Batch')}</b>\n\n"
        f"<b>📥 Provided By: @itachi_xd</b>\n\n"
        f"<b>━━━━━✦ιтα¢нι✦━━━━━</b>"
    )
    if file_type == "video":
        return f"<b>🎞️ VID_ID: {data.get('id', '000')}.</b>\n\n{common}"
    else:
        return f"<b>📄 DOC_ID: {data.get('id', '000')}.</b>\n\n{common}"

# Message processor
async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = update.message or update.channel_post
        if not message or not (message.video or message.document) or not message.caption:
            return

        caption = message.caption
        data = {}
        file_type = "video" if message.video else "pdf"

        # New Format
        if "➭ Index »" in caption:
            index_match = re.search(r"➭ Index » (.+)", caption)
            title_match = re.search(r"➭ Title » \((.+?)\) (.+)", caption) or re.search(r"➭ Title » (.+)", caption)
            batch_match = re.search(r"➭ [𝐁𝐁]𝐚𝐭𝐜𝐡 » (.+)", caption)

            if index_match:
                data['id'] = index_match.group(1).strip()
            if title_match:
                if title_match.lastindex == 2:
                    data['title'] = f"{title_match.group(1)} - {title_match.group(2)}"
                else:
                    data['title'] = title_match.group(1)
            if batch_match:
                data['batch'] = batch_match.group(1).strip()

        # Original Video Format
        elif "Lecture Name ➜" in caption:
            lecture_match = re.search(r"Lecture Name ➜ (.+)\.mp4", caption)
            batch_match = re.search(r"Batch Name ➜ (.+)", caption)

            if lecture_match:
                parts = lecture_match.group(1).strip().split()
                data['id'] = parts[0] if parts else "000"
                data['title'] = ' '.join(parts[1:]).title() if len(parts) > 1 else "Untitled"
            if batch_match:
                data['batch'] = batch_match.group(1).strip()

        # PDF Format
        elif "Name »" in caption:
            name_match = re.search(r"Name » (.+)\.pdf", caption)
            batch_match = re.search(r"Batch » (.+)", caption)

            if name_match:
                parts = name_match.group(1).strip().split()
                data['id'] = parts[0] if parts else "000"
                data['title'] = ' '.join(parts[1:]).title() if len(parts) > 1 else "Untitled"
            if batch_match:
                data['batch'] = batch_match.group(1).strip()

        # If parsed, replace caption
        if data:
            new_caption = create_formatted_caption(data, file_type)
            await context.bot.edit_message_caption(
                chat_id=message.chat_id,
                message_id=message.message_id,
                caption=new_caption,
                parse_mode='HTML'
            )

    except Exception as e:
        logger.exception("Error while processing message")

# Main runner
def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(
        (filters.VIDEO | filters.Document.PDF) & filters.Caption()
        & (filters.ChatType.PRIVATE | filters.ChatType.CHANNEL),
        process_message
    ))

    logger.info("Bot started!")
    application.run_polling()

if __name__ == '__main__':
    main()
