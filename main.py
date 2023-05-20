from abc import ABC, abstractmethod
import sys

from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QAction, QLabel, QListWidget, QLineEdit, QCheckBox, QRadioButton, QPushButton, QComboBox
from PyQt5.QtCore import Qt, QFileInfo, QFile, QTextStream, QIODevice, QDateTime
import re

class Fraction(object):
    def __init__(self, num, den):
        self.__num = num
        self.__den = den
        self.reduce()

    def __str__(self):
        return "%d/%d" % (self.__num, self.__den)

    def reduce(self):
        g = Fraction.gcd(self.__num, self.__den)
        self.__num /= g
        self.__den /= g

    def __neg__(self):
        return Fraction(-self.__num, self.__den)

    def __invert__(self):
        return Fraction(self.__den, self.__num)

    def __pow__(self, power):
        return Fraction(self.__num ** power, self.__den ** power)

    def __float__(self):
        return float(self.__num) / self.__den

    def __int__(self):
        return int(self.__num / self.__den)

    @staticmethod
    def gcd(n, m):
        if m == 0:
            return n
        else:
            return Fraction.gcd(m, n % m)


class Taggable(ABC):
    @abstractmethod
    def tag(self):
        pass


class Book(Taggable):
    __code = 0

    def __init__(self, name, author):
        if any(arg is None for arg in (name, author)):
            raise ValueError("Ошибка, введите все данные!")
        self.name = name
        self.author = author
        Book.__code += 1
        self.code = Book.__code


    def tag(self):
        return [word for word in self.name.split() if word[0].isupper()]


class Library(object):
    def __init__(self, address, number):
        if any(arg is None for arg in (address, number)):
            raise ValueError("Ошибка, введите все данные!")
        self.address = address
        self.number = number
        self.books = []


    def __iadd__(self, book):
        if not isinstance(book, Book):
            raise ValueError("Ошибка, можно добавлять только объекты класса 'Книга' в библиотеку!")
        self.books.append(book)
        return self


    def __iter__(self):
        return iter(self.books)


def Zad1():
    frac = Fraction(7, 2)
    print(-frac)
    print(~frac)
    print(frac ** 2)
    print(float(frac))
    print(int(frac))


def Zad2():
    lib = Library(1, '51 Some str., NY')
    lib += Book('Leo Tolstoi', 'War and Peace')
    lib += Book('Charles Dickens', 'David Copperfield')

    for book in lib:
        print(f"[{book.code}] {book.author} '{book.name}'")
        print(book.tag())

class SearchWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Поиск номера телефона")
        self.resize(800, 600)

        self.file_path = None
        self.log_file_path = "LogFile.log"
        self.log_opened = False

        self.result_list = QListWidget(self)
        self.result_list.setGeometry(0, 0, self.width(), self.height())

        self.status_label = QLabel(self)
        self.status_label.setAlignment(Qt.AlignLeft)
        self.status_label.setGeometry(0, self.height() - 30, int(self.width() * 0.6), 30)

        self.size_label = QLabel(self)
        self.size_label.setAlignment(Qt.AlignRight)
        self.size_label.setGeometry(int(self.width() * 0.6), self.height() - 30, int(self.width() * 0.4), 30)

        self.create_menu()

    def create_menu(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("Файл")
        open_action = QAction("Открыть...", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        log_menu = menu_bar.addMenu("Лог")
        export_action = QAction("Экспорт...", self)
        export_action.triggered.connect(self.export_log)
        log_menu.addAction(export_action)

        add_action = QAction("Добавить в лог", self)
        add_action.triggered.connect(self.add_to_log)
        log_menu.addAction(add_action)

        view_action = QAction("Просмотр", self)
        view_action.triggered.connect(self.view_log)
        log_menu.addAction(view_action)

    def open_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", "Текстовые файлы (*.txt)", options=options)
        if file_path:
            self.file_path = file_path
            self.process_file()
            self.status_label.setText(f"Обработан файл {QFileInfo(file_path).fileName()}")
            self.size_label.setText(self.get_file_size_string(file_path))

    def process_file(self):
        if not self.file_path:
            return

        if self.log_opened is True:
            self.result_list.clear()
        else: pass

        self.log_opened = False

        with open(self.file_path, 'r', encoding='utf-8') as file:
            current_datetime = QDateTime.currentDateTime().toString("dd.MM.yyyy HH:mm:ss")
            file_info = f"\nФайл: {self.file_path} был обработан {current_datetime}\n"
            self.result_list.addItem(file_info)
            for i, line in enumerate(file, start=1):
                for match in re.finditer(r'\(\+7\s?949\s?\)?\d{3}(-?)\d{2}\1\d{2}', line):
                    result = f'Строка: {i}, позиция: {match.start()}, найдено: {match.group(0)}\n'
                    self.result_list.addItem(result)

    def export_log(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Выберите файл для экспорта", "", "Текстовые файлы (*.txt)",
                                                   options=options)
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as file:
                for i in range(self.result_list.count()):
                    file.write(self.result_list.item(i).text() + '\n')

            QMessageBox.information(self, "Экспорт", "Экспорт завершен успешно")

    def add_to_log(self):
        if not QFile.exists(self.log_file_path):
            QMessageBox.information(self, "Информация", "Файл лога не найден. Файл будет создан автоматически")
        with open(self.log_file_path, 'a', encoding='utf-8') as file:
            current_datetime = QDateTime.currentDateTime().toString("dd.MM.yyyy HH:mm:ss")
            file.write(f"[{current_datetime}] {self.file_path}\n")

            for i in range(self.result_list.count()):
                file.write(self.result_list.item(i).text() + '\n')

            QMessageBox.information(self, "Лог", "Данные добавлены в лог")

    def view_log(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Подтверждение")
        msg.setIcon(QMessageBox.Question)
        msg.setText("Вы уверены, что хотите открыть лог файл? Данные последних поисков будут потеряны!")

        buttonAceptar = msg.addButton("Да", QMessageBox.YesRole)
        buttonCancelar = msg.addButton("Нет", QMessageBox.RejectRole)
        msg.setDefaultButton(buttonAceptar)
        msg.exec_()
        if msg.clickedButton() == buttonAceptar:
            self.log_opened = True
            self.status_label.setText("Открыт лог")
            self.size_label.clear()
            self.result_list.clear()

            if QFile.exists(self.log_file_path):
                with open(self.log_file_path, 'r', encoding='utf-8') as file:
                    for line in file:
                        self.result_list.addItem(line.rstrip('\n'))

    def get_file_size_string(self, file_path):
        file_info = QFileInfo(file_path)
        file_size = file_info.size()

        size_str = ""
        for unit in ['', 'K', 'M', 'G', 'T']:
            if file_size < 1024:
                size_str = f"{file_size:.0f} {unit}B"
                break
            file_size /= 1024

        return size_str


def Zad3():
    app = QApplication(sys.argv)
    window = SearchWindow()
    window.show()
    sys.exit(app.exec_())


class StringFormatter(object):
    @staticmethod
    def DelWords(string, n):
        words = string.split(' ')
        for i in range(len(words)):
            if (len(words[i]) < n):
                words[i] = ''
        return ' '.join(words)

    @staticmethod
    def ReplaceNum(string):
        words = string.split(' ')
        for i in range(len(words)):
            lit = list(words[i])
            for j in range(len(lit)):
                if lit[j].isdigit():
                    lit[j] = '*'
            words[i] = ''.join(lit)
        return ' '.join(words)

    @staticmethod
    def CreateSpace(string):
        words = string.split(' ')
        for i in range(len(words)):
            lit = list(words[i])
            words[i] = ' '.join(lit)
        return ' '.join(words)

    @staticmethod
    def SortSize(string):
        words = string.split(' ')
        return ' '.join(sorted(words, key=lambda word: len(word))).lstrip()

    @staticmethod
    def SortLex(string):
        words = string.split(' ')
        return ' '.join(sorted(words)).lstrip()


def Zad4():
    string = "ksl;jasfj aafdsa a dfs as  123 dfasfafsa"
    print(StringFormatter.DelWords(string, 3))
    print(StringFormatter.ReplaceNum(string))
    print(StringFormatter.CreateSpace(string))
    print(StringFormatter.SortSize(string))
    print(StringFormatter.SortLex(string))


class Formatter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StringFormatter")
        self.resize(800, 600)

        self.string_label = QLabel(self)
        self.string_label.setText("Строка: ")
        self.string_label.setGeometry(30, 30, 50, 30)

        self.string_text = QLineEdit(self)
        self.string_text.setGeometry(80,35,500,25)

        self.delete_word = QCheckBox(self)
        self.delete_word.setText("Удалить слова размером меньше")
        self.delete_word.setGeometry(30,100,185,30)

        self.change_digits = QCheckBox(self)
        self.change_digits.setText("Заменить все цифры на *")
        self.change_digits.setGeometry(30, 120, 185, 30)

        self.insert_space = QCheckBox(self)
        self.insert_space.setText("Вставить по пробелу между символами")
        self.insert_space.setGeometry(30, 140, 218, 30)

        self.sort_word = QCheckBox(self)
        self.sort_word.setText("Сортировать слова в строке")
        self.sort_word.setGeometry(30, 160, 185, 30)

        self.number_word = QLineEdit(self)
        self.number_word.setValidator(QIntValidator(self))
        self.number_word.setGeometry(220,100,30,30)
        self.number_word.setAlignment(Qt.AlignCenter)
        # self.number_word.textChanged.connect(self.sizeEdit)

        self.up_btn = QPushButton(self)
        self.up_btn.setText("+")
        self.up_btn.setGeometry(260,100,15,15)
        self.up_btn.clicked.connect(self.setNumWordUp)

        self.down_btn = QPushButton(self)
        self.down_btn.setText("-")
        self.down_btn.setGeometry(260, 115, 15, 15)
        self.down_btn.clicked.connect(self.setNumWordDown)

        self.at_size = QRadioButton(self)
        self.at_size.setText("По размеру")
        self.at_size.move(50, 180)

        self.at_lexico = QRadioButton(self)
        self.at_lexico.setText("Лексикографически")
        self.at_lexico.setGeometry(50,200,130,20)

        self.formatter_btn = QPushButton(self)
        self.formatter_btn.setText("Форматировать")
        self.formatter_btn.setGeometry(80, 230, 500, 40)
        self.formatter_btn.setStyleSheet('border-radius: 10; background-color: gray;')
        self.formatter_btn.clicked.connect(self.strFormat)

        self.result_label = QLabel(self)
        self.result_label.setText("Результат:")
        self.result_label.move(10, 290)

        self.result_text = QLineEdit(self)
        self.result_text.setReadOnly(True)
        self.result_text.setGeometry(80,295,500,25)


    def setNumWordUp(self):
        i = 0
        try:
            if self.number_word.text():
                i = int(self.number_word.text()) + 1
                self.number_word.setText(str(i))
            else:
                i = 0 + 1
                self.number_word.setText(str(i))
        except Exception as e:
            print(e)


    def setNumWordDown(self):
        i = 0
        try:
            if self.number_word.text() and int(self.number_word.text()) !=0:
                i = int(self.number_word.text()) - 1
                self.number_word.setText(str(i))
            else:
                i = 0
                self.number_word.setText(str(i))
        except Exception as e:
            print(e)


    def strFormat(self):
        try:
            string = self.string_text.text()

            if self.delete_word.isChecked():
                n = int(self.number_word.text())
                string = StringFormatter.DelWords(string, n)

            if self.change_digits.isChecked():
                string = StringFormatter.ReplaceNum(string)

            if self.insert_space.isChecked():
                string = StringFormatter.CreateSpace(string)

            if self.sort_word.isChecked():

                if self.at_size.isChecked():
                    string = StringFormatter.SortSize(string)
                elif self.at_lexico.isChecked():
                    string = StringFormatter.SortLex(string)

            self.result_text.setText(string)
        except Exception as e:
            print(e)


def Zad5():
    app = QApplication(sys.argv)
    window = Formatter()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    # Zad1()
    # Zad2()
    # Zad3()
    # Zad4()
    Zad5()