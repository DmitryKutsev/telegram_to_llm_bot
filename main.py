import os
import openai
import telebot

from utils import detect_lang

from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate


api_key = os.getenv("ENRU_OPENAPI_KEY")
bot_key = os.getenv("BOT_KEY")

bot = telebot.TeleBot(bot_key)
llm = ChatOpenAI(openai_api_key=api_key, model_name="gpt-3.5-turbo", temperature=0)

def translate_msg(msg: str) -> str:
    """Translates the given message from English to Russian or vice versa."""
    curr_lang = detect_lang(msg)

    if curr_lang == "ru":
        translation_lang = "english"
        current_lang = "russian"
    else:
        translation_lang = "russian"
        current_lang = "english"

    prompt_template = PromptTemplate.from_template("Translate the message from {current_lang} to {translation_lang}."
                                                   "Message: {msg}")
    prompt = prompt_template.format(current_lang=current_lang, translation_lang=translation_lang, msg=msg)

    return llm.predict(prompt)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_all(message: telebot.types.Message) -> None:
    """Handles all messages that are not commands."""
    response = translate_msg(message.text)
    bot.reply_to(message, response)


@bot.message_handler(commands=['start'])
def start_message(message: telebot.types.Message) -> None:
    bot.send_message(message.chat.id, """Hello! I am your OpenAI-based translator bot.
                      I translate English to Russian and vice versa!""")


@bot.message_handler(commands=['help'])
def help_message(message: telebot.types.Message) -> None:
    bot.send_message(message.chat.id, """I am your OpenAI-based translator bot.
                      Just tag me in your message and I will translate it for you!""")


if __name__ == "__main__":
    bot.polling(non_stop=True)
