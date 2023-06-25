import psycopg2
import datetime
import os
from dotenv import load_dotenv
import pytz

COST = 4900


class Database:
    def __init__(self):
        load_dotenv()
        self.db = psycopg2.connect(
            database=os.getenv("DATABASE"),
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD"),
            host=os.getenv("HOST"),
            port=os.getenv("PORT"),
        )
        self.cursor = self.db.cursor()

    def getAdmins(self):
        return list(map(int, (os.getenv("ADMINIDS").split(', '))))

    def getAttendance(self, dateFrom: datetime.date, dateTo: datetime.date):
        self.cursor.execute("SELECT client.id, client.username, client.last_visit, partner.name FROM client LEFT JOIN partner ON client.referral_id=partner.id;")
        result = self.cursor.fetchall()
        result1 = []
        for i in result:
            if i[2].date() >= dateFrom and i[2].date() <= dateTo:
                result1.append(i)
        return result1

    def getUsers(self, filter=None):
        self.cursor.execute("SELECT id, username FROM client;")
        result = self.cursor.fetchall()
        result1 = []
        if filter == None:
            return result
        for user in result:
            if (
                filter.lower() in str(user[0]).lower()
                or user[1] is not None
                and filter.lower() in user[1].lower()
            ):
                result1 += [user]
        return result1

    def getPaymentInfo(self, id=None, username=None):
        if id is not None:
            self.cursor.execute(
                f"SELECT id, username, rank FROM client WHERE id = {id};"
            )
        elif username is not None:
            self.cursor.execute(
                f"SELECT id, username, rank FROM client WHERE username = '{username}';"
            )
        else:
            raise Exception("Type username or id")

        user = self.cursor.fetchone()
        if len(user) == 0:
            raise Exception("No data found")

        self.cursor.execute(f"SELECT discount FROM rank WHERE name = '{user[2]}';")
        discount_rank=self.cursor.fetchone()[0]
        self.cursor.execute(f"""SELECT SUM(discount) FROM achievements 
        INNER JOIN client_achievements ON achievements.id=client_achievements.achievements_id 
        WHERE  client_achievements.client_id= {user[0]};""")
        discount_achievements = self.cursor.fetchone()[0]  # (3,) tuple
        if discount_achievements is not None:
            payment = COST * (1 - (discount_achievements+discount_rank) * 0.01)
        else:
            payment = COST * (1 - discount_rank * 0.01)
        return user[0], user[1], payment

    def getAuthorizationInfo(self, login, password):
        if login and password:
            self.cursor.execute(
                f"SELECT username, id, name FROM teacher WHERE id = {password} AND username = '{login}';"
            )
            user = self.cursor.fetchone()
            return user
        else:
            return None

    def getTeachers(self):
        self.cursor.execute("SELECT distinct teacher_id FROM office_hours;")
        teachersID = self.cursor.fetchall()
        teachers = []
        for teacher in teachersID:
            self.cursor.execute(f"SELECT name FROM teacher WHERE id={teacher[0]};")
            teachers.append(self.cursor.fetchone()[0])
        return teachers

    def getTeacher(self, id):
        self.cursor.execute(f"SELECT name  FROM teacher WHERE id={int(id[:-1])};")
        return self.cursor.fetchone()[0]

    def getOfficeHoursByTeacher(self, teacher, month=None, year=None):
        self.cursor.execute(
            f"""SELECT office_hours."time", client.id, client.username, office_hours.recording 
        FROM office_hours 
        JOIN teacher ON office_hours.teacher_id = teacher.id 
        JOIN purchases ON purchases.id = office_hours.purchases_id 
        JOIN client ON client.id = purchases.client_id 
        WHERE teacher.name = '{teacher}';"""
        )
        result = self.cursor.fetchall()
        if month is not None or year is not None:
            return [
                lesson
                for lesson in result
                if lesson[0].month == month + 1 and lesson[0].year == year
            ]
        return result

    def getPurchasesExpDays(self):
        self.cursor.execute("""SELECT id, finish_date,client_id FROM purchases """)
        purchases=self.cursor.fetchall()
        purchases_exp_days=[]
        for purchase_id, finish_date, client_id in purchases:
            if finish_date>datetime.datetime.utcnow().replace(tzinfo=pytz.UTC):
                purchases_exp_days.append([purchase_id, client_id,(finish_date-datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)).days])
        return purchases_exp_days

    def getClientUsernameById(self, id):
        self.cursor.execute(f"""SELECT username FROM client WHERE id={id}""")
        return self.cursor.fetchone()[0]

    def getExpHours(self,purchases_id):
        self.cursor.execute(f"""SELECT tariff FROM purchases WHERE id={purchases_id}""")
        tariff=self.cursor.fetchone()[0]
        data=tariff.split(" | ")
        hours=0
        for i in range(len(data)):
            self.cursor.execute(f"""SELECT office_hours FROM tariff WHERE name='{data[i]}'""")
            hours+=self.cursor.fetchone()[0]
        self.cursor.execute(f"""SELECT COUNT(purchases_id) FROM office_hours WHERE purchases_id={purchases_id}""")
        return hours-self.cursor.fetchone()[0]






