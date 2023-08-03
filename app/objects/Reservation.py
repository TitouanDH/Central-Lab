import json
from mysql.connector import connect, Error
import datetime


class Reservation:
    def __init__(self, id):
        try:
            connection = connect(
                host="localhost",
                user="root",
                password="Alcatel1$",
                database="central_lab"
            )
        except Error as e:
            print(e)
        self.id = id
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM reservations WHERE id = %s', (id, ))
        result = cursor.fetchone()
        print()

        self.end = result[1]
        self.creator = result[2]
        self.name = result[3]
        self.purpose = result[4]

        self.selected = False
        connection.close()


    def serialize(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    

    def delete(self):
        try:
            connection = connect(
                host="localhost",
                user="root",
                password="Alcatel1$",
                database="central_lab"
            )
        except Error as e:
            print(e)
            return False

        cursor = connection.cursor()
        cursor.execute("UPDATE dut SET reserv_id = NULL WHERE reserv_id = %s", (self.id,))
        connection.commit()
        # delete reservatiom
        cursor = connection.cursor()
        cursor.execute("DELETE FROM reservations WHERE id = %s", (self.id,))
        connection.commit()
        connection.close()

        return True
    

    @staticmethod
    def new(duration,username, name, purpose):
        try:
            connection = connect(
                host="localhost",
                user="root",
                password="Alcatel1$",
                database="central_lab"
            )
        except Error as e:
            print(e)
            return False
        
        end = datetime.datetime.now() + datetime.timedelta(hours=int(duration))

        cursor = connection.cursor()
        cursor.execute('INSERT INTO reservations (end, creator, name, purpose) VALUES (%s, %s, %s, %s)', (end,username, name, purpose,))
        connection.commit()
        connection.close()

        return True


    
    @staticmethod
    def deserialize(json_data):
        return(json.loads(json_data))

    @staticmethod
    def getReservations(creator):
        try:
            connection = connect(
                host="localhost",
                user="root",
                password="Alcatel1$",
                database="central_lab"
            )
        except Error as e:
            print(e)
        reservations = {}
        cursor = connection.cursor()
        cursor.execute('SELECT id FROM reservations WHERE creator = %s', (creator, ))
        result = cursor.fetchall()


        for id in result:
            reservations[id[0]] = Reservation(id[0])

        connection.close()
        return reservations


    @staticmethod
    def getAllReservations():
        try:
            connection = connect(
                host="localhost",
                user="root",
                password="Alcatel1$",
                database="central_lab"
            )
        except Error as e:
            print(e)
        reservations = {}
        cursor = connection.cursor()
        cursor.execute('SELECT id FROM reservations')
        result = cursor.fetchall()


        for id in result:
            reservations[id[0]] = Reservation(id[0])

        connection.close()
        return reservations
