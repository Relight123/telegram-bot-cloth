import telebot
from telebot import types
import sqlite3
import os
from datetime import datetime

bot = telebot.TeleBot('8008772489:AAF6pSVLc1b16WDx7awirW4SGKP8HhZ4pIM')

admin_chat_id = 1013095495

def get_products():
    """Получает список товаров из базы данных."""
    try:
        with sqlite3.connect('products.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, description, price, image FROM products")
            products = cursor.fetchall()
        return products
    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")
        return []

def register_user(user_id, username, first_name, last_name):
    """Регистрирует пользователя в базе данных."""
    try:
        with sqlite3.connect('products.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO users (user_id, username, first_name, last_name) "
                "VALUES (?, ?, ?, ?)",
                (user_id, username, first_name, last_name)
            )
            conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при регистрации пользователя: {e}")

def add_to_cart(user_id, product_name, quantity=1):
    """Добавляет товар в корзину пользователя."""
    try:
        with sqlite3.connect('products.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO cart (user_id, product_name, quantity) VALUES (?, ?, ?)",
                (user_id, product_name, quantity)
            )
            conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при добавлении товара в корзину: {e}")

def get_cart(user_id):
    """Возвращает содержимое корзины пользователя."""
    try:
        with sqlite3.connect('products.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT product_name, quantity FROM cart WHERE user_id = ?", (user_id,))
            cart_items = cursor.fetchall()
        return cart_items
    except sqlite3.Error as e:
        print(f"Ошибка при получении корзины: {e}")
        return []

def clear_cart(user_id):
    """Очищает корзину пользователя."""
    try:
        with sqlite3.connect('products.db') as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при очистке корзины: {e}")

def calculate_total(cart_items):
    """Рассчитывает общую стоимость товаров в корзине."""
    total = 0
    products = get_products()
    for item in cart_items:
        product_name, quantity = item
        for product in products:
            if product[0] == product_name:
                price = int(product[2].replace('₽', '').replace('$', '').replace(',', '').strip())
                total += price * quantity
    return total

def add_feedback(user_id, feedback_text):
    """Добавляет отзыв в базу данных."""
    try:
        with sqlite3.connect('products.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO feedback (user_id, feedback_text) VALUES (?, ?)",
                (user_id, feedback_text)
            )
            conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при добавлении отзыва: {e}")

def get_feedbacks():
    """Возвращает все отзывы из базы данных."""
    try:
        with sqlite3.connect('products.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT users.username, feedback.feedback_text, feedback.feedback_date FROM feedback JOIN users ON feedback.user_id = users.user_id")
            feedbacks = cursor.fetchall()
        return feedbacks
    except sqlite3.Error as e:
        print(f"Ошибка при получении отзывов: {e}")
        return []

@bot.message_handler(commands=["start"])
def welcome(message):
    """Обрабатывает команду /start и показывает главное меню."""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('👕Товары')
    button2 = types.KeyboardButton('⚙️Настройки')
    button3 = types.KeyboardButton('🔴Помощь')
    button4 = types.KeyboardButton('🛒Корзина')
    button5 = types.KeyboardButton('👤Личный кабинет')
    markup.row(button1)
    markup.row(button2, button3)
    markup.row(button4, button5)

    if message.text == "/start":
        bot.send_message(
            message.chat.id,
            f"Привет!, {message.from_user.first_name}!\n"
            f"У меня нас можешь купить одежду!\n"
            f"Контакты разработчиков: @relight_b, @suppnexy",
            reply_markup=markup
        )
    else:
        bot.send_message(
            message.chat.id,
            "Ты вернулся в главное меню!",
            reply_markup=markup
        )

@bot.message_handler(content_types='photo')
def handle_payment_screenshot(message):
    """Обрабатывает скриншот перевода."""
    order_info = (
        f"Новый заказ от пользователя @{message.from_user.username} (ID: {message.from_user.id}).\n"
        f"Скриншот оплаты прикреплен."
    )
    markup = types.InlineKeyboardMarkup()
    confirm_button = types.InlineKeyboardButton(
        "Подтвердить оплату",
        callback_data=f"confirm_{message.from_user.id}"
    )
    reject_button = types.InlineKeyboardButton(
        "Отклонить оплату",
        callback_data=f"reject_{message.from_user.id}"
    )
    markup.add(confirm_button, reject_button)

    bot.send_photo(
        admin_chat_id,
        message.photo[-1].file_id,
        caption=order_info,
        reply_markup=markup
    )

    bot.send_message(
        message.chat.id,
        "Спасибо! Администратор проверит ваш платеж и подтвердит заказ."
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_admin_action(call):
    """Обрабатывает действия администратора."""
    action, user_id = call.data.split("_")
    user_id = int(user_id)

    if action == "confirm":
        bot.send_message(
            user_id,
            "Ваш платеж подтвержден! Заказ обрабатывается."
        )
        clear_cart(user_id)  # Очистка корзины
        bot.send_message(
            admin_chat_id,
            f"Оплата от пользователя {user_id} подтверждена."
        )
    elif action == "reject":
        bot.send_message(
            user_id,
            "Ваш платеж отклонен. Пожалуйста, свяжитесь с администратором."
        )
        bot.send_message(
            admin_chat_id,
            f"Оплата от пользователя {user_id} отклонена."
        )

    # Удаление кнопок у администратора
    bot.edit_message_reply_markup(
        admin_chat_id,
        call.message.message_id,
        reply_markup=None
    )

@bot.message_handler()
def info(message):
    """Обрабатывает текстовые сообщения."""
    if message.text == "👕Товары":
        goods_chapter(message)
    elif message.text.startswith("Купить: "):
        bot.send_message(
            message.chat.id,
            "Напиши ему по поводу покупки: @relight_b"
        )
    elif message.text.startswith("Товар"):
        show_product_info(message)
    elif message.text == "⚙️Настройки":
        setting_chapter(message)
    elif message.text == "🔴Помощь":
        info_chapter(message)
    elif message.text == "Написать разработчику":
        bot.send_message(
            message.chat.id,
            "@relight_b"
        )
    elif message.text == "🔙Вернуться" or message.text == "🔙Вернуться в меню":
        welcome(message)
    elif message.text == "🛒Корзина":
        show_cart(message)
    elif message.text == "👤Личный кабинет":
        show_profile(message)
    elif message.text.startswith("Добавить в корзину: "):
        add_product_to_cart(message)
    elif message.text == "Очистить корзину":
        clear_user_cart(message)
    elif message.text == "Оплатить вручную":
        manual_payment(message)
    elif message.text == "Оставить отзыв":
        leave_feedback(message)  # Обработка кнопки "Оставить отзыв"
    elif message.text == "Просмотреть отзывы":
        show_feedbacks(message)  # Обработка кнопки "Просмотреть отзывы"
    else:
        bot.send_message(
            message.chat.id,
            "Я не понял, повтори"
        )

def goods_chapter(message):
    """Показывает список товаров."""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    products = get_products()

    for product in products:
        product_button = types.KeyboardButton(f"Товар: {product[0]}")
        markup.add(product_button)

    back_button = types.KeyboardButton('🔙Вернуться в меню')
    markup.add(back_button)

    bot.send_message(
        message.chat.id,
        "Выберите товар:",
        reply_markup=markup
    )

def show_product_info(message):
    """Показывает информацию о выбранном товаре."""
    product_name = message.text.replace("Товар: ", "")
    products = get_products()

    for product in products:
        if product[0] == product_name:
            description = product[1]
            price = product[2]
            image_path = product[3]

            if os.path.exists(image_path):
                with open(image_path, 'rb') as photo:
                    bot.send_photo(message.chat.id, photo)
            else:
                bot.send_message(
                    message.chat.id,
                    "Изображение товара не найдено."
                )

            bot.send_message(
                message.chat.id,
                f"{product_name}\n{description}\nЦена: {price}"
            )

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            buy_button = types.KeyboardButton(f"Купить: {product_name}")
            add_to_cart_button = types.KeyboardButton(f"Добавить в корзину: {product_name}")
            back_button = types.KeyboardButton('🔙Вернуться в меню')
            markup.add(buy_button, add_to_cart_button, back_button)

            bot.send_message(
                message.chat.id,
                "Выберите действие:",
                reply_markup=markup
            )
            return

    bot.send_message(
        message.chat.id,
        "Товар не найден."
    )

def setting_chapter(message):
    """Показывает меню настроек."""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('Написать разработчику')
    button2 = types.KeyboardButton('Оставить отзыв')
    button3 = types.KeyboardButton('Просмотреть отзывы')
    button4 = types.KeyboardButton('🔙Вернуться в меню')
    markup.row(button1)
    markup.row(button2, button3)
    markup.row(button4)

    bot.send_message(
        message.chat.id,
        "Настройки:\nЗдесь ты можешь изменить ваши параметры.",
        reply_markup=markup
    )

def info_chapter(message):
    """Показывает меню помощи."""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('Написать разработчику')
    button2 = types.KeyboardButton('🔙Вернуться в меню')
    markup.row(button1, button2)

    bot.send_message(
        message.chat.id,
        "Раздел справки.\nЗдесь ты можешь написать моему разработчику.",
        reply_markup=markup
    )

def show_cart(message):
    """Показывает содержимое корзины пользователя."""
    user_id = message.from_user.id
    cart_items = get_cart(user_id)

    if cart_items:
        cart_message = "Ваша корзина:\n"
        for item in cart_items:
            cart_message += f"{item[0]} - {item[1]} шт.\n"
        total = calculate_total(cart_items)
        cart_message += f"\nОбщая сумма: {total}₽"
        bot.send_message(
            message.chat.id,
            cart_message
        )

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        pay_button = types.KeyboardButton('Оплатить вручную')
        clear_button = types.KeyboardButton('Очистить корзину')
        back_button = types.KeyboardButton('🔙Вернуться в меню')
        markup.row(pay_button, clear_button)
        markup.row(back_button)

        bot.send_message(
            message.chat.id,
            "Выберите действие:",
            reply_markup=markup
        )
    else:
        bot.send_message(
            message.chat.id,
            "Ваша корзина пуста."
        )

def show_profile(message):
    """Показывает личный кабинет пользователя."""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    register_user(user_id, username, first_name, last_name)

    profile_message = (
        f"👤 Личный кабинет:\n"
        f"Имя: {first_name} {last_name}\n"
        f"Username: @{username}\n"
    )
    bot.send_message(
        message.chat.id,
        profile_message
    )

def add_product_to_cart(message):
    """Добавляет товар в корзину пользователя."""
    user_id = message.from_user.id
    product_name = message.text.replace("Добавить в корзину: ", "")

    add_to_cart(user_id, product_name)
    bot.send_message(
        message.chat.id,
        f"Товар {product_name} добавлен в корзину."
    )

def clear_user_cart(message):
    """Очищает корзину пользователя."""
    user_id = message.from_user.id
    clear_cart(user_id)
    bot.send_message(
        message.chat.id,
        "Ваша корзина очищена."
    )

def manual_payment(message):
    """Предлагает пользователю оплатить вручную."""
    user_id = message.from_user.id
    cart_items = get_cart(user_id)
    total = calculate_total(cart_items)

    if total == 0:
        bot.send_message(
            message.chat.id,
            "Ваша корзина пуста."
        )
        return

    payment_instructions = (
        f"Для оплаты заказа на сумму {total}₽:\n"
        "1. Переведите деньги на номер +79991234567 (Сбербанк).\n"
        "2. Отправьте скриншот перевода в этот чат.\n"
        "3. Мы проверим платеж и подтвердим ваш заказ."
    )

    bot.send_message(
        message.chat.id,
        payment_instructions
    )

@bot.message_handler(func=lambda message: message.text == "Оставить отзыв")
def leave_feedback(message):
    """Запрашивает отзыв у пользователя."""
    bot.send_message(
        message.chat.id,
        "Пожалуйста, напишите ваш отзыв:"
    )
    bot.register_next_step_handler(message, process_feedback)

def process_feedback(message):
    """Обрабатывает отзыв пользователя."""
    user_id = message.from_user.id
    feedback_text = message.text
    add_feedback(user_id, feedback_text)
    bot.send_message(
        message.chat.id,
        "Спасибо за ваш отзыв!"
    )

@bot.message_handler(func=lambda message: message.text == "Просмотреть отзывы")
def show_feedbacks(message):
    """Показывает все отзывы."""
    feedbacks = get_feedbacks()
    if feedbacks:
        feedback_message = "Отзывы:\n"
        for feedback in feedbacks:
            feedback_message += f"@{feedback[0]}: {feedback[1]} (Дата: {feedback[2]})\n"
        bot.send_message(
            message.chat.id,
            feedback_message
        )
    else:
        bot.send_message(
            message.chat.id,
            "Отзывов пока нет."
        )

if __name__ == "__main__":
    bot.polling(none_stop=True)