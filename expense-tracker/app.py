from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"


# ---------------- DATABASE INIT ----------------
def init_db():
    conn = sqlite3.connect('expenses.db')
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            amount REAL,
            category TEXT,
            user_id INTEGER
        )
    ''')

    conn.commit()
    conn.close()


# ---------------- HOME ----------------
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('expenses.db')
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM expenses WHERE user_id = ?",
        (session['user_id'],)
    )
    data = cur.fetchall()
    conn.close()

    total = sum(row[2] for row in data)
    return render_template('index.html', expenses=data, total=total)


# ---------------- ADD EXPENSE ----------------
@app.route('/add', methods=['POST'])
def add():
    if 'user_id' not in session:
        return redirect('/login')

    title = request.form['title']
    amount = request.form['amount']
    category = request.form['category']

    conn = sqlite3.connect('expenses.db')
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO expenses (title, amount, category, user_id) VALUES (?, ?, ?, ?)",
        (title, amount, category, session['user_id'])
    )
    conn.commit()
    conn.close()

    return redirect('/')


# ---------------- DELETE EXPENSE ----------------
@app.route('/delete/<int:id>')
def delete(id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('expenses.db')
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM expenses WHERE id = ? AND user_id = ?",
        (id, session['user_id'])
    )
    conn.commit()
    conn.close()

    return redirect('/')


# ---------------- SIGNUP ----------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('expenses.db')
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('signup.html')


# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('expenses.db')
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password)
        )
        user = cur.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            return redirect('/')

    return render_template('login.html')


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# ---------------- RUN ----------------
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
