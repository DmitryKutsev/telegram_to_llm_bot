import os

import telebot
from dotenv import load_dotenv
from pathlib import Path
from openai import OpenAI
from together import Together


load_dotenv()


BOT_KEY = os.getenv("BOT_KEY")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai_client = OpenAI(api_key=OPENAI_API_KEY)
together_client = Together(api_key=TOGETHER_API_KEY)

CURRENT_MODEL = "gpt-4o"
CURRENT_LLM_CLIENT = openai_client

bot = telebot.TeleBot(BOT_KEY)
llm_client = Together(api_key=TOGETHER_API_KEY)


system_prompt_template = Path("prompt_template.txt").read_text()

last_msg_lst = [" "]


# def describe_msg(msg: str) -> str:
#     """Describes the given message."""

#     prompt_template = PromptTemplate.from_template(
#         "Please, split the given message into words and translate each word separately in two languages"
#         " 1) in English and 2) in Russian. "
#         "Message: {msg}"
#     )
#     prompt = prompt_template.format(msg=msg)

#     return llm.predict(prompt)


@bot.message_handler(commands=["start"])
def start_message(message: telebot.types.Message) -> None:
    bot.send_message(
        message.chat.id,
        """Hello! I am your OpenAI-based translator bot.
                      I translate English to Russian and vice versa!""",
    )


@bot.message_handler(commands=["help"])
def help_message(message: telebot.types.Message) -> None:
    bot.send_message(
        message.chat.id,
        """I am your OpenAI-based translator bot.
                      Just tag me in your message and I will translate it for you!""",
    )


# @bot.message_handler(commands=["describe"])
# def describe_message(message: telebot.types.Message) -> None:
#     """Describes the given message in English and Russian."""

#     response = describe_msg(last_msg_lst[0])
#     bot.send_message(message.chat.id, response)


@bot.message_handler(func=lambda message: True, content_types=["text"])
def echo_all(
    message: telebot.types.Message,
    llm_client: OpenAI | Together = CURRENT_LLM_CLIENT,
    model: str = CURRENT_MODEL,
) -> None:
    """Handles all messages that are not commands."""
    last_msg_lst[0] = message.text
    response = openai_client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": f"{system_prompt_template} {message.text}",
            }
        ],
    )

    bot.reply_to(message, response.choices[0].message.content)


if __name__ == "__main__":
    # bot.infinity_polling()
    response = together_client.chat.completions.create(
        model="meta-llama/Llama-3-8b-chat-hf",
        messages=[
            {
                "role": "user",
                "content": f"{system_prompt_template} What are some fun things to do in New York",
            }
        ],
    )

    print(response.choices[0].message.content, "Llama")

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": f"{system_prompt_template} What are some fun things to do in New York",
            }
        ],
    )
    print(response.choices[0].message.content, "Chatgpt")
