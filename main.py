from PyQt6.QtWidgets import QApplication
from transliterate import translit
from Codes.Attendance import Attendance
from Codes.Authorization import Authorization
from Codes.Menu import Menu
from Codes.OfficeHours import OfficeHours
from Codes.OfficeHoursStaff import OfficeHoursStaff
from Codes.Payments import Payments
from Codes.path import resource_path

win = QApplication([])
menu = Menu()

def showFirstWindow(authorization):
    try:
        with open(resource_path("authorizationInfo.txt"), "r", encoding="UTF-8") as f:
            filelines = f.readlines()
    except:
        open(resource_path("authorizationInfo.txt"), "w")
        filelines = ""

    if (
        filelines
        and menu.db.getAuthorizationInfo(filelines[0].strip(), filelines[1].strip())
        is not None
    ):
        menu.form.helloMessage.setText(
            f'Hello, {translit(filelines[2], "ru", reversed=True)}'
        )
        menu.show()
    else:
        authorization.show()


def createWindows():
    attendance = Attendance()
    authorization = Authorization()
    payments = Payments()
    officeHours = OfficeHours()
    officeHoursStaff = OfficeHoursStaff()
    return authorization


if __name__ == "__main__":
    showFirstWindow(createWindows())

    win.exec()
