import datetime
import hashlib
from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import datetime


from objects.Link import Link
from objects.DUT import DUT
from objects.Reservation import Reservation
from python.cli import create_tunnel, delete_tunnel



BVLAN = 4000
SERVICE = 4000

app = Flask(__name__)

app.secret_key = 'Letacla01*'


@app.route("/", methods=['GET', 'POST'])
def index():
    return redirect(url_for("reservation"))



@app.route("/connect", methods=['GET', 'POST'])
def connect():
    try :
        if session['loggedin'] == True:
            pass
    except KeyError:
        return redirect(url_for("login"))

    reservations = Reservation.getReservations(session['username'])

    try:
        equipmentsA = DUT.getDUTs(session["reservation"])
        equipmentsB = DUT.getDUTs(session["reservation"])
        reservations[int(session["reservation"])].selected = True
    except KeyError:

        if len(list(reservations.keys())) > 0: #if there is reservations
            session["reservation"] = list(reservations.keys())[0] # Select the 1st id of the list
            equipmentsA = DUT.getDUTs(session["reservation"])
            equipmentsB = DUT.getDUTs(session["reservation"])
            reservations[int(session["reservation"])].selected = True
        else:
            equipmentsA = {}
            equipmentsB = {}
            reservations = {}


    try:
        linka = Link.getLinks(session["equipA"])
        linkb = Link.getLinks(session["equipB"])
        equipmentsA[int(session["equipA"])].selected = True
        equipmentsB[int(session["equipB"])].selected = True
    except KeyError:

        if len(list(equipmentsA.keys())) > 0: #if there is equipments
            session["equipA"] = list(equipmentsA.keys())[0] # Select the 1st id of the list
            session["equipB"] = list(equipmentsB.keys())[0] # Select the 1st id of the list
            equipmentsA[int(session["equipA"])].selected = True
            equipmentsB[int(session["equipB"])].selected = True
            linka = Link.getLinks(session["equipA"])
            linkb = Link.getLinks(session["equipB"])
        else:
            linka = {}
            linkb = {}



    if request.method == 'GET':
        return render_template("connect.html", reservations=[(k, v.name, v.selected) for (k, v) in reservations.items()], equipmentsA=[(k, v.model, v.selected) for (k, v) in equipmentsA.items()], equipmentsB=[(k, v.model, v.selected) for (k, v) in equipmentsB.items()])
    elif request.method == 'POST':
        if 'form_control' in request.form:
            if request.form['form_control'] == "select_reservation":
                reservations[int(session["reservation"])].selected = False
                session["reservation"] = request.form['current_reservation']
                reservations[int(session["reservation"])].selected = True
                equipmentsA = DUT.getDUTs(session["reservation"])
                equipmentsB = DUT.getDUTs(session["reservation"])
                return render_template("connect.html", reservations=[(k, v.name, v.selected) for (k, v) in reservations.items()], equipmentsA=[(k, v.model, v.selected) for (k, v) in equipmentsA.items()], equipmentsB=[(k, v.model, v.selected) for (k, v) in equipmentsB.items()])
            elif request.form['form_control'] == "select_equipments":
                equipmentsA[int(session["equipA"])].selected = False
                equipmentsB[int(session["equipB"])].selected = False
                session["equipA"] = request.form['equipA']
                session["equipB"] = request.form['equipB']
                equipmentsA[int(session["equipA"])].selected = True
                equipmentsB[int(session["equipB"])].selected = True
                linka = Link.getLinks(session["equipA"])
                linkb = Link.getLinks(session["equipB"])
                return render_template("connect.html", reservations=[(k, v.name, v.selected) for (k, v) in reservations.items()], equipmentsA=[(k, v.model, v.selected) for (k, v) in equipmentsA.items()], equipmentsB=[(k, v.model, v.selected) for (k, v) in equipmentsB.items()], linkA=[(k, v.dut_port, v.selected) for (k, v) in linka.items()], linkB=[(k, v.dut_port, v.selected) for (k, v) in linkb.items()])
            elif request.form['form_control'] == "connection":
                portA = Link(request.form['portA'])
                portB = Link(request.form['portB'])

                if request.form['action'] == 'connect':
                    global BVLAN
                    global SERVICE

                    if BVLAN >= 4002:
                        BVLAN = 4000
                    else:
                        BVLAN += 1

                    if SERVICE >= 5000:
                        SERVICE = 4000
                    else:
                        SERVICE += 1

                    if create_tunnel(portA.core_ip, portA.core_port, portB.core_ip, portB.core_port, BVLAN, SERVICE): # if tunnel is created
                        portA.updateService(SERVICE)
                        portB.updateService(SERVICE)
                else:
                    if delete_tunnel(portA.core_ip, portA.core_port, portB.core_ip, portB.core_port, SERVICE): # if tunnel is created
                        portA.deleteService()
                        portB.deleteService()

                return redirect(url_for("connect"))




@app.route("/admin", methods=['GET', 'POST'])
def admin():
    try :
        if session['username'] == 'admin':
            pass
        else:
            return redirect(url_for("login"))   
    except KeyError:
        return redirect(url_for("login"))
    
    reservations = Reservation.getAllReservations()
    reservations_data = []


    if request.method == 'GET':
        for k, v in reservations.items():
            name = v.name
            user = v.creator
            time = v.end
            state = 'active' if time > datetime.datetime.now() else 'dark'
            equipments = DUT.getDUTs(k)
            
            reservations_data.append((k, state, user, name, time, [(k, v.model, v.ip, v.console) for (k, v) in equipments.items()]))

        return render_template("admin.html", reservations=reservations_data)
    
    elif request.method == 'POST':
        if 'form_control' in request.form:
            if request.form['form_control'] == "delete_reservation":
                Reservation(request.form['reservation']).delete()
                return redirect(url_for('admin'))
            elif request.form['form_control'] == "delete_equipment":
                DUT(request.form['equipment']).unlink()
                return redirect(url_for('admin'))


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
                Reservation.new(request.form['duration'], session["username"], request.form['name'],request.form['purpose'])
            elif request.form['form_control'] == "select_reservation":
                if request.form['button_reservation'] == "delete":
                    # delete DUT of reservation
                    Reservation(request.form['current_reservation']).delete()
                    return redirect(url_for('reservation'))
                else:
                    # show reserved equipements
                    reservations[int(session["reservation"])].selected = False
                    session["reservation"] = request.form['current_reservation']
                    reservations[int(session["reservation"])].selected = True
                    used = DUT.getDUTs(session["reservation"])
                    return render_template("reservation.html", reservations=[(k, v.name, v.selected) for (k, v) in reservations.items()], equipments=[(k, v.model, v.ip, v.console) for (k, v) in used.items()], available_equipment=[(k, v.model) for (k, v) in availables.items()])

            elif request.form['form_control'] == "delete_equipment":
                DUT(request.form['equipment']).unlink()
            elif request.form['form_control'] == "add_equipment":
                DUT(request.form['equipment']).link(session["reservation"])


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
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Alcatel1$",
                database="central_lab"
            )
        except mysql.connector.Error as e:
            print(e)

        cursor = connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return the result
        account = cursor.fetchone()
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['username'] = account[0]
            # Redirect to home page
            connection.close()
            return redirect(url_for('index'))
        
    connection.close()    
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
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Alcatel1$",
                database="central_lab"
            )
        except mysql.connector.Error as e:
            print(e)

        cursor = connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            connection.close()
            return render_template('register.html', alert2=True)
        else:
            # Hash the password
            hash = password + app.secret_key
            hash = hashlib.sha1(hash.encode())
            password = hash.hexdigest()
            # Account doesn't exist, and the form data is valid, so insert the new account into the accounts table
            cursor.execute('INSERT INTO users VALUES (%s, %s)', (username, password,))
            connection.commit()
            connection.close()
            return render_template('register.html', success=True)
    else:
        return render_template('register.html', alert=True)



@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('user', None)
   session.pop('reservation', None)
   session.pop('equipA', None)
   session.pop('equipB', None)
   # Redirect to login page
   return redirect(url_for('login'))




if __name__ == "__main__":
    app.run()