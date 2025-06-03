import os
import logging
from uuid import uuid4
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, Filter
from aiogram.types import FSInputFile, InlineQueryResultVoice, InlineQueryResultCachedVoice, InlineQueryResultArticle
from aiogram.exceptions import TelegramBadRequest
from elevenlabs.client import ElevenLabs
import tempfile
import asyncio
import json

# Load environment variables
load_dotenv()

# Get API keys from environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Dictionary to store the voice chosen by each user
with open("voices.json", "r") as f:
    voices = json.load(f)

if not voices or not isinstance(voices, list):
    print("No voices found in voices.json. Please add voices to the file.")

default_voice = voices[0]["id"]
user_voices = {}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_command(message: types.Message):
    logger.info(f"User {message.from_user.id} started the bot")
    await message.reply("Hello! Use the inline query to generate voice messages, or send a message to generate a voice message. Telegram text lenght input limits: for inline query: 256 symbols, and for the messages: 3000 symbols.")

@dp.message(Command("voice"))
async def voice_command(message: types.Message):
    logger.info(f"User {message.from_user.id} requested voice selection")
    await choose_voice(message)

async def choose_voice(message: types.Message):
    logger.info(f"Presenting voice options to user {message.from_user.id}")
    voice_names = [voice["name"] for voice in voices]
    keyboard = [[types.KeyboardButton(text=name) for name in voice_names[i:i+2]] for i in range(0, len(voice_names), 2)]
    reply_markup = types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)
    await message.reply("Please choose a voice:", reply_markup=reply_markup)

async def voice_chosen(message: types.Message):
    user_id = message.from_user.id
    chosen_voice = message.text
    logger.info(f"User {user_id} chose voice: {chosen_voice}")
    for voice in voices:
        if voice["name"] == chosen_voice:
            user_voices[user_id] = voice["id"]
            await message.reply(f"Voice set to {chosen_voice}.", reply_markup=types.ReplyKeyboardRemove())
            return
    await message.reply("Invalid voice choice. Please try again.")

@dp.inline_query()
async def inline_query_handler(query: types.InlineQuery):

    if not query.query:
        return

    logger.info(f"Inline query from user {query.from_user.id}: {query.query}")
    
    user_id = query.from_user.id
    voice_id = user_voices.get(user_id, default_voice)
    logger.info(f"Generating voice message for user {user_id} with voice {voice_id}: {query.query}")

    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    audio_stream = client.text_to_speech.convert(
        text=query.query,
        voice_id=voice_id,
        model_id="eleven_multilingual_v2"
    )

    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        for chunk in audio_stream:
            temp_audio.write(chunk)
        temp_audio_path = temp_audio.name

    try:
        # Upload the voice message to Telegram
        voice_message = await bot.send_voice(
            chat_id=query.from_user.id,
            voice=FSInputFile(temp_audio_path),
            caption=query.query
        )
        file_id = voice_message.voice.file_id

        # Create an InlineQueryResultVoice object
        results = [
            InlineQueryResultCachedVoice(
                id=str(uuid4()),
                title="Voice message by @voicy_gg_bot",
                voice_file_id=file_id,
                caption=f"" # If need a caption, add {query.query}
            )
        ]

        # Clean up the temporary file after the query is answered
        async def cleanup():
            await asyncio.sleep(5)  # Wait for 60 seconds before deleting the file
            os.unlink(temp_audio_path)
            await voice_message.delete()

        asyncio.create_task(cleanup())

        logger.info(f"Voice message sent to user {user_id}")

        await query.answer(results)
    except TelegramBadRequest as e:
        if "VOICE_MESSAGES_FORBIDDEN" in str(e):
            results = [
            InlineQueryResultArticle(
                id=str(uuid4()),
                title="Voice messages are disabled in your privacy settings",
                input_message_content=types.InputTextMessageContent(
                        message_text="Please enable voice messages in your privacy settings to use this bot."
                    )
                )
            ]
            await query.answer(results)
        else:
            raise

@dp.chosen_inline_result()
async def chosen_inline_result_handler(chosen_result: types.ChosenInlineResult):
    logger.info(f"Chosen inline result: {chosen_result.result_id}")

@dp.message()
async def handle_text_message(message: types.Message):
    if message.text in [voice["name"] for voice in voices]:
        await voice_chosen(message)
        return
    
    if message.text is None:
        return
    
    # Check if the message is in a group and not mentioning the bot
    if message.chat.type in ['group', 'supergroup'] and not message.text.startswith(f"@{(await bot.me()).username}"):
        return  # Ignore messages in groups that don't mention the bot

    # Remove the bot's username from the message text if it's mentioned
    if message.text.startswith(f"@{(await bot.me()).username}"):
        text = message.text.replace(f"@{(await bot.me()).username}", "").strip()
    else:
        text = message.text
    
    # If the message is empty after removing the mention, ignore it
    if not text:
        return

    text = message.text
    user_id = message.from_user.id
    voice_id = user_voices.get(user_id, default_voice)
    logger.info(f"Generating voice message for user {user_id} with voice {voice_id}: {text}")

    # Send a "processing" message
    processing_message = await message.reply("Generating voice message...")

    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    audio_stream = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id="eleven_multilingual_v2"
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        for chunk in audio_stream:
            temp_audio.write(chunk)
        temp_audio_path = temp_audio.name

    
    # Send the voice message
    try:
        await bot.send_voice(
            chat_id=message.chat.id,
            voice=FSInputFile(temp_audio_path),
            caption=f"{text}"
        )
    except TelegramBadRequest as e:
        if "VOICE_MESSAGES_FORBIDDEN" in str(e):
            await message.reply("Your private settings do not allow me to send voice messages.")
        else:
            raise  # Re-raise the exception if it's not the specific error we're handling

    logger.info(f"Voice message sent to user {user_id}")

    # Delete the temporary file
    os.unlink(temp_audio_path)

    # Delete the "processing" message
    await processing_message.delete()

async def main():
    if not TELEGRAM_BOT_TOKEN or not ELEVENLABS_API_KEY:
        logger.error("Missing API keys. Please check your .env file.")
        return

    logger.info("Starting the bot")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
