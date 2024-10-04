import logging
import os
from telegram import Update
from telegram.constants import ReactionEmoji
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler
from typing import Optional

from capacities.api_client import CapacitiesAPIClient


logger = logging.getLogger("capacities-telegram-bot")
TELEGRAM_INBOX_TAG = "telegram-inbox"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,  # type: ignore
        text=(
            "Ready! Start posting messages, "
            "I'll append them to your active daily note "
            "([follow Markdown format](https://www.markdownguide.org/basic-syntax/))."
        )
    )


async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not (
        update.message and
        (msg := update.message.text)
    ):
        # Ignore
        return

    api_client: CapacitiesAPIClient = context.bot_data["api_client"]
    telegram_inbox_tag: CapacitiesAPIClient = context.bot_data["telegram_inbox_tag"]
    opts: dict = context.bot_data["opts"]

    if update.message.is_topic_message:
        try:
            # NOTE: https://github.com/tdlib/telegram-bot-api/issues/356#issuecomment-1751924102
            topic = update.message.reply_to_message.forum_topic_created.name  # type: ignore
            msg += f" #{topic}"
        except Exception as e:
            logger.error(f"Could not get topic name. {e}")
            await update.message.reply_text(
                text="Could not get topic name, sorry :c. For more info check the logs."
            )

    if opts.get("only_forward_from_topics"):
        # Do not forward if message not coming from topic
        return

    msg += f" #{telegram_inbox_tag}"
    api_client.save_to_daily_note(msg, no_time_stamp=False)

    await update.message.set_reaction(
        reaction=ReactionEmoji.WRITING_HAND
    )


HANDLERS = [
    CommandHandler("start", start),
    MessageHandler(None, message),
]


class CapacitiesTelegramBot:
    def __init__(
        self,
        token: Optional[str] = None,
        telegram_inbox_tag: Optional[str] = None,
        only_forward_from_topics: bool = False
    ) -> None:

        if not (
            token := token or os.getenv("CAPACITIES_TELEGRAM_BOT_TOKEN")
        ):
            raise ValueError(
                "Telegram token cannot be None."
                "Please provide one or define CAPACITIES_TELEGRAM_BOT_TOKEN env var."
            )

        telegram_inbox_tag = (
            telegram_inbox_tag or
            os.getenv("CAPACITIES_TELEGRAM_INBOX_TAG", TELEGRAM_INBOX_TAG)
        )

        only_forward_from_topics = (
            only_forward_from_topics or
            os.getenv("ONLY_FORWARD_FROM_TOPICS", "false").lower() in ["true", "1"]
        )
        opts = {
            "only_forward_from_topics": only_forward_from_topics
        }

        self.application = ApplicationBuilder().token(token).build()
        self.application.bot_data["api_client"] = CapacitiesAPIClient()
        self.application.bot_data["telegram_inbox_tag"] = telegram_inbox_tag
        self.application.bot_data["opts"] = opts

        for handler in HANDLERS:
            self.application.add_handler(handler)

    def run(self):
        self.application.run_polling()
