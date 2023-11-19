import cryptography
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem

from cryptography.fernet import Fernet
from stegano import exifHeader
from exceptions import error_message
import sys
import os
import json

import secrets


# для нахождения картинок в exe
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


# чтение текста с изображения
def read_text_img(self, key) -> str:
    try:
        file_path = open_file(self, key)

        encrypt_text = exifHeader.reveal(file_path)
        encrypt_text = encrypt_text.decode()

        decrypt_text = decrypt_message(key, encrypt_text)

        return decrypt_text

    except cryptography.fernet.InvalidToken:
        error_message("Неверный ключ")

    except KeyError:
        error_message("Выбран не тот файл")

    except Exception as ex:
        print(ex)


# преобразование тбличных данных в текст
def table_data_to_text(table):
    data = []
    for row in range(table.rowCount()):
        row_data = []
        for column in range(table.columnCount()):
            item = table.item(row, column)
            if item is not None:
                row_data.append(item.text())
            else:
                row_data.append("")
        data.append(row_data)
    return json.dumps(data)


# преобразование текста в данные для таблицы
def text_to_table_data(text, table):
    table.clearContents()
    data = json.loads(text)
    table.setRowCount(len(data))
    table.setColumnCount(len(data[0]))
    for row, row_data in enumerate(data):
        for column, text in enumerate(row_data):
            table.setItem(row, column, QTableWidgetItem(text))


# сохранение текста в изображение
def save_text_to_img(self, text, key):
    try:
        if len(text) == 0:
            raise ValueError(error_message("Файл не должен быть пустым"))
        file_path = open_file(self, key)

        encrypt_text = encrypt_message(key, text)

        file_name = "_passwords.".join(file_path.split("."))
        exifHeader.hide(file_path, file_name, encrypt_text)

        generate_key_file(file_name, key)

    except Exception as ex:
        print(ex)


# выбор файла для дальнейшей обработки
def open_file(self, key) -> str:
    # Проверяем, что ключ не является None и имеет правильную длину
    is_key = key is not None and len(key) == 44
    if not is_key:
        raise ValueError(error_message("Ключ не указан или не имеет правильную длину"))

    file_path, _ = QFileDialog.getOpenFileName(self, 'Выберите изображение', '', 'Image Files (*.jpeg *.jpg)')

    if not file_path:
        raise ValueError(error_message("No such file"))

    # Проверка, является ли выбранный файл изображением по расширению
    allowed_extensions = (".jpg", ".jpeg")
    if not file_path.lower().endswith(allowed_extensions):
        raise ValueError(error_message("Выбранный файл не может быть использован.\n"
                                       "Попробуйте следующие форматы: '.jpg', '.jpeg'"))

    return file_path


# сгенерировать ключ
def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)


# ключ сохраняется рядом с картинкой
def generate_key_file(filename, key):
    test = [".jpg", ".jpeg"]
    for ext in test:
        if filename.endswith(ext):
            filename = filename[:-len(ext)]
            break

    with open(f"{filename}.txt", "w") as key_file:
        key_file.write(key)


# зашифровать текст
def encrypt_message(key, message):
    encoded_message = message.encode()
    fernet = Fernet(key)
    encrypted_message = fernet.encrypt(encoded_message)
    return encrypted_message


# расшифровать текст
def decrypt_message(key, encrypted_message):
    fernet = Fernet(key)
    decrypted_message = fernet.decrypt(encrypted_message)
    return decrypted_message.decode()


# функция для чтения файла
def read_secret_key() -> str:
    with open("secret.key", "r") as file:
        key = file.read()

    return key


# создать новый пароль
def create_new(length, characters):
    return "".join(secrets.choice(characters) for _ in range(length))
