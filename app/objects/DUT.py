import json
from mysql.connector import connect, Error
from .Link import Link
from python.cli import change_banner, clean_dut



class DUT:
    def __init__(self, id):
        try:
            connection = connect(
                host="10.255.120.133",
                user="admin",
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
        self.selected = False

        connection.close()

    def serialize(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    

    def unlink(self):
        try:
            connection = connect(
                host="10.255.120.133",
                user="admin",
                password="Alcatel1$",
                database="central_lab"
            )
        except Error as e:
            print(e)
            return False

        cursor = connection.cursor()
        cursor.execute("SELECT id FROM links WHERE dut = %s", (self.id,))
        result = cursor.fetchall()

        for id in result:
            Link(id[0]).deleteService()



        cursor.execute("UPDATE dut SET reserv_id = NULL WHERE id = %s", (self.id,))
        connection.commit()
        connection.close()

        change_banner(self.ip, 'nobody')
        clean_dut(self.ip)

        return True

    def link(self, reservation):
        try:
            connection = connect(
                host="10.255.120.133",
                user="admin",
                password="Alcatel1$",
                database="central_lab"
            )
        except Error as e:
            print(e)
            return False

        cursor = connection.cursor()
        cursor.execute("UPDATE dut SET reserv_id = %s WHERE id = %s", (reservation, self.id,))
        connection.commit()

        self.reserv_id = reservation
        
        cursor.execute('SELECT creator FROM reservations WHERE id = %s', (self.reserv_id, ))
        result = cursor.fetchone()

        change_banner(self.ip, result[0])
        connection.close()


        return True


    
    @staticmethod
    def deserialize(json_data):
        return(json.loads(json_data))


    @staticmethod
    def getDUTs(reserv_id):
        try:
            connection = connect(
                host="10.255.120.133",
                user="admin",
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
                host="10.255.120.133",
                user="admin",
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
