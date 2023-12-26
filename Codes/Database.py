import psycopg2
import datetime
import os
from dotenv import load_dotenv
import pytz

COST = 5990


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
        self.cursor.execute(
            "SELECT client.id, client.username, client.last_visit, partner.name, client.points FROM client LEFT JOIN partner ON client.referral_id=partner.id;")
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
        discount_rank = self.cursor.fetchone()[0]
        self.cursor.execute(f"""SELECT SUM(discount) FROM achievements 
        INNER JOIN client_achievements ON achievements.id=client_achievements.achievements_id 
        WHERE  client_achievements.client_id= {user[0]};""")
        discount_achievements = self.cursor.fetchone()[0]  # (3,) tuple
        if discount_achievements is not None:
            payment = COST * (1 - (discount_achievements + discount_rank) * 0.01)
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
            f"""SELECT 
    office_hours.time, 
    COALESCE(p.client_id, office_hours.client_id) as client_id,
    client.username, 
    office_hours.recording 
FROM 
    office_hours 
JOIN 
    teacher ON office_hours.teacher_id = teacher.id 
LEFT JOIN 
    (SELECT id, client_id FROM purchases WHERE id IS NOT NULL) p ON office_hours.purchases_id = p.id
JOIN 
    client ON client.id = COALESCE(p.client_id, office_hours.client_id)
WHERE 
    teacher.name = '{teacher}'
    ORDER BY office_hours.time DESC;
"""
        )
        result = self.cursor.fetchall()
        if month is not None or year is not None:
            return [
                lesson
                for lesson in result
                if lesson[0].month == month + 1 and lesson[0].year == year
            ]
        return result

    def fetch_all_data(self):
        query = """
        SELECT p.id, p.client_id, p.finish_date, p.tariff,
               c.username, c.points, c.last_visit,
               t.office_hours, COALESCE(oh.hours_used, 0) as hours_used
        FROM purchases p
        JOIN client c ON p.client_id = c.id
        LEFT JOIN tariff t ON p.tariff = t.name
        LEFT JOIN (
            SELECT purchases_id, COUNT(*) as hours_used
            FROM office_hours
            GROUP BY purchases_id
        ) oh ON p.id = oh.purchases_id
        WHERE p.finish_date > %s
        ORDER BY c.last_visit DESC
        """
        current_time = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
        self.cursor.execute(query, (current_time,))
        return self.cursor.fetchall()

    def get_office_hours(self, purchase_id):
        self.cursor.execute(f"""SELECT COUNT(purchases_id) FROM office_hours WHERE purchases_id={purchase_id}""")
        return self.cursor.fetchone()[0]



