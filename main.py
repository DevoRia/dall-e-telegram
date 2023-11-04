from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import os
from dotenv import load_dotenv

from dalle import generate_image_with_dalle
from db import set_uri, is_user_allowed, store_message
from s3 import put_object, set_s3_creds

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
DALLE_API_KEY = os.getenv("DALLE_API_KEY")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")

set_uri(MONGO_URI)
set_s3_creds(AWS_ACCESS_KEY, AWS_SECRET_KEY)


def img(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if not is_user_allowed(user_id):
        print(user_id, 'wanted to use service')
        update.message.reply_text("Вам не можна користуватись цією функцією.")
        return

    prompt = ' '.join(context.args)

    if prompt == '':
        update.message.reply_text("Ви не ввели промпт😠")
        return

    loading_message = update.message.reply_text("⏳Завантаження...")

    print(user_id, 'used prompt')

    try:
        loading_message.delete()
        generation_message = update.message.reply_text("🎨Генерація...")

        image_url = generate_image_with_dalle(prompt, DALLE_API_KEY)

        generation_message.delete()
        download_message = update.message.reply_text("📩Отримання...")

        print(user_id, 'received the image for prompt', prompt[:10])

        s3_url = put_object(AWS_S3_BUCKET, user_id, prompt, image_url)
        print(user_id, 'uploaded to s3')
        store_message(user_id, prompt, s3_url, image_url)

        update.message.reply_photo(photo=image_url, reply_to_message_id=update.message.message_id)

        download_message.delete()

    except ValueError as e:
        print(user_id, 'error with prompt', prompt[:10])

        if f"{e}" == "billing_hard_limit_reached":
            update.message.reply_text(f"Ліміт ресурсу вичерпано абсолютно.")
        elif f"{e}" == "rate_limit_exceeded":
            update.message.reply_text(
                f"Ліміт ресурсу вичерпано. Потрібно спробувати ще раз через 1 хвилину. Ліміт 3 запити на хвилину, та 200 запитів в день.")
        else:
            update.message.reply_text(f"Помилка!!!:\n{e}")
    finally:
        print(user_id, 'finished')


def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("img", img))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
