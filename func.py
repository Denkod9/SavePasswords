import cryptography
from PyQt5.QtWidgets import QFileDialog

from cryptography.fernet import Fernet
from stegano import exifHeader
from exceptions import error_message
import sys
import os

import secrets


# для нахождения картинок в exe
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


# чтение текста с изображения
def read_text_img(key) -> str:
    try:
        file_path = open_file(key)

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


# сохранение текста в изображение
def save_text_to_img(text, key):
    try:
        if len(text) == 0:
            raise ValueError(error_message("Файл не должен быть пустым"))
        file_path = open_file(key)

        encrypt_text = encrypt_message(key, text)

        file_name = "_passwords.".join(file_path.split("."))
        exifHeader.hide(file_path, file_name, encrypt_text)

    except Exception as ex:
        print(ex)


# выбор файла для дальнейшей обработки
def open_file(key) -> str:
    # Проверяем, что ключ не является None и имеет правильную длину
    is_key = key is not None and len(key) == 44
    if not is_key:
        raise ValueError(error_message("Ключ не указан или не имеет правильную длину"))

    file_dialog = QFileDialog()
    file_dialog.setNameFilter("Images (*.jpg *.bmp *.jpeg);; *.jpg;; *.bmp;; *.jpeg")
    file_dialog.setFileMode(QFileDialog.ExistingFile)
    file_dialog.setViewMode(QFileDialog.List)
    file_path = file_dialog.getOpenFileName()[0]

    if not file_path:
        raise ValueError(error_message("No such file"))

    # Проверка, является ли выбранный файл изображением по расширению
    allowed_extensions = (".jpg", ".bmp", ".jpeg")
    if not file_path.lower().endswith(allowed_extensions):
        raise ValueError(error_message("Выбранный файл не может быть использовн"))

    return file_path


# сгенерировать ключ
def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
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
