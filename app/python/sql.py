from mysql.connector import connect, Error

try:
    with connect(
        host="localhost",
        user="root",
        password="Alcatel1$",
        database="central_lab"
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM links")
            result = cursor.fetchall()

            for row in result:
                print(row)
except Error as e:
    print(e)


