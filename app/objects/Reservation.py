import json
from mysql.connector import connect, Error


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

        self.duration = result[1]
        self.creator = result[2]
        self.name = result[3]
        self.purpose = result[4]

        self.selected = False
        connection.close()


    def serialize(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    
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

