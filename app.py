from flask import Flask, render_template, request, redirect, url_for
import sqlite3
app = Flask(__name__)



db = sqlite3.connect("database.db", check_same_thread=False)
#create data table to store all posts
# "IF NOT EXISTS" so it doesn't create new table unless I purposefully deleted data
db.execute("""
    
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stallName TEXT,
        foodType TEXT,
        quantityKG REAL,
        condition TEXT,
        phoneNumber TEXT,
        status TEXT DEFAULT 'open'
    )
           
""")
db.commit()



@app.route("/")
def home():
    return render_template("home.html", activePage="home")


@app.route("/post", methods=["get", "post"])
def post():
    submitted = False
    if request.method == "POST":
        food = request.form["foodType"]
        stallName = request.form["stallName"]
        phoneNumber = request.form["phoneNumber"]
        quantityKG = request.form["quantityKG"]
        condition = request.form["condition"]

        db.execute(
            "INSERT INTO posts (stallName, foodType, quantityKG, condition, phoneNumber) VALUES (?, ?, ?, ?, ?)",
            (stallName, food, quantityKG, condition, phoneNumber)
        )
        db.commit()
        submitted = True
    return render_template("post.html", submitted=submitted, activePage="post")


#DELETE LATER
@app.route("/all_posts")
def allPosts():
    rows = db.execute("SELECT * FROM posts").fetchall()
    return str(rows)

@app.route("/charities")
def charities():
    #retrieves only edible food for charities
    rows = db.execute("SELECT * FROM posts WHERE condition = 'edible' AND status = 'open'").fetchall()
    return render_template("charities.html", posts=rows, activePage="charities")


@app.route("/gardens")
def gardens():
    #only "scrap" labeled food for gardens
    rows = db.execute("SELECT * FROM posts WHERE condition = 'scraps' AND status = 'open'").fetchall()
    return render_template("gardens.html", posts=rows, activePage="gardens")

#the claiming button route -  refresh after claiming
@app.route("/claim/<int:post_id>", methods=["POST"])
def claim(post_id):
    matchedPost = db.execute("SELECT condition FROM posts WHERE id = ?", (post_id,)).fetchone()
    #setting status to claimed
    db.execute("UPDATE posts SET status = 'claimed' WHERE id = ?", (post_id,))
    db.commit()

    if matchedPost and matchedPost[0] == "edible":
        return redirect(url_for("charities"))
    else:
        return redirect(url_for("gardens"))
    
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", activePage="dashboard")



app.run(debug=True)