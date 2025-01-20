# Импортируем библиотеку json для работы с файлами
import json
import os
from config import AUTH_FILE, USER_DATA_FILE, USER_PROGRESS_FILE


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

#-----------------------------------------------------------------------------------------#

# Загрузка данных из файла (если файл существует)
def load_user_data():
    try:
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except json.JSONDecodeError:
        # Если файл пуст или содержит некорректные данные, возвращаем пустой словарь
        return {}
    except FileNotFoundError:
        # Если файл не найден, также возвращаем пустой словарь
        return {}

# Сохранение данных пользователя в файл
def save_user_data(data):
    with open(USER_DATA_FILE, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Функция для получения данных пользователя по ID
def get_user_data(user_id):
    user_data = load_user_data()
    return user_data.get(str(user_id), None)

# Функция для добавления/обновления данных пользователя
def set_user_data(user_id, data):
    user_data = load_user_data()
    user_data[str(user_id)] = data
    save_user_data(user_data)

# Функция для очистки данных пользователя
def clear_user_data(user_id):
    user_data = load_user_data()
    if str(user_id) in user_data:
        del user_data[str(user_id)]
        save_user_data(user_data)

#-----------------------------------------------------------------------------------------#

# Загрузка прогресса
def load_user_progress():
    file_path = USER_PROGRESS_FILE  # Убедитесь, что путь к файлу указан правильно
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    else:
        return {}  # Возвращаем пустой словарь, если файл не существует или пуст

# Сохранение прогресса
def save_user_progress(progress):
    with open(USER_PROGRESS_FILE, "w") as file:
        json.dump(progress, file)

# Обновление прогресса пользователя
def update_user_progress(user_id, module_id, lesson_index, quiz_index, is_correct):
    progress = load_user_progress()
    if str(user_id) not in progress:
        progress[str(user_id)] = {}
    user_progress = progress[str(user_id)]
    if module_id not in user_progress:
        user_progress[module_id] = {}
    if lesson_index not in user_progress[module_id]:
        user_progress[module_id][lesson_index] = {}
    user_progress[module_id][lesson_index][quiz_index] = is_correct
    save_user_progress(progress)

# Получение прогресса пользователя
def get_user_progress(user_id):
    progress = load_user_progress()
    return progress.get(str(user_id), {})