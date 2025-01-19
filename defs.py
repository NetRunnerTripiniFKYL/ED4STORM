# Импортируем библиотеку json для работы с файлами
import json
from config import AUTH_FILE

# Загрузка авторизованных пользователей из файла
def load_authorized_users():
    try:
        with open(AUTH_FILE, "r") as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

# Сохранение авторизованных пользователей в файл
def save_authorized_users(users):
    with open(AUTH_FILE, "w") as f:
        json.dump(list(users), f)

