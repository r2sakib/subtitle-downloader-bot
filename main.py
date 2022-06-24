from telebot import TeleBot, types
import shutil
import os
from dotenv import load_dotenv
from subtitle_dw_bot import get_subtitle

load_dotenv()
bot_api_key = os.environ.get("BOT_API_KEY")

bot = TeleBot(bot_api_key, parse_mode='HTML')


@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.send_message(message.chat.id, '- Enter a name of a movie.\n\n- Including release year is rcommended.\n- Only English subtitles are available, for now.')

@bot.message_handler()
def subtitle(message):
    bot.send_message(message.chat.id, 'Downloading subtitle...')

    try:
        id = str(message.chat.id) + '-' + str(message.id)
        path = get_subtitle(message.text, id)

        subtitle_file = open(path, encoding='cp1252')
        bot.send_document(message.chat.id, subtitle_file, reply_to_message_id=message.id)
        subtitle_file.close()

        shutil.rmtree(id)
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, 'Try again.')

print('Running...')

bot.remove_webhook()
bot.polling()