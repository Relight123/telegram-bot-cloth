class DatabaseModel:
    """
    Модель базы данных, описывающая все таблицы и их структуру.
    """

    class Product:
        """
        Модель таблицы products.
        """
        def __init__(self, id, name, description, price, image):
            self.id = id  # Уникальный идентификатор товара
            self.name = name  # Название товара
            self.description = description  # Описание товара
            self.price = price  # Цена товара
            self.image = image  # Ссылка на изображение товара

    class User:
        """
        Модель таблицы users.
        """
        def __init__(self, id, user_id, username, first_name, last_name):
            self.id = id  # Уникальный идентификатор записи
            self.user_id = user_id  # Уникальный идентификатор пользователя
            self.username = username  # Имя пользователя
            self.first_name = first_name  # Имя
            self.last_name = last_name  # Фамилия

    class Cart:
        """
        Модель таблицы cart.
        """
        def __init__(self, id, user_id, product_name, quantity):
            self.id = id  # Уникальный идентификатор записи
            self.user_id = user_id  # Идентификатор пользователя
            self.product_name = product_name  # Название товара
            self.quantity = quantity  # Количество товара

    class Feedback:
        """
        Модель таблицы feedback.
        """
        def __init__(self, id, user_id, feedback_text, feedback_date):
            self.id = id  # Уникальный идентификатор записи
            self.user_id = user_id  # Идентификатор пользователя
            self.feedback_text = feedback_text  # Текст отзыва
            self.feedback_date = feedback_date  # Дата отзыва