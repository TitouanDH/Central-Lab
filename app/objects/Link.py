import json
from mysql.connector import connect, Error

class Link:
    def __init__(self, core_infos):
        try:
            connection = connect(
                host="localhost",
                user="root",
                password="Alcatel1$",
                database="central_lab"
            )
        except Error as e:
            print(e)

        self.core_ip = core_infos[0]
        self.core_port = core_infos[1]

        cursor = connection.cursor()
        cursor.execute('SELECT * FROM link WHERE core_ip = %s AND core_port = %s', (self.core_ip, self.core_port ,))
        result = cursor.fetchone()
        print()
        connection.close()

    def serialize(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    
    @staticmethod
    def deserialize(json_data):
        return(json.loads(json_data))


    @staticmethod
    def getLinks(dut):
        try:
            connection = connect(
                host="localhost",
                user="root",
                password="Alcatel1$",
                database="central_lab"
            )
        except Error as e:
            print(e)

        links = {}
        cursor = connection.cursor()
        cursor.execute('SELECT id FROM link WHERE dut = %s', (dut, ))
        result = cursor.fetchall()


        for id in result:
            links[id[0]] = Link(id[0])

        connection.close()
        return links
