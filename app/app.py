import hashlib
from flask import Flask, render_template, request, redirect, url_for, session
from mysql.connector import connect, Error

from objects.DUT import DUT
from objects.Reservation import Reservation

app = Flask(__name__)

try:
    connection = connect(
        host="localhost",
        user="root",
        password="Alcatel1$",
        database="central_lab"
    )
except Error as e:
    print(e)

app.secret_key = 'Letacla01*'


@app.route("/", methods=['GET', 'POST'])
def index():
    return redirect(url_for("reservation"))


@app.route("/reservation", methods=['GET', 'POST'])
def reservation():
    try :
        if session['loggedin'] == True:
            pass
    except KeyError:
        return redirect(url_for("login"))

    
    reservations = Reservation.getReservations(session['username'])
    availables = DUT.getAvailable()


    try:
        used = DUT.getDUTs(session["reservation"])
        reservations[int(session["reservation"])].selected = True
    except KeyError:
        if len(list(reservations.keys())) > 0:
            session["reservation"] = list(reservations.keys())[0] # Select the 1st id of the list
            used = DUT.getDUTs(session["reservation"])
            reservations[int(session["reservation"])].selected = True
        else:
            used = {}
            reservations = {}


    if request.method == 'GET':
        return render_template("reservation.html", reservations=[(k, v.name, v.selected) for (k, v) in reservations.items()],  equipments=[(k, v.model, v.ip, v.console) for (k, v) in used.items()], available_equipment=[(k, v.model) for (k, v) in availables.items()])
    
        # Reservation form username / ID etc..;
    elif request.method == 'POST':
        if 'form_control' in request.form:
            if request.form['form_control'] == "make_reservation":
                cursor = connection.cursor()
                cursor.execute('INSERT INTO reservations (duration, creator, name, purpose) VALUES (%s, %s, %s, %s)', (request.form['duration'], session["username"], request.form['name'],request.form['purpose'],))
                connection.commit()
            elif request.form['form_control'] == "select_reservation":
                if request.form['button_reservation'] == "delete":
                    # delete DUT of reservation
                    
                    cursor = connection.cursor()
                    cursor.execute("UPDATE dut SET reserv_id = NULL WHERE reserv_id = %s", (request.form['current_reservation'],))
                    connection.commit()
                    # delete reservatiom
                    cursor = connection.cursor()
                    cursor.execute("DELETE FROM reservations WHERE id = %s", (request.form['current_reservation'],))
                    connection.commit()
                    return redirect(url_for('reservqtion'))
                else:
                    # show reserved equipements
                    reservations[int(session["reservation"])].selected = False
                    session["reservation"] = request.form['current_reservation']
                    reservations[int(session["reservation"])].selected = True
                    used = DUT.getDUTs(session["reservation"])
                    return render_template("reservation.html", reservations=[(k, v.name, v.selected) for (k, v) in reservations.items()], equipments=[(k, v.model, v.ip, v.console) for (k, v) in used.items()], available_equipment=[(k, v.model) for (k, v) in availables.items()])

            elif request.form['form_control'] == "delete_equipment":
                cursor = connection.cursor()
                cursor.execute("UPDATE dut SET reserv_id = NULL WHERE id = %s", (request.form['equipment'],))
                connection.commit()
            elif request.form['form_control'] == "add_equipment":
                cursor = connection.cursor()
                cursor.execute("UPDATE dut SET reserv_id = %s WHERE id = %s", (str(session["reservation"]), request.form['equipment'],))
                connection.commit()


    return redirect(url_for("reservation"))

    


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Retrieve the hashed password
        hash = password + app.secret_key
        hash = hashlib.sha1(hash.encode())
        password = hash.hexdigest()
        # Check if account exists using MySQL
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return the result
        account = cursor.fetchone()
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['username'] = account[0]
            # Redirect to home page
            return redirect(url_for('index'))
        
    return render_template('login.html', alert=True)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
            # Create variables for easy access
        username = request.form['username']
        password = request.form['password']

        # Check if account exists using MySQL
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            return render_template('register.html', alert2=True)
        else:
            # Hash the password
            hash = password + app.secret_key
            hash = hashlib.sha1(hash.encode())
            password = hash.hexdigest()
            # Account doesn't exist, and the form data is valid, so insert the new account into the accounts table
            cursor.execute('INSERT INTO users VALUES (%s, %s)', (username, password,))
            connection.commit()
            return render_template('register.html', success=True)
    else:
        return render_template('register.html', alert=True)



@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('user', None)
   # Redirect to login page
   return redirect(url_for('login'))




if __name__ == "__main__":
    app.run(port=80)