import datetime

import pytz
from PyQt6.QtWidgets import QTableWidgetItem

from Codes.window import Window


class OfficeHours(Window):
    def __init__(self):
        super().__init__("OfficeHours", r"Designs\OfficeHours.ui")
        self.form.backToMenu.clicked.connect(self.showBackToMenu)
        self.form.byMonthButton.toggled.connect(self.mainMethod)
        self.form.allButton.toggled.connect(self.mainMethod)
        for teacher in self.db.getTeachers():
            self.form.teacherList.addItem(teacher)
        for i in reversed(range(2022, datetime.datetime.now().year + 1)):
            self.form.yearList.addItem(str(i))
        self.form.monthList.hide()
        self.form.yearList.hide()
        self.form.withoutRecButton.toggled.connect(self.mainMethod)
        self.form.monthList.currentIndexChanged.connect(self.mainMethod)
        self.form.yearList.currentIndexChanged.connect(self.mainMethod)
        self.form.teacherList.currentIndexChanged.connect(self.mainMethod)
        self.form.allButton.setChecked(True)
        self.form.monthList.setCurrentIndex(datetime.datetime.now().month - 1)

    def mainMethod(self):
        self.form.resultTable.clearContents()
        self.form.resultTable.setRowCount(0)
        self.form.resultTable.setColumnCount(4)
        if self.form.allButton.isChecked():
            self.form.monthList.hide()
            self.form.yearList.hide()
            result = Window.db.getOfficeHoursByTeacher(
                self.form.teacherList.currentText()
            )

        else:
            self.form.monthList.show()
            self.form.yearList.show()
            month = self.form.monthList.currentIndex()
            year = int(self.form.yearList.currentText())
            result = Window.db.getOfficeHoursByTeacher(
                self.form.teacherList.currentText(), month=month, year=year
            )
        moscow_tz = pytz.timezone('Europe/Moscow')
        for i, elem in enumerate(result):
            moscow_time = elem[0].astimezone(moscow_tz) if elem[0] else None

            if (
                    elem[3] is None
                    and self.form.withoutRecButton.isChecked()
                    or not self.form.withoutRecButton.isChecked()
            ):
                self.form.resultTable.setRowCount(self.form.resultTable.rowCount() + 1)

                date = QTableWidgetItem(moscow_time.strftime("%d-%m-%y %H:%M") if moscow_time else '')
                self.form.resultTable.setItem(i, 0, date)
                client_id = QTableWidgetItem(str(elem[1]))
                self.form.resultTable.setItem(i, 1, client_id)
                if elem[2] is not None:
                    client_username = QTableWidgetItem(str(elem[2]))
                    self.form.resultTable.setItem(i, 2, client_username)
                if elem[3] is not None:
                    recording = QTableWidgetItem(str(elem[3]))
                    self.form.resultTable.setItem(i, 3, recording)

    def byMonthPressed(self):
        self.form.monthList.show()
        self.form.yearList.show()

    def allPressed(self):
        self.form.monthList.hide()
        self.form.yearList.hide()
        self.form.resultTable.setColumnCount(4)
        result = Window.db.getOfficeHoursByTeacher(self.form.teacherList.currentText())
        self.form.resultTable.setRowCount(len(result))

        for i, elem in enumerate(result):
            if (
                elem[3] is None
                and self.form.withoutRecButton.isChecked()
                or not self.form.withoutRecButton.isChecked()
            ):
                date = QTableWidgetItem(str(elem[0].strftime("%d-%m-%y %H:%M")))
                self.form.resultTable.setItem(i, 0, date)
                client_id = QTableWidgetItem(str(elem[1]))
                self.form.resultTable.setItem(i, 1, client_id)
                if elem[2] is not None:
                    client_username = QTableWidgetItem(str(elem[2]))
                    self.form.resultTable.setItem(i, 2, client_username)
                if elem[3] is not None:
                    recording = QTableWidgetItem(str(elem[3]))
                    self.form.resultTable.setItem(i, 3, recording)

    def showBackToMenu(self):
        Window.windows["Menu"]["window"].show()
        self.hide()
