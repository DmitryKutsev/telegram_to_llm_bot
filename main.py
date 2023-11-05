import os
import openai
import telebot
from dotenv import load_dotenv

from utils import detect_lang

from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

load_dotenv()


api_key = os.getenv('API_KEY')
bot_key = os.getenv('BOT_KEY')

bot = telebot.TeleBot(bot_key)
llm = ChatOpenAI(openai_api_key=api_key, model_name="gpt-3.5-turbo", temperature=0)

last_msg_lst = [' ']

def translate_msg(msg: str) -> str:
    """Translates the given message from English to Russian or vice versa."""
    curr_lang = detect_lang(msg)

    if curr_lang == "en":
        translation_lang = "Dutch"
        second_lang = "Russian"
        current_lang = "English"
    elif curr_lang == "nl":
        translation_lang = "English"
        second_lang = "Russian"
        current_lang = "Dutch"
    elif curr_lang == "ru":
        translation_lang = "Dutch"
        second_lang = "English"
        current_lang = "Russian"
    else:
        translation_lang = "English"
        second_lang = "Duch"
        current_lang = curr_lang

    prompt_template = PromptTemplate.from_template("Translate the message from {current_lang} to "
                                                   "1) {translation_lang} and 2) {second_lang}."
                                                   "Message: {msg}")
    prompt = prompt_template.format(current_lang=current_lang,
                                    translation_lang=translation_lang,
                                    second_lang=second_lang,
                                    msg=msg)

    return llm.predict(prompt)


def describe_msg(msg: str) -> str:
    """Describes the given message."""
    prompt_template = PromptTemplate.from_template(
                                "Please, split the given message into words and translate each word separately in two languages"
                                " 1) in English and 2) in Russian. "
                                "Message: {msg}"
                                
                                                   )
    prompt = prompt_template.format(msg=msg)

    return llm.predict(prompt)


@bot.message_handler(commands=['start'])
def start_message(message: telebot.types.Message) -> None:
    bot.send_message(message.chat.id, """Hello! I am your OpenAI-based translator bot.
                      I translate English to Russian and vice versa!""")


@bot.message_handler(commands=['help'])
def help_message(message: telebot.types.Message) -> None:
    bot.send_message(message.chat.id, """I am your OpenAI-based translator bot.
                      Just tag me in your message and I will translate it for you!""")
    
@bot.message_handler(commands=['describe'])
def describe_message(message: telebot.types.Message) -> None:
    """Describes the given message in English and Russian."""

    response = describe_msg(last_msg_lst[0])
    bot.send_message(message.chat.id, response)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_all(message: telebot.types.Message) -> None:
    """Handles all messages that are not commands."""
    last_msg_lst[0] = message.text
    response = translate_msg(message.text)
    bot.reply_to(message, response)


if __name__ == '__main__':
    bot.infinity_polling()