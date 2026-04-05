from flask import Flask, render_template, request, redirect, session
from datetime import datetime
from flask import request
import sqlite3

conn = sqlite3.connect('database.db')
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS visitors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT,
    page TEXT,
    time TEXT
)
""")

conn.commit()
conn.close()

print("Visitors table created ✅")

app = Flask(__name__)
app.secret_key = "secret123"

# DB INIT
def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # USERS TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    # PLACES TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS places (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT
    )
    """)

    conn.commit()
    conn.close()

def get_db():
    return sqlite3.connect("database.db")

def track_visit(page):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    ip = request.remote_addr
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("INSERT INTO visitors (ip, page, time) VALUES (?, ?, ?)", (ip, page, time))
    conn.commit()
    conn.close()


# SIGNUP
@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        conn.execute("INSERT INTO users (username, password) VALUES (?,?)", (username,password))
        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("signup.html")

# LOGIN
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=?",
                            (username,password)).fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect("/dashboard")
        else:
            return "Invalid Login ❌"

    return render_template("login.html")
# dashboard
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("database.db")
    count = conn.execute("SELECT COUNT(*) FROM places").fetchone()[0]
    conn.close()

    return render_template("dashboard.html", user=session["user"], count=count)
# HOME
@app.route("/home")
def home():
    if "user" not in session:
        return redirect("/")
    #track_visit("Home")    
    return render_template("home.html")

@app.route("/features")
def features():
    if "user" not in session:
        return redirect("/")
   # track_visit("Features")
    conn = get_db()
    data = conn.execute("SELECT * FROM places").fetchall()
    conn.close()

    return render_template("features.html", data=data)

@app.route("/about", methods=["GET", "POST"])
def about():
  # track_visit("About")
    if request.method == "POST":
        name = request.form["name"]

        with open("contacts.txt", "a") as f:
            f.write(name + "\n")

        return "Message Sent ✅"

    return render_template("about.html")

@app.route('/admin')
def admin():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    data = cur.execute("SELECT * FROM visitors").fetchall()
    conn.close()

    return render_template("admin.html", data=data)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
