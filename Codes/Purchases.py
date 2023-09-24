from PyQt6 import QtGui

from Codes.window import Window

from PyQt6.QtWidgets import QTableWidgetItem


class Purchases(Window):
    def __init__(self):
        super().__init__("Purchases", r"Designs\Purchases.ui")
        self.form.backToMenu.clicked.connect(self.showBackToMenu)

    def fill(self):
        data_list_exp_days = self.db.getPurchasesExpDays()
        self.form.tablePurchases.clearContents()
        self.form.tablePurchases.setColumnCount(7)
        self.form.tablePurchases.setRowCount(len(data_list_exp_days))
        last_visit_day_sort = []
        for i, (purchases_id, client_id, days) in enumerate(data_list_exp_days):
            client_name, points, last_visit = self.db.getUsernamePointsLastVisit(client_id)
            hours, is_real, addition_hours = self.db.getExpHours(purchases_id)
            last_visit_day_sort.append(
                (client_id, client_name, days, hours, points, last_visit, is_real, addition_hours))
        last_visit_day_sort = sorted(last_visit_day_sort, key=lambda x: x[5], reverse=True)
        for i, (client_id, client_name, days, hours, points, last_visit, is_real, addition_hours) in enumerate(
                last_visit_day_sort):
            client_id_item = QTableWidgetItem(str(client_id))
            client_name_item = QTableWidgetItem(str(client_name))
            days_item = QTableWidgetItem(str(days))
            hours_item = QTableWidgetItem(str(hours))
            points_item = QTableWidgetItem(str(points))
            last_visit_item = QTableWidgetItem(str(last_visit.strftime("%d.%m.%y %H:%M")))
            addition_hours_item = QTableWidgetItem(str(addition_hours))
            if is_real:
                client_id_item.setBackground(QtGui.QColor(153, 255, 153))
                client_name_item.setBackground(QtGui.QColor(153, 255, 153))
                days_item.setBackground(QtGui.QColor(153, 255, 153))
                hours_item.setBackground(QtGui.QColor(153, 255, 153))
                points_item.setBackground(QtGui.QColor(153, 255, 153))
                last_visit_item.setBackground(QtGui.QColor(153, 255, 153))
                addition_hours_item.setBackground(QtGui.QColor(153, 255, 153))

            self.form.tablePurchases.setItem(i, 0, client_id_item)
            self.form.tablePurchases.setItem(i, 1, client_name_item)
            self.form.tablePurchases.setItem(i, 2, days_item)
            self.form.tablePurchases.setItem(i, 3, hours_item)
            self.form.tablePurchases.setItem(i, 4, points_item)
            self.form.tablePurchases.setItem(i, 5, last_visit_item)
            self.form.tablePurchases.setItem(i, 6, addition_hours_item)

    def showBackToMenu(self):
        Window.windows["Menu"]["window"].show()
        self.hide()
