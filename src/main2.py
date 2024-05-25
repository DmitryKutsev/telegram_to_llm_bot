import os
import time
from pathlib import Path

import telebot
from dotenv import load_dotenv
from loguru import logger
from openai import OpenAI
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from together import Together

load_dotenv()


BOT_KEY = os.getenv("BOT_KEY")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai_client = OpenAI(api_key=OPENAI_API_KEY)
together_client = Together(api_key=TOGETHER_API_KEY)

DEFAULT_MODEL = "gpt-4o"
DEFAULT_LLM_CLIENT = openai_client

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

ALL_MODELS_LIST = TOGETHER_MODELS_LIST + [DEFAULT_MODEL]

MODELS_IN_USE_LIST = [DEFAULT_MODEL]
CLIENTS_IN_USE_LIST = [DEFAULT_LLM_CLIENT]
TEMPLATES_IN_USE_LIST = [SYSTEM_PROMPT_TEMPLATE]

last_msg_lst = [" "]

# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Starts the conversation and asks the user about their preferred car type."""
#     reply_keyboard = [["Sedan", "SUV", "Sports", "Electric"]]
# reply_string = """<b>Welcome to the LLM API BOT. It is creted mostly for the translation between
#     Dutch/English/Russian languages, but you can customize prompts and models to build
#     your own usecase.</b>"""

#     await update.message.reply_text(
#         reply_string,
#         parse_mode="HTML",
#         reply_markup=ReplyKeyboardMarkup(
#             reply_keyboard, one_time_keyboard=True, resize_keyboard=True
#         ),
#     )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text(
        "Bye! Hope to talk to you again soon.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def show_prompt_template(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    await update.message.reply_text(
        f"Current template is {TEMPLATES_IN_USE_LIST[-1]}",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )


async def change_llm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Changes an llm instance."""
    curr_message = update.message.text.split(" ")[-1]
    if curr_message not in ALL_MODELS_LIST:
        response_msg = f"Haven't found model {curr_message} in the list. Changing to {MODELS_IN_USE_LIST[-1]}."

        # TODO: move this block into utils?
        await update.message.reply_text(
            response_msg,
            parse_mode="HTML",
            reply_markup=ReplyKeyboardRemove(),
        )

    if curr_message in TOGETHER_MODELS_LIST:
        CLIENTS_IN_USE_LIST[-1] = together_client
        MODELS_IN_USE_LIST[-1] = curr_message
        response_msg = (
            f"You have successfully changed your llm to {MODELS_IN_USE_LIST[-1]}"
        )

        await update.message.reply_text(
            response_msg,
            parse_mode="HTML",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        CLIENTS_IN_USE_LIST[-1] = openai_client  # noqa: F841
        MODELS_IN_USE_LIST[-1] = curr_message  # noqa: F841
        response_msg = (
            f"You have successfully changed your llm to {MODELS_IN_USE_LIST[-1]}"
        )

        await update.message.reply_text(
            response_msg,
            parse_mode="HTML",
            reply_markup=ReplyKeyboardRemove(),
        )


async def restore_prompt_template(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    TEMPLATES_IN_USE_LIST[-1] = system_prompt_path.read_text()  # noqa: F841

    await update.message.reply_text(
        f"Template should be restored to {TEMPLATES_IN_USE_LIST[-1]}",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )


async def list_llms(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "\n".join(ALL_MODELS_LIST),
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )


async def change_prompt_template(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    new_template = update.message.text.split()[-1]
    if new_template == "/change_prompt":
        new_template = ""
    TEMPLATES_IN_USE_LIST[-1] = new_template  # noqa: F841
    msg = f"New prompt template:\n{new_template}"

    await update.message.reply_text(
        msg,
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )


async def show_curr_model(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f"Current model is {MODELS_IN_USE_LIST[-1]}",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )


async def responce_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles all messages that are not commands."""
    last_msg_lst[0] = update.message.text
    response = CLIENTS_IN_USE_LIST[-1].chat.completions.create(
        model=MODELS_IN_USE_LIST[-1],
        messages=[
            {
                "role": "user",
                "content": f"{TEMPLATES_IN_USE_LIST[-1]} {last_msg_lst[0]}",
            }
        ],
    )
    reply_string = f"{response.choices[0].message.content}"
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=reply_string, parse_mode="HTML"
    )


def main() -> None:
    """Run the bot."""
    application = Application.builder().token(BOT_KEY).build()

    # conv_handler = ConversationHandler(
    #     entry_points=[CommandHandler("start", start)],
    #     states={
    #         show_prompt_template: [
    #             CommandHandler("show_prompt", show_prompt_template)
    #         ],
    #         CAR_COLOR: [CallbackQueryHandler(car_color)],
    #         CAR_MILEAGE_DECISION: [CallbackQueryHandler(car_mileage_decision)],
    #         CAR_MILEAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, car_mileage)],
    #         PHOTO: [
    #             MessageHandler(filters.PHOTO, photo),
    #             CommandHandler('skip', skip_photo)
    #         ],
    #         SUMMARY: [MessageHandler(filters.ALL, summary)]
    #     },
    #     fallbacks=[CommandHandler("cancel", cancel), CommandHandler("start", start)],
    # )

    # application.add_handler(conv_handler)

    # Handle the case when a user sends /start but they're not in a conversation
    # application.add_handler(CommandHandler("start", start))
    application.add_handler(responce_all)
    application.add_handler(CommandHandler("show_prompt", show_prompt_template))

    application.run_polling()


if __name__ == "__main__":
    responce_all_handler = MessageHandler(
        filters.TEXT & (~filters.COMMAND), responce_all
    )

    application = Application.builder().token(BOT_KEY).build()
    # application.add_handler(CommandHandler("start", start))
    application.add_handler(responce_all_handler)
    application.add_handler(CommandHandler("show_prompt", show_prompt_template))
    application.add_handler(CommandHandler("show_model", show_curr_model))
    application.add_handler(CommandHandler("change_llm", change_llm))
    application.add_handler(CommandHandler("change_prompt", change_prompt_template))
    application.add_handler(CommandHandler("restore_prompt", restore_prompt_template))
    application.add_handler(CommandHandler("list_llms", list_llms))


    application.run_polling()
