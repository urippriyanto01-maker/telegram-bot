import os
import yt_dlp

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

TOKEN = "8659403003:AAFdsMj9oTAUo4gTCKKPHq7r7blreNnWlUw"

# SIMPAN URL USER
user_urls = {}

# PAS USER KIRIM LINK
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text
    user_id = update.message.from_user.id

    user_urls[user_id] = url

    keyboard = [
        [
            InlineKeyboardButton("🎥 Video", callback_data="video"),
            InlineKeyboardButton("🎵 MP3", callback_data="mp3")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Pilih format download:",
        reply_markup=reply_markup
    )

# PAS TOMBOL DIKLIK
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    url = user_urls.get(user_id)

    if not url:
        await query.message.reply_text("URL tidak ditemukan")
        return

    mode = query.data

    await query.message.reply_text("⏳ Lagi download...")

    try:

        # VIDEO
        if mode == "video":

            ydl_opts = {
                "format": "best[height<=480]",
                "outtmpl": "%(title)s.%(ext)s"
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file = ydl.prepare_filename(info)

            with open(file, "rb") as f:
                await query.message.reply_video(f)

        # MP3
        else:

            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": "%(title)s.%(ext)s",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }]
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file = ydl.prepare_filename(info)

                file = os.path.splitext(file)[0] + ".mp3"

            with open(file, "rb") as f:
                await query.message.reply_audio(f)

        os.remove(file)

    except Exception as e:
        await query.message.reply_text(f"Error:\n{e}")

# START BOT
app = Application.builder().token(TOKEN).build()

app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
)

app.add_handler(
    CallbackQueryHandler(button_handler)
)

print("🚀 Bot aktif")

app.run_polling()