import sys

from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QTableWidgetItem
from PyQt5.QtGui import QIcon
from design import Ui_MainWindow

from func import (create_new, generate_key, read_secret_key, save_text_to_img,
                  read_text_img, resource_path, table_data_to_text, text_to_table_data)
from string import ascii_lowercase, ascii_uppercase, digits, punctuation
from exceptions import error_message


class SavePasswords(QMainWindow):
    def __init__(self):
        super(SavePasswords, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.is_show = True

        self.init_ui()

    def init_ui(self):
        self.setWindowIcon(QIcon(resource_path("img/icon.jpg")))
        self.ui.img_save_tab.setPixmap(QtGui.QPixmap(resource_path("img/new.jpg")))
        self.ui.img_generate_tab.setPixmap(QtGui.QPixmap(resource_path("img/new.jpg")))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(resource_path("img/eye_hide.png")))
        self.ui.pass_show_btn.setIcon(icon)

        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        file_menu = QMenu("&File", self)
        menu_bar.addMenu(file_menu)

        file_menu.addAction("Open", self.action_clicked)
        file_menu.addAction("Save", self.action_clicked)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.action_clicked)

        # region Save and Read Password
        self.ui.add_to_list_btn.clicked.connect(self.add_to_show_password)
        self.ui.pass_show_btn.clicked.connect(self.replace_img_password_show_hide)

        self.ui.save_to_img.clicked.connect(self.save_to_file)

        self.ui.clear_table_btn.clicked.connect(self.clear_table)
        # endregion

        # region Generate Password and Secret key
        # изменение len_pass_slider и len_pass_edt
        self.ui.len_pass_slider.valueChanged.connect(self.update_line_edit)
        self.ui.len_pass_edt.textChanged.connect(self.update_slider)

        # ввод в значенте слайдера ограничиваем цифрами
        self.ui.len_pass_edt.setValidator(Qt.QIntValidator(0, 99))

        # генерация пароля по клику
        self.ui.generate_password_btn.clicked.connect(self.set_password)

        # генерация ключа для кодирования текста
        self.ui.key_generate_btn.clicked.connect(self.show_secret_key)
        # endregion

    # region Функции выбора меню
    @QtCore.pyqtSlot()
    def action_clicked(self):
        action = self.sender()

        if action.text() == "Open":
            try:
                key = self.ui.key_edt.text()

                decrypt_text = read_text_img(self, key)
                text_to_table_data(decrypt_text, self.ui.show_text_tbl)
            except Exception as ex:
                print(ex)

        elif action.text() == "Save":
            key = self.ui.key_edt.text()
            text = table_data_to_text(self.ui.show_text_tbl)

            save_text_to_img(self, text, key)

        elif action.text() == "Exit":
            sys.exit()
    # endregion

    # region Save and Read Password

    # очистка таблицы
    def clear_table(self):
        self.ui.show_text_tbl.setRowCount(0)

    # сохранение файла по кнопке
    def save_to_file(self):
        key = self.ui.key_edt.text()
        text = table_data_to_text(self.ui.show_text_tbl)

        save_text_to_img(self, text, key)

    # смена изображения и показ пароля по нажатию кнопки показа пароля
    def replace_img_password_show_hide(self):
        icon = QtGui.QIcon()
        if self.is_show:
            icon.addPixmap(QtGui.QPixmap(resource_path("img/eye.png")))
            self.ui.password_edt.setEchoMode(QtWidgets.QLineEdit.Normal)
            self.is_show = False
        else:
            icon.addPixmap(QtGui.QPixmap(resource_path("img/eye_hide.png")))
            self.ui.password_edt.setEchoMode(QtWidgets.QLineEdit.Password)
            self.is_show = True
        self.ui.pass_show_btn.setIcon(icon)
        self.ui.pass_show_btn.setObjectName("pass_show_btn")

    # добовление Логина, оплисания и пароля в область для чтения паролей
    def add_to_show_password(self):
        login = self.ui.login_edt.text() if len(self.ui.login_edt.text()) != 0 else "———————————"
        description = self.ui.description_edt.text() if len(self.ui.description_edt.text()) != 0 else "———————————"
        password = self.ui.password_edt.text() if len(self.ui.password_edt.text()) != 0 else "———————————"

        row_position = self.ui.show_text_tbl.rowCount()
        self.ui.show_text_tbl.insertRow(row_position)

        self.ui.show_text_tbl.setItem(row_position, 0, QTableWidgetItem(login))
        self.ui.show_text_tbl.setItem(row_position, 1, QTableWidgetItem(description))
        self.ui.show_text_tbl.setItem(row_position, 2, QTableWidgetItem(password))

        self.ui.login_edt.setText("")
        self.ui.description_edt.setText("")
        self.ui.password_edt.setText("")
    # endregion

    # region Generate Password and Secret key
    # Настройка слайдера: при движении его позиция отображается в len_pass_edt и наоборот
    def update_line_edit(self):
        self.ui.len_pass_edt.setText(str(self.ui.len_pass_slider.value()))

    def update_slider(self):
        if self.ui.len_pass_edt.text() == "":
            self.ui.len_pass_edt.setText("1")
        try:
            value = int(self.ui.len_pass_edt.text())
            self.ui.len_pass_slider.setValue(value)
        except Exception as ex:
            print(type(ex))

    # генерация пароля учитывая включенные ф-ии
    def set_password(self):
        try:
            chars = ""

            if self.ui.digits_cbx.isChecked():
                chars += digits

            if self.ui.lower_cbx.isChecked():
                chars += ascii_lowercase

            if self.ui.upper_cbx.isChecked():
                chars += ascii_uppercase

            if self.ui.symbol_cbx.isChecked():
                chars += punctuation

            length = int(self.ui.len_pass_slider.value())
            generated_password = create_new(length=length, characters=chars)
            self.ui.generate_password_edt.setText(generated_password)
        except IndexError:
            error_message("Выберите хотябы один параметр для генерации пароля")

    # создать ключ, сохранить его и показать
    def show_secret_key(self):
        generate_key()
        key = read_secret_key()

        self.ui.key_generate_edt.setText(key)
    # endregion


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SavePasswords()
    window.show()

    sys.exit(app.exec_())
