import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, ReplyKeyboardMarkup, KeyboardButton
import os, json
from datetime import datetime, timedelta
from collections import defaultdict
import threading
import re
album_buffer = defaultdict(list)
TOKEN = "8305042007:AAE2PX79pcdFuQ59wB6cRXnDqchLOjZxHgM"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")  # parse_mode включён глобально

ADMINS = [542079843]
GROUP_CHAT_ID = -1003003522297
user_states = {}
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "posts.db")
POSTS_FILE = os.path.join(BASE_DIR, "posts.json")
USERS_FILE = os.path.join(BASE_DIR, "users.txt")
IMAGES_DIR = os.path.join(BASE_DIR, "images")
os.makedirs(IMAGES_DIR, exist_ok=True)

os.makedirs(IMAGES_DIR, exist_ok=True)

def download_media(file_id: str) -> str:
    file_info = bot.get_file(file_id)
    data = bot.download_file(file_info.file_path)
    save_path = os.path.join(IMAGES_DIR, f"{file_id}.jpg")
    with open(save_path, "wb") as f:
        f.write(data)
    return save_path

# --- Загрузка и сохранение постов ---
def load_posts():
    if os.path.exists(POSTS_FILE):
        try:
            with open(POSTS_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except json.JSONDecodeError:
            return []
    return []

def save_posts(posts):
    with open(POSTS_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=4)

import shutil

SITE_IMAGES_DIR = os.path.join("..", "site", "katalog", "images")
os.makedirs(SITE_IMAGES_DIR, exist_ok=True)

def save_post(media, title, caption, characteristics):
    posts = load_posts()
    post_id = (max([p.get("post_id", 0) for p in posts], default=0) + 1)

    renamed_media = []
    for idx, file_id in enumerate(media, start=1):
        old_path = os.path.join("bot/images", f"{file_id}.jpg")
        new_name = f"img{post_id}-{idx}.jpg"
        new_path = os.path.join("bot/images", new_name)

        # Переименовываем в bot/images
        if os.path.exists(old_path):
            shutil.move(old_path, new_path)

        # Копируем в site/images (для сайта)
        site_path = os.path.join("site/images", new_name)
        os.makedirs(os.path.dirname(site_path), exist_ok=True)
        shutil.copy2(new_path, site_path)

        renamed_media.append(new_name)

    post = {
        "post_id": post_id,
        "timestamp": datetime.now().isoformat(),
        "media": renamed_media,
        "title": title,
        "caption": caption,
        "characteristics": characteristics
    }

    posts.append(post)
    save_posts(posts)

    return post
   # 🔥 возвращаем весь пост, а не только id




# --- Пользователи ---
if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r") as f:
        users = set(int(line.strip()) for line in f if line.strip())
else:
    users = set()

def save_users():
    with open(USERS_FILE, "w") as f:
        for user_id in users:
            f.write(str(user_id) + "\n")

# --- Главное меню ---
def main_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("📰 Актуальні пропозиції"))
    return keyboard

# --- START ---
@bot.message_handler(commands=["start"])
def start(message):
    users.add(message.chat.id)
    save_users()
    bot.send_message(
        message.chat.id,
        "👋 Привіт! Ви завітали до бота телеграм каналу https://t.me/Prezident_Cars ✅",
        reply_markup=main_menu()
    )

# --- POST ALL ---
waiting_for_post = {}
pending_post = {}

@bot.message_handler(commands=["postall"])
def postall(message):
    if message.chat.id not in ADMINS:
        return bot.send_message(message.chat.id, "⛔ у вас немає прав виконати данну команду.")
    waiting_for_post[message.chat.id] = "photos"
    pending_post[message.chat.id] = {"photos": [], "title": "", "caption": "", "characteristics": ""}
    bot.send_message(message.chat.id, "✍️ Відправте фото для машини (можна декілька). Після першого фото я попрошу заголовок.")

# --- POST ALL (текст) ---
waiting_for_textpost = {}
pending_textpost = {}

@bot.message_handler(commands=["postalltext"])
def postalltext(message):
    if message.chat.id not in ADMINS:
        return bot.send_message(message.chat.id, "⛔ у вас немає прав виконати данну команду")
    waiting_for_textpost[message.chat.id] = True
    pending_textpost[message.chat.id] = {"text": ""}
    bot.send_message(message.chat.id, "✍️ Відправте текст для Текстової розсилки")

@bot.message_handler(func=lambda m: m.chat.id in waiting_for_post, content_types=['photo'])
def handle_photos(message):
    chat_id = message.chat.id
    step = waiting_for_post[chat_id]
    post = pending_post[chat_id]

    # === Обработка альбома ===
    if message.media_group_id:
        album_buffer[message.media_group_id].append(message)

        # ждём 1.5 сек, пока Телеграм пришлёт все фото из альбома
        def process_album():
            photos = album_buffer.pop(message.media_group_id, [])
            for msg in photos:
                file_id = msg.photo[-1].file_id
                download_media(file_id)
                post["photos"].append(file_id)

            if photos:
                bot.send_message(
                    chat_id,
                    f"📷 Додано {len(photos)} фото!\n✍️ Тепер введіть ЗАГОЛОВОК для машини"
                )
                waiting_for_post[chat_id] = "title"

        threading.Timer(1.5, process_album).start()
        return

    # === Одиночное фото ===
    if step == "photos":
        file_id = message.photo[-1].file_id
        download_media(file_id)
        post["photos"].append(file_id)

        if len(post["photos"]) == 1:
            bot.send_message(chat_id, "📷 Фото додане!\n✍️ Тепер введіть ЗАГОЛОВОК для машини")
            waiting_for_post[chat_id] = "title"

# --- Получение фото/заголовка/характеристик/описания ---
@bot.message_handler(func=lambda m: m.chat.id in waiting_for_post, content_types=['photo','text'])
def handle_post(message):
    chat_id = message.chat.id
    step = waiting_for_post[chat_id]
    post = pending_post[chat_id]

    # === 1) Фото ===
    if step == "photos":
        if message.content_type == 'photo':
            file_id = message.photo[-1].file_id  # берём id самой большой версии фото

            # скачиваем фото сразу в папку bot/images/
            try:
                download_media(file_id)
            except Exception as e:
                print(f"Не удалось скачать фото {file_id}: {e}")

            post["photos"].append(file_id)

            if len(post["photos"]) == 1:
                bot.send_message(
                    chat_id,
                    "📷 Фото додане!\n✍️ Тепер введіть ЗАГОЛОВОК для машини (наприклад: BMW 530d 2019)"
                )
                waiting_for_post[chat_id] = "title"
        else:
            bot.send_message(chat_id, "⚠️ Будь ласка, спочатку надішліть фото.")
        return

    # === 2) Заголовок ===
    if step == "title" and message.content_type == 'text':
        post["title"] = message.text.strip()
        waiting_for_post[chat_id] = "characteristics"
        bot.send_message(chat_id, "✍️ Тепер введіть ХАРАКТЕРИСТИКИ (вільним текстом або списком)")
        return

    # === 3) Характеристики ===
    if step == "characteristics" and message.content_type == 'text':
        post["characteristics"] = message.text.strip()
        waiting_for_post[chat_id] = "caption"
        bot.send_message(chat_id, "✍️ Тепер введіть ОПИС (стан, історія, додатково)")
        return

    # === 4) Опис ===
    if step == "caption" and message.content_type == 'text':
        post["caption"] = message.text.strip()
        waiting_for_post.pop(chat_id, None)

        # подтверждение
        preview_text = (
            f"<b>🏷 {post['title'] or 'Без назви'}</b>\n\n"
            f"📋 Характеристики:\n{post['characteristics'] or '—'}\n\n"
            f"📝 {post['caption'] or '—'}"
        )
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("✅ Відправити", callback_data="send_post"),
            InlineKeyboardButton("❌ Відміна", callback_data="cancel_post")
        )
        bot.send_message(chat_id, "✅ Усі дані отримано. Попередній перегляд:")
        if post["photos"]:
            try:
                bot.send_media_group(chat_id, [InputMediaPhoto(fid) for fid in post["photos"]])
            except Exception as e:
                print(f"Ошибка предпросмотра фото: {e}")
        bot.send_message(chat_id, preview_text, reply_markup=markup)
        return


# --- Кнопки под постом ---
def create_user_buttons(post_id, admin=False):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("📞 Контакти", callback_data=f"contact_{post_id}"),
        InlineKeyboardButton("⭐ Зацікавило", callback_data=f"interest_{post_id}")
    )
    if admin:
        markup.add(InlineKeyboardButton("❌ Видалити пост", callback_data=f"delete_{post_id}"))
    return markup

# --- Callback рассылки ---
@bot.callback_query_handler(func=lambda c: c.data in ["send_post", "cancel_post"])
def callback_post(call):
    chat_id = call.message.chat.id

    if call.data == "cancel_post":
        pending_post.pop(chat_id, None)
        return bot.edit_message_text("❌ Пост відмінили.", chat_id, call.message.message_id)

    if call.data == "send_post":
        post = pending_post.pop(chat_id)

    # сохраняем в JSON и получаем пост
        saved_post = save_post(post["photos"], post["title"], post["caption"], post["characteristics"])

    # генерируем HTML страницу
        generate_car_page(saved_post)

        # добавляем в каталог
        add_to_catalog(saved_post)

        media = [InputMediaPhoto(file_id) for file_id in post["photos"]]
        text_full = (
        f"<b>🏷 {post['title'] or 'Без назви'}</b>\n\n"
        f"📋 Характеристики:\n{post['characteristics'] or '—'}\n\n"
        f"📝 {post['caption'] or '—'}"
        )


        success = 0
        # рассылаем всем пользователям
        for user_id in list(users):
            try:
                if media:
                    bot.send_media_group(user_id, media)
                bot.send_message(
                    user_id,
                    text_full,
                    reply_markup=create_user_buttons(post.get('post_id'), admin=(user_id in ADMINS))
                )
                success += 1
            except:
                # молча пропускаем недоступных
                pass

        # отправляем в группу
        try:
            if media:
                bot.send_media_group(GROUP_CHAT_ID, media)
            bot.send_message(GROUP_CHAT_ID, text_full, reply_markup=create_user_buttons(saved_post['post_id']))
        except:
            pass

        bot.edit_message_text(f"✅ Пост відправлено {success} користувачам і в групу.", chat_id, call.message.message_id)

# --- Актуальні пости ---
@bot.message_handler(func=lambda m: m.text == "📰 Актуальні пропозиції")
def send_recent_posts(message):
    user_id = message.from_user.id
    posts = load_posts()
    if not posts:
        return bot.send_message(user_id, "❌ Поки ще немає актуальних пропозицій, спробуйте пізніше.")

    now = datetime.now()
    recent_posts = [p for p in posts if datetime.fromisoformat(p["timestamp"]) > now - timedelta(hours=24)]
    if not recent_posts:
        return bot.send_message(user_id, "❌ За останні 24 години пропозицій не було.")

    bot.send_message(user_id, "📰 Актуальні пропозиції за 24 години:")

    def build_media_entities(media_items):
        entities = []
        for m in media_items:
            # Если это имя файла (после save_post) — отправляем как файл
            if isinstance(m, str) and m.lower().endswith(".jpg"):
                local_path = os.path.join(IMAGES_DIR, m)
                site_path  = os.path.join(SITE_IMAGES_DIR, m) if 'SITE_IMAGES_DIR' in globals() else None

                path = local_path if os.path.exists(local_path) else (site_path if site_path and os.path.exists(site_path) else None)
                if path:
                    entities.append(InputMediaPhoto(open(path, "rb")))
                else:
                    print(f"Файл для отправки не найден: {m}")
            else:
                # Иначе предполагаем, что это file_id (поддержка старых записей)
                entities.append(InputMediaPhoto(m))
        return entities

    for post in recent_posts:
        media_list = post.get("media", []) or []
        title = post.get("title") or "Без назви"
        caption = post.get("caption", "Без опису")
        characteristics = post.get("characteristics", "—")

        text_full = (
            f"<b>🏷 {title}</b>\n\n"
            f"📋 Характеристики:\n{characteristics}\n\n"
            f"📝 {caption}"
        )

        try:
            if media_list:
                media_entities = build_media_entities(media_list)
                if media_entities:
                    bot.send_media_group(user_id, media_entities)
            bot.send_message(
                user_id,
                text_full,
                reply_markup=create_user_buttons(post.get("post_id"), admin=(user_id in ADMINS))
            )
        except Exception as e:
            print(f"Ошибка при пересылке поста: {e}")


# --- Кнопки пользователей ---
@bot.callback_query_handler(func=lambda c: c.data.startswith(("contact_", "interest_", "delete_")))
def handle_user_choice(call):
    user_id = call.from_user.id
    try:
        action, post_id_str = call.data.split("_", 1)
        post_id = int(post_id_str)
    except ValueError:
        return

    posts = load_posts()
    post = next((p for p in posts if p.get("post_id") == post_id), None)

    if action in ["contact", "interest"] and not post:
        try:
            bot.send_message(user_id, "❌ Ця пропозицій більше не актуальна.")
        except: pass
        return

    if action == "delete" and user_id in ADMINS:
        posts = [p for p in posts if p.get("post_id") != post_id]
        save_posts(posts)
        try:
            bot.send_message(user_id, "✅ Пост видалено з бази.")
        except: pass
        return

    if action == "contact":
        for admin_id in ADMINS:
            try:
                bot.send_message(admin_id, f"🔔 Користувач обрав 📞 Контакти\nTelegram: @{call.from_user.username or 'не вказано'}")
            except: pass
        try:
            bot.send_message(user_id, "✅ Ваша заявка прийнята! З вами зв'яжуться в найкоротший час.")
        except: pass

    if action == "interest":
        # сохраняем контекст для завки
        user_states[user_id] = {
            "step": "wait_name",
            "data": {},
            "car_title": post.get("title", "Без назви"),
            "car_desc": post.get("caption", "Без опису"),
            "car_specs": post.get("characteristics", "Не вказані"),
            "post_id": post.get("post_id")
        }
        try:
            bot.send_message(user_id, "⭐ Вас зацікавила пропозиція.\nВведіть своє ім'я (як до вас звертатись):")
        except:
            pass

# --- Сбор данных заявки ---
@bot.message_handler(func=lambda m: m.from_user.id in user_states and user_states[m.from_user.id]["step"] == "wait_name")
def handle_name(message):
    user_id = message.from_user.id
    user_states[user_id]["data"]["name"] = message.text.strip()
    user_states[user_id]["step"] = "wait_phone"
    bot.send_message(user_id, "Введіть номер телефону для контакту (наприклад: +380123456789):")

@bot.message_handler(func=lambda m: m.from_user.id in user_states and user_states[m.from_user.id]["step"] == "wait_phone")
def handle_phone(message):
    user_id = message.from_user.id
    phone = message.text.strip()
    if len(phone) < 13 or not phone.startswith("+"):
        return bot.send_message(user_id, "⚠️ Номер телефону має бути у форматі +380123456789\nСпробуйте ще раз:")
    user_states[user_id]["data"]["phone"] = phone
    name = user_states[user_id]["data"]["name"]
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("✅ Підтвердити", callback_data="confirm_interest"),
        InlineKeyboardButton("❌ Відмінити", callback_data="cancel_action")
    )
    bot.send_message(user_id, f"📋 Перевірте дані:\n\nІм'я: {name}\nТелефон: {phone}", reply_markup=markup)
    user_states[user_id]["step"] = "confirming"

@bot.callback_query_handler(func=lambda c: c.data in ["confirm_interest", "cancel_action"])
def handle_interest_confirm(call):
    user_id = call.from_user.id

    if call.data == "cancel_action":
        user_states.pop(user_id, None)
        try:
            return bot.edit_message_text("❌ Заявку скасовано.", call.message.chat.id, call.message.message_id)
        except:
            return

    data = user_states.pop(user_id, None)
    if not data:
        return bot.answer_callback_query(call.id, "Немає активної заявки або час очікування вийшов.")

    name = data["data"].get("name", "Не вказано")
    phone = data["data"].get("phone", "Не вказано")
    car_title = data.get("car_title", "Без назви")
    car_desc = data.get("car_desc", "Без опису")
    car_specs = data.get("car_specs", "Не вказані")
    username = call.from_user.username or "не вказано"

    # подтверждаем пользователю
    try:
        bot.send_message(user_id, "✅ Заявка створена! З Вами звʼяжуться в найкоротший термін.")
    except:
        pass

    # отправляем админу все данные
    for admin_id in ADMINS:
        try:
            bot.send_message(
                admin_id,
                f"🔔 Нова заявка!\n\n"
                f"🏷 <b>{car_title}</b>\n"
                f"📋 Характеристики: {car_specs}\n"
                f"📝 Опис: {car_desc}\n\n"
                f"👤 Ім'я: {name}\n"
                f"📞 Телефон: {phone}\n"
                f"💬 Телеграм: @{username}"
            )
        except:
            pass

# --- Статистика ---
@bot.message_handler(commands=["stats"])
def stats_command(message):
    if message.chat.id not in ADMINS:
        return bot.send_message(message.chat.id, "⛔ У вас нема прав.")
    bot.send_message(message.chat.id, f"👥 Всього користувачів: {len(users)}")

@bot.message_handler(commands=["checkusers"])
def check_users(message):
    if message.chat.id not in ADMINS:
        return bot.send_message(message.chat.id, "⛔ У вас нема прав.")
    inactive = []
    for user_id in list(users):
        try:
            bot.send_chat_action(user_id, "typing")
        except:
            inactive.append(user_id)
            users.remove(user_id)
    bot.send_message(message.chat.id, f"✅ Перевірка завершена.\nВидалено неактивних: {len(inactive)}\nЗараз активних: {len(users)}")

# === Функция генерации HTML ===
def generate_car_page(post, images_path="images", template_path="site/templatecar/template.html", output_folder="site/carsfolder"):
    import re

    # Читаем шаблон
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    # Генерируем данные
    filename = re.sub(r'\W+', '', post["title"].lower()) + ".html"
    filepath = os.path.join(output_folder, filename)

    main_photo = f"../{images_path}/{post['media'][0]}" if post["media"] else ""
    gallery_html = "\n".join(
        [f'<img src="../{images_path}/{img}" alt="car image">' for img in post["media"]]
    )

    # Подставляем в шаблон
    html_content = (
        template.replace("{{title}}", post["title"])
                .replace("{{description}}", post["caption"])
                .replace("{{features}}", post["characteristics"])
                .replace("{{main_photo}}", main_photo)
                .replace("{{gallery}}", gallery_html)
    )

    # Создаём папку если её нет
    os.makedirs(output_folder, exist_ok=True)

    # Сохраняем HTML
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[INFO] Страница создана: {filepath}")
    return filepath

def add_to_catalog(post, katalog_path="site/katalogtemp/katalog.html"):
    # читаем html каталога
    with open(katalog_path, "r", encoding="utf-8") as f:
        katalog_html = f.read()

    import re
    filename = re.sub(r'\W+', '', post["title"].lower()) + ".html"

    # карточка по шаблону каталога
    card_html = f"""
    <a href="../carsfolder/{filename}" class="card">
        <img src="../images/{post['media'][0]}" alt="{post['title']}">
        <h2>{post['title']}</h2>
        <p>{post['caption']}</p>
    </a>
    """

    # вставляем перед </div> каталога
    if '<div class="catalog-grid">' in katalog_html:
        katalog_html = katalog_html.replace(
            "</div>\n\n  <!-- Пагинация -->", 
            card_html + "\n    </div>\n\n  <!-- Пагинация -->"
        )
    else:
        # fallback — в конец body
        katalog_html = katalog_html.replace("</body>", card_html + "\n</body>")

    with open(katalog_path, "w", encoding="utf-8") as f:
        f.write(katalog_html)

    print(f"[INFO] Добавлена карточка в каталог: {post['title']}")

# --- Запуск бота ---
print("🤖 Бот запущен...")
bot.polling(none_stop=True)
