import datetime

import pytz
from PyQt6 import QtGui

from Codes.window import Window

from PyQt6.QtWidgets import QTableWidgetItem


class Purchases(Window):
    def __init__(self):
        super().__init__("Purchases", r"Designs\Purchases.ui")
        self.form.backToMenu.clicked.connect(self.showBackToMenu)

    def fill(self):
        data_list = self.db.fetch_all_data()
        self.form.tablePurchases.clearContents()
        self.form.tablePurchases.setRowCount(len(data_list))

        for i, data in enumerate(data_list):
            self.populate_table_row(i, data)

    def populate_table_row(self, row_index, data):
        purchase_id, client_id, finish_date, tariff, client_name, points, last_visit, office_hours, hours_used = data

        moscow_tz = pytz.timezone('Europe/Moscow')
        last_visit_moscow = last_visit.astimezone(moscow_tz)

        days_remaining = (finish_date - datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)).days
        hours, is_real, addition_hours = self.calculate_hours_and_real_status(tariff, office_hours, hours_used)

        items = [
            QTableWidgetItem(str(client_id)),
            QTableWidgetItem(str(client_name)),
            QTableWidgetItem(str(days_remaining)),
            QTableWidgetItem(str(hours)),
            QTableWidgetItem(str(points)),
            QTableWidgetItem(last_visit_moscow.strftime("%d.%m.%y %H:%M")),
            QTableWidgetItem(str(addition_hours))
        ]

        if is_real:
            for item in items:
                item.setBackground(QtGui.QColor(153, 255, 153))

        for col, item in enumerate(items):
            self.form.tablePurchases.setItem(row_index, col, item)

    def calculate_hours_and_real_status(self, tariff, office_hours, hours_used):
        is_real = tariff in ["Подписка PILOT", "Подписка MEDIUM", "Подписка PRO", "Детский"]
        if office_hours is None:
            office_hours = 0
        hours = office_hours - hours_used
        addition_hours = sum(int(part.split()[0][1:]) for part in tariff.split(" | ")[1:]) if '|' in tariff else 0

        if hours < 0:
            addition_hours += hours
            hours = 0

        return hours, is_real, addition_hours

    def showBackToMenu(self):
        Window.windows["Menu"]["window"].show()
        self.hide()
