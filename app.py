from flask import Flask, request, render_template, redirect, url_for, session
import sqlite3
import random
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('railway_reservation.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        conn = get_db_connection()

        if conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone():
            return 'Username already exists', 400

        
        hashed_password = generate_password_hash(password)

        conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, hashed_password, role))
        conn.commit()
        conn.close()

        if role == 'admin':
            return redirect(url_for('add_train'))  
        else:
            return redirect(url_for('login')) 

    return render_template('register.html')

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password) and user['role'] == role:
            session['user'] = user['id']
            if user['role'] == 'admin':
                return redirect(url_for('add_train'))
            else:
                return redirect(url_for('index'))
        else:
            error = 'Invalid username, password, or role'
            return render_template('login.html', error=error)

    return render_template('login.html')

@app.route('/index')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('user_index.html')  

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/add_train', methods=('GET', 'POST'))
def add_train():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user'],)).fetchone()
    conn.close()
    if user['role'] != 'admin':
        return redirect(url_for('index'))

    if request.method == 'POST':
        trainname = request.form['trainname']
        trainno = request.form['trainno']
        no_ofac1stclass = request.form['no_ofac1stclass']
        no_ofac2ndclass = request.form['no_ofac2ndclass']
        no_ofac3rdclass = request.form['no_ofac3rdclass']
        no_ofsleeper = request.form['no_ofsleeper']
        startingpt = request.form['startingpt']
        destination = request.form['destination']

        conn = get_db_connection()
        conn.execute('INSERT INTO trains (trainname, trainno, no_ofac1stclass, no_ofac2ndclass, no_ofac3rdclass, no_ofsleeper, startingpt, destination) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                     (trainname, trainno, no_ofac1stclass, no_ofac2ndclass, no_ofac3rdclass, no_ofsleeper, startingpt, destination))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('add_train.html')

@app.route('/reservation', methods=('GET', 'POST'))
def reservation():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        trainno = request.form['trainno']
        class_type = request.form['class_type']
        no_oftickets = int(request.form['no_oftickets'])
        status = 'CONFIRMED'

        conn = get_db_connection()
        train = conn.execute('SELECT * FROM trains WHERE trainno = ?', (trainno,)).fetchone()

        if not train:
            return 'Train not found', 404

        if class_type == 'AC1':
            available_seats = train['no_ofac1stclass']
            cost_per_ticket = 1000
            column_name = 'no_ofac1stclass'
        elif class_type == 'AC2':
            available_seats = train['no_ofac2ndclass']
            cost_per_ticket = 900
            column_name = 'no_ofac2ndclass'
        elif class_type == 'AC3':
            available_seats = train['no_ofac3rdclass']
            cost_per_ticket = 800
            column_name = 'no_ofac3rdclass'
        elif class_type == 'Sleeper':
            available_seats = train['no_ofsleeper']
            cost_per_ticket = 550
            column_name = 'no_ofsleeper'

        if no_oftickets > available_seats:
            status = 'WAITING LIST'

        total_amount = no_oftickets * cost_per_ticket
        resno = random.randint(1000, 2546)

        conn.execute('INSERT INTO tickets (resno, name, age, trainno, no_ofac1stclass, no_ofac2ndclass, no_ofac3rdclass, no_ofsleeper, no_oftickets, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                     (resno, name, age, trainno, no_oftickets if class_type == 'AC1' else 0, no_oftickets if class_type == 'AC2' else 0, no_oftickets if class_type == 'AC3' else 0, no_oftickets if class_type == 'Sleeper' else 0, no_oftickets, status))
        conn.commit()

        if status == 'CONFIRMED':
            conn.execute(f'UPDATE trains SET {column_name} = {column_name} - ? WHERE trainno = ?', (no_oftickets, trainno))
            conn.commit()

        conn.close()

        return render_template('reservation_status.html', resno=resno, status=status, total_amount=total_amount)

    return render_template('reservation.html')

@app.route('/cancellation', methods=('GET', 'POST'))
def cancellation():
    if request.method == 'POST':
        resno = request.form['resno']

        conn = get_db_connection()
        ticket = conn.execute('SELECT * FROM tickets WHERE resno = ?', (resno,)).fetchone()

        if not ticket:
            return 'Reservation not found', 404

        conn.execute('DELETE FROM tickets WHERE resno = ?', (resno,))
        conn.commit()
        conn.close


        return 'Ticket cancelled successfully'

    return render_template('cancellation.html')

@app.route('/pnr_status', methods=('GET', 'POST'))
def pnr_status():
    if request.method == 'POST':
        resno = request.form['resno']

        conn = get_db_connection()
        ticket = conn.execute('SELECT * FROM tickets WHERE resno = ?', (resno,)).fetchone()
        conn.close()

        if not ticket:
            return 'PNR not found', 404

        return render_template('pnr_status.html', ticket=ticket)

    return render_template('pnr_status_form.html')

if __name__ == '__main__':
    app.run(debug=True)
