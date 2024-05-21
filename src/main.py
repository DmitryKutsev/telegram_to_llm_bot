import os
import time
from pathlib import Path

import telebot
from dotenv import load_dotenv
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

curr_dir = Path(__file__).parent
PROMPT_FOLDER_PATH = curr_dir / "prompt_templates"


system_prompt_path = PROMPT_FOLDER_PATH / "system_prompt_template.txt"
SYSTEM_PROMPT_TEMPLATE = system_prompt_path.read_text()


TOGETHER_MODELS_LIST = [
    "zero-one-ai/Yi-34B-Chat",
    "meta-llama/Llama-3-8b-chat-hf",
    "meta-llama/Llama-3-70b-chat-hf",
    "mistralai/Mixtral-8x22B-Instruct-v0.1",
    "Qwen/Qwen1.5-110B-Chat",
    "WizardLM/WizardLM-13B-V1.2",
    "togethercomputer/RedPajama-INCITE-7B-Chat",
    "togethercomputer/alpaca-7b",
]

MODELS_IN_USE_LIST = [CURRENT_MODEL]
CLIENTS_IN_USE_LIST = [CURRENT_LLM_CLIENT]
TEMPLATES_IN_USE_LIST = [SYSTEM_PROMPT_TEMPLATE]

bot = telebot.TeleBot(BOT_KEY)

last_msg_lst = [" "]


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


@bot.message_handler(commands=["show_prompt"])
def show_prompt_template(message: telebot.types.Message) -> None:
    bot.send_message(
        message.chat.id,
        TEMPLATES_IN_USE_LIST[-1],
    )


@bot.message_handler(commands=["change_prompt"])
def change_prompt_template(message: telebot.types.Message) -> None:
    new_template = message.text
    TEMPLATES_IN_USE_LIST[-1] = new_template  # noqa: F841
    msg = f"New prompt template:\n{new_template}"

    bot.send_message(
        message.chat.id,
        msg,
    )


@bot.message_handler(commands=["restore_prompt"])
def restore_prompt_template(message: telebot.types.Message) -> None:
    TEMPLATES_IN_USE_LIST[-1] = system_prompt_path.read_text()  # noqa: F841

    bot.send_message(
        message.chat.id,
        "Template should be restored",
    )


@bot.message_handler(commands=["list_prompt_templates"])
def list_prompt_templates(
    message: telebot.types.Message, folder_path=PROMPT_FOLDER_PATH
) -> None:
    path = Path(folder_path)
    files = [file for file in path.iterdir() if file.is_file()]

    bot.send_message(
        message.chat.id,
        files,
    )

    for file in files:
        bot.send_message(
            message.chat.id,
            file.read_text(),
        )
        time.sleep(1)


@bot.message_handler(commands=["change_llm"])
def describe_message(message: telebot.types.Message) -> None:
    """Changes an llm instance."""
    if message.text not in TOGETHER_MODELS_LIST:
        CLIENTS_IN_USE_LIST[-1] = openai_client
        MODELS_IN_USE_LIST[-1] = "gpt-4o"
        response_msg = (
            "Haven't found model in the list. Changing to default {CURRENT_MODEL}."
        )
        bot.send_message(message.chat.id, response_msg)
    else:
        CLIENTS_IN_USE_LIST[-1] = together_client  # noqa: F841
        MODELS_IN_USE_LIST[-1] = message.text  # noqa: F841

    response_msg = "You have successfully changed your llm to {CURRENT_MODEL}"
    bot.send_message(message.chat.id, response_msg)


@bot.message_handler(func=lambda message: True, content_types=["text"])
def echo_all(message: telebot.types.Message) -> None:
    """Handles all messages that are not commands."""
    last_msg_lst[0] = message.text
    response = CLIENTS_IN_USE_LIST[-1].chat.completions.create(
        model=MODELS_IN_USE_LIST[-1],
        messages=[
            {
                "role": "user",
                "content": f"{TEMPLATES_IN_USE_LIST[-1]} {message.text}",
            }
        ],
    )

    bot.reply_to(message, response.choices[0].message.content)


if __name__ == "__main__":
    bot.infinity_polling()
