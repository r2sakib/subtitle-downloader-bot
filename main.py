from telebot import TeleBot, types
import shutil
import os
from dotenv import load_dotenv
from subtitle_dw_bot import get_subtitle

from flask import Flask, request

load_dotenv()
bot_api_key = os.environ.get("BOT_API_KEY")

bot = TeleBot(bot_api_key, parse_mode='HTML')
server = Flask(__name__)


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


@server.route('/' + bot_api_key, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://subtitle-downloader-bot.herokuapp.com/' + bot_api_key)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))