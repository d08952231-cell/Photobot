import telebot
from PIL import Image
import os

TOKEN = "7727584585:AAELht4V_5JOoM7hK3UP21m-CVgFL7787kM"
bot = telebot.TeleBot(TOKEN)

user_state = {}

# ---------- /start ----------
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Привет🖐️\n"
        "Давно хотел порезать фото, но получалось не ровно?\n"
        "Ты пришёл по адресу 😎\n\n"
        "Тут ты можешь разрезать своё фото на несколько частей.\n"
        "Просто пришли фото боту 📸"
    )

# ---------- Фото ----------
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    file = bot.download_file(file_info.file_path)

    os.makedirs("photos", exist_ok=True)
    path = f"photos/{message.from_user.id}.jpg"

    with open(path, "wb") as f:
        f.write(file)

    user_state[message.from_user.id] = path
    bot.send_message(message.chat.id, "На сколько частей порезать? Напиши 9 или 16")

# ---------- Число ----------
@bot.message_handler(func=lambda m: m.text in ["9", "16"])
def handle_parts(message):
    user_id = message.from_user.id

    if user_id not in user_state:
        bot.send_message(message.chat.id, "Сначала отправь фото 📷")
        return

    parts = 3 if message.text == "9" else 4
    img = Image.open(user_state[user_id])

    w, h = img.size
    tile_w = w // parts
    tile_h = h // parts

    media = []

    for y in range(parts):
        for x in range(parts):
            crop = img.crop((
                x * tile_w,
                y * tile_h,
                (x + 1) * tile_w,
                (y + 1) * tile_h
            ))

            name = f"photos/{user_id}_{y}_{x}.jpg"
            crop.save(name)

            media.append(
                telebot.types.InputMediaPhoto(open(name, "rb"))
            )

    # Отправляем ВСЁ ОДНИМ АЛЬБОМОМ
    bot.send_media_group(message.chat.id, media)

    # Чистим файлы
    for item in media:
        item.media.close()

    for file in os.listdir("photos"):
        if file.startswith(str(user_id)):
            os.remove(f"photos/{file}")

    bot.send_message(message.chat.id, "Готово ✅ Можешь отправить новое фото")

# ---------- Запуск ----------
bot.polling(none_stop=True)