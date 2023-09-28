import os
import openai
import telebot

from utils import detect_lang

from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate


api_key = os.getenv("ENRU_OPENAPI_KEY")
bot_key = os.getenv("BOT_KEY")

bot = telebot.TeleBot(bot_key)
llm = OpenAI(openai_api_key=api_key)

def translate_msg(msg: str) -> str:
    """Translates the given message from English to Russian or vice versa."""
    curr_lang = detect_lang(msg)

    if curr_lang == "ru":
        translation_lang = "english"
        current_lang = "russian"
    else:
        translation_lang = "russian"
        current_lang = "english"

    prompt = f'Translate the message from {current_lang} to {translation_lang}.'\
             f'Message: {msg}'
    print(prompt)
    return llm.predict(prompt)

@bot.inline_handler(lambda query: query.query == 'text')
def query_text(message):
    response = translate_msg(message.text)

    print(message.text)
    print(11)
    print(response)
    bot.reply_to(message, response)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, """Hello! I am your OpenAI translator bot.
                     I translate English to Russian and vice versa!""")


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    response = translate_msg(message.text)

    print(message.text)
    print(11)
    print(response)
    bot.reply_to(message, response)

if __name__ == "__main__":
    bot.polling()
