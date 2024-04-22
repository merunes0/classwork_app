# Git) - https://github.com/merunes0
# Imports

import sys
import json
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, \
    QWidget, QTreeWidget, QTreeWidgetItem, QInputDialog, QDialog, QHeaderView, QComboBox, QLabel
from PySide6.QtCore import QDateTime, Qt, QUrl
from PySide6.QtWidgets import QDateTimeEdit
from PySide6 import QtCore
from PySide6.QtGui import QDesktopServices, QColor, QBrush
from datetime import datetime
from environs import Env

# Environs
env = Env()
env.read_env()
ONE_MILLION_DOLLARS_HACK = env("ONE_MILLION_DOLLARS_HACK")


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Виджеты
        self.treeWidget = QTreeWidget()
        self.treeWidget.setHeaderLabels(["Предмет", "Задание", "Дедлайн", "Тип Задания"])

        # Кнопки
        self.pushButton = QPushButton("Добавить задание")
        self.button_delete_task = QPushButton("Удалить задание")

        # Лейаут
        layout = QVBoxLayout()
        layout.addWidget(self.treeWidget)
        layout.addWidget(self.pushButton)
        layout.addWidget(self.button_delete_task)

        # Установка размера окна по умолчанию
        self.resize(550, 550)

        # Ссылочка
        self.link_label = QLabel(f"<a href='{ONE_MILLION_DOLLARS_HACK}'>Стань доллоровым миллионером 2024 гайд</a>")
        self.link_label.setStyleSheet("color: rgba(128, 128, 128, 220);")
        layout.addWidget(self.link_label)
        layout.setAlignment(self.link_label, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)

        # Мейн виджет
        main_widget = QWidget()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

        # Коннекты
        self.pushButton.clicked.connect(self.add_task)
        self.treeWidget.itemDoubleClicked.connect(self.change_column)
        self.button_delete_task.clicked.connect(self.delete_selected_tasks)  # Подключаем обработчик удаления заданий
        self.treeWidget.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.link_label.linkActivated.connect(self.openLink)

        # Загрузка конфига
        self.load_tasks_cfg()

    # Метод для добавления задания в список
    def add_task(self):
        subject_text, ok = QInputDialog.getText(self, "Добавить предмет", "Введите название предмета:")
        if ok and subject_text:
            task_text, ok = QInputDialog.getText(self, "Добавить задание", "Введите задание:")
            if ok and task_text:
                combo_box = QComboBox()
                combo_box.addItems(["Контрольная работа", "С.Р"])
                item = QTreeWidgetItem([subject_text, task_text, datetime.now().strftime("%Y-%m-%d")])
                self.treeWidget.addTopLevelItem(item)
                self.treeWidget.setItemWidget(item, 3, combo_box)  # Устанавливаем ComboBox в колонку 3

    # Метод Сохранения конфига при выходе (.json)
    def save_tasks(self):
        tasks = []
        for i in range(self.treeWidget.topLevelItemCount()):
            item = self.treeWidget.topLevelItem(i)
            subject = item.text(0)
            task = item.text(1)
            date = item.text(2)
            task_type_combo_box = self.treeWidget.itemWidget(item, 3)
            task_type = task_type_combo_box.currentText()
            text_color = item.foreground(2).color().name()
            tasks.append({"subject": subject, "task": task, "date": date, "task_type": task_type, "text_color":text_color})

        with open("cfg/tasks.json", "w") as f:
            json.dump(tasks, f)

    # Метод загрузки конфига
    def load_tasks_cfg(self):
        try:
            with open("cfg/tasks.json", "r") as f:
                tasks = json.load(f)
                for task in tasks:
                    subject = task["subject"]
                    task_text = task["task"]
                    date = task["date"]
                    task_type = task["task_type"]
                    text_color = task["text_color"]

                    item = QTreeWidgetItem([subject, task_text, date, task_type, text_color])
                    self.treeWidget.addTopLevelItem(item)

                    #Цвета
                    color = QColor(text_color)
                    brush = QBrush(color)
                    item.setForeground(2, brush)

                    combo_box = QComboBox()
                    combo_box.addItems(["Контрольная работа",
                                        "Самостоятельная работа",
                                        "Домашнее задание",])
                    combo_box.setCurrentText(task_type)
                    self.treeWidget.setItemWidget(item, 3, combo_box)

        except FileNotFoundError:
            pass

    # Метод для удаления выбранных заданий
    def delete_selected_tasks(self):
        selected_items = self.treeWidget.selectedItems()
        for item in selected_items:
            (item.parent() or self.treeWidget.invisibleRootItem()).removeChild(item)

    # Метод возможности изменения столбцов (по дабл клику)
    def change_column(self, item, column):
        if column == 0:
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.adjust_task_text(item, column)
            self.treeWidget.editItem(item, column)
        elif column == 1:
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.adjust_task_text(item, column)
            self.treeWidget.editItem(item, column)
        elif column == 3:
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.adjust_task_text(item, column)
            self.treeWidget.editItem(item, column)
            # Изменение даты
        elif column == 2:  #
            current_date = QDateTime.fromString(item.text(column), "yyyy-MM-dd")
            date_edit = QDateTimeEdit(current_date, self)
            date_edit.setCalendarPopup(True)
            date_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")

            dialog = QDialog(self)
            layout = QVBoxLayout()
            layout.addWidget(date_edit)

            button_yes = QPushButton("Подтвердить изменения")
            button_yes.clicked.connect(dialog.accept)
            layout.addWidget(button_yes)

            dialog.setLayout(layout)

            if dialog.exec_():
                new_date = date_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
                item.setText(column, new_date)

                # Проверка времени до дедлайна
                deadline = QDateTime.fromString(new_date, "yyyy-MM-dd HH:mm:ss")
                current_datetime = QDateTime.currentDateTime()
                difference_seconds = current_datetime.secsTo(deadline)
                days_difference = difference_seconds // (24 * 3600)

                # Установка цвета текста в зависимости от времени до дедлайна
                if days_difference > 1:
                    dark_green = QColor(0, 100, 0, 255)
                    item.setForeground(column, dark_green)
                else:
                    item.setForeground(column, Qt.red)

    # Метод перехода на новую строку если кол/во символов > 50 (Работает в связке с change_column)
    def adjust_task_text(self, item, column):
        if column == 1:
            task_text = item.text(1)
            if len(task_text) > 50:
                lines = [task_text[i:i+50] for i in range(0, len(task_text), 50)]
                item.setText(1, "\n".join(lines))

    def openLink(self, url):
        QDesktopServices.openUrl(QUrl(url))

    # Переопределение метода closeEvent для сохранения заданий перед выходом
    def closeEvent(self, event):
        self.save_tasks()
        event.accept()


# Запуск
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())