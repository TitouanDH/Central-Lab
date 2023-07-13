import json
from mysql.connector import connect, Error



class DUT:
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
        cursor.execute('SELECT * FROM dut WHERE id = %s', (id, ))
        result = cursor.fetchone()
        print()
        self.ip = result[1]
        self.model = result[2]
        self.console = result[3]
        self.reserv_id = result[4]

        connection.close()

    def serialize(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    
    @staticmethod
    def deserialize(json_data):
        return(json.loads(json_data))


    @staticmethod
    def getDUTs(reserv_id):
        try:
            connection = connect(
                host="localhost",
                user="root",
                password="Alcatel1$",
                database="central_lab"
            )
        except Error as e:
            print(e)

        duts = {}
        cursor = connection.cursor()
        cursor.execute('SELECT id FROM dut WHERE reserv_id = %s', (reserv_id, ))
        result = cursor.fetchall()


        for id in result:
            duts[id[0]] = DUT(id[0])

        connection.close()
        return duts
    
    @staticmethod
    def getAvailable():
        try:
            connection = connect(
                host="localhost",
                user="root",
                password="Alcatel1$",
                database="central_lab"
            )
        except Error as e:
            print(e)

        duts = {}
        cursor = connection.cursor()
        cursor.execute('SELECT id FROM dut WHERE reserv_id IS NULL')
        result = cursor.fetchall()


        for id in result:
            duts[id[0]] = DUT(id[0])

        connection.close()
        return duts