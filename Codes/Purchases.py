from Codes.window import Window

from PyQt6.QtWidgets import QTableWidgetItem

class Purchases(Window):
    def __init__(self):
        super().__init__("Purchases", r"Designs\Purchases.ui")
        self.form.backToMenu.clicked.connect(self.showBackToMenu)


    def fill(self):
        data_list_exp_days=self.db.getPurchasesExpDays()
        print(data_list_exp_days)
        self.form.tablePurchases.clearContents()
        self.form.tablePurchases.setColumnCount(6)
        self.form.tablePurchases.setRowCount(len(data_list_exp_days))
        last_visit_day_sort = []
        for i, (purchases_id, client_id, days) in enumerate(data_list_exp_days):
            client_name=self.db.getClientUsernameById(client_id)
            hours=self.db.getExpHours(purchases_id)
            points, last_visit = self.db.getPointsAndLastvisit(client_id)
            last_visit_day_sort.append((client_id, client_name, days, hours, points, last_visit))
        last_visit_day_sort = sorted(last_visit_day_sort, key=lambda x: x[5], reverse=True)
        for i, (client_id, client_name, days, hours, points, last_visit) in enumerate(last_visit_day_sort):
            self.form.tablePurchases.setItem(i, 0,QTableWidgetItem(str(client_id)))
            self.form.tablePurchases.setItem(i, 1, QTableWidgetItem(str(client_name)))
            self.form.tablePurchases.setItem(i, 2, QTableWidgetItem(str(days)))
            self.form.tablePurchases.setItem(i, 3, QTableWidgetItem(str(hours)))
            self.form.tablePurchases.setItem(i, 4, QTableWidgetItem(str(points)))
            self.form.tablePurchases.setItem(i, 5, QTableWidgetItem(str(last_visit.strftime("%d.%m.%y %H:%M"))))


    def showBackToMenu(self):
        Window.windows["Menu"]["window"].show()
        self.hide()

















