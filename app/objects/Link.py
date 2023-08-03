import json
from mysql.connector import connect, Error

class Link:
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
        cursor.execute('SELECT * FROM links WHERE id = %s', (self.id ,))
        result = cursor.fetchone()

        self.core_ip = result[1]
        self.core_port = result[2]
        self.dut = result[3]
        self.dut_port = result[4]
        self.service = result[5]
        self.selected = False
        connection.close()

    def serialize(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    
    def updateService(self, service):
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
        cursor.execute("UPDATE links SET service = %s WHERE id = %s", (service, self.id,))
        connection.commit()
        connection.close()

        return True
    

    def deleteService(self):
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
        cursor.execute("UPDATE links SET service = NULL WHERE id = %s", (self.id,))
        connection.commit()
        connection.close()

        return True


    
    @staticmethod
    def deserialize(json_data):
        return(json.loads(json_data))


    @staticmethod
    def getLinks(dut):
        try:
            connection = connect(
                host="10.255.120.133",
                user="admin",
                password="Alcatel1$",
                database="central_lab"
            )
        except Error as e:
            print(e)

        links = {}
        cursor = connection.cursor()
        cursor.execute('SELECT id FROM links WHERE dut = %s', (dut, ))
        result = cursor.fetchall()


        for id in result:
            links[id[0]] = Link(id[0])

        connection.close()
        return links
