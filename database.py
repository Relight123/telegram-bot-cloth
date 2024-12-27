import sqlite3

def create_database():
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()

    # Создание таблицы products
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            description TEXT,
            price TEXT,
            image TEXT
        )
    ''')

    # Создание таблицы users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            username TEXT,
            first_name TEXT,
            last_name TEXT
        )
    ''')

    # Создание таблицы cart
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_name TEXT,
            quantity INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')

    # Создание таблицы feedback
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            feedback_text TEXT,
            feedback_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')

    # Добавление тестовых данных в таблицу products
    products = [
        ("Товар 1", "Описание товара 1: качественная футболка.", "1000₽", "./test.jpg"),
        ("Товар 2", "Описание товара 2: стильные джинсы.", "1500₽", "./test.jpg"),
        ("Товар 3", "Описание товара 3: удобные кроссовки.", "2000₽", "./test.jpg"),
        ("Товар 4", "Описание товара 4: элегантная рубашка.", "2500₽", "./test.jpg"),
        ("Товар 5", "Описание товара 5: кеды.", "3000₽", "./test.jpg")
    ]

    # Проверка, чтобы не добавлять дубликаты
    cursor.execute("SELECT name FROM products")
    existing_products = [row[0] for row in cursor.fetchall()]

    for product in products:
        if product[0] not in existing_products:
            cursor.execute('INSERT INTO products (name, description, price, image) VALUES (?, ?, ?, ?)', product)

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_database()