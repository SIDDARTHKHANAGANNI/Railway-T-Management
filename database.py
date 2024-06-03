import sqlite3

def init_db():
    conn = sqlite3.connect('railway_reservation.db')
    c = conn.cursor()

    # Create table for train details
    c.execute('''CREATE TABLE IF NOT EXISTS trains (
                    trainno INTEGER PRIMARY KEY,
                    trainname TEXT,
                    no_ofac1stclass INTEGER,
                    no_ofac2ndclass INTEGER,
                    no_ofac3rdclass INTEGER,
                    no_ofsleeper INTEGER,
                    startingpt TEXT,
                    destination TEXT
                )''')

    # Create table for ticket reservations
    c.execute('''CREATE TABLE IF NOT EXISTS tickets (
                    resno INTEGER PRIMARY KEY,
                    name TEXT,
                    age INTEGER,
                    trainno INTEGER,
                    no_ofac1stclass INTEGER,
                    no_ofac2ndclass INTEGER,
                    no_ofac3rdclass INTEGER,
                    no_ofsleeper INTEGER,
                    no_oftickets INTEGER,
                    status TEXT,
                    FOREIGN KEY(trainno) REFERENCES trains(trainno)
                )''')
    
    # Create table for users
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )''')

    # Add admin user
    c.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('admin', 'admin_password_hash', 'admin')")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
