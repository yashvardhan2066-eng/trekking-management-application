from flask import Flask, redirect, render_template, request, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "trek-demo-secret-key-2026"

def create_database():                             #DATABASE AND TABLE CREATION OF USERS
    conn = sqlite3.connect("trek.db")
    cursor = conn.cursor()                      
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            fullname TEXT NOT NULL,
            address TEXT NOT NULL,
            gender TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            status TEXT DEFAULT 'active'
        )
    """)                                            #DATABASE AND TABLE CREATION OF TREKS
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS treks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trek_name TEXT NOT NULL,
        location TEXT NOT NULL,
        difficulty TEXT NOT NULL,
        duration INTEGER NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        total_slots INTEGER NOT NULL,
        available_slots INTEGER NOT NULL,
        status TEXT DEFAULT 'Open',
        description TEXT,
        image TEXT,
        staff_id INTEGER,
        trek_state TEXT DEFAULT 'Not Started',
        FOREIGN KEY(staff_id) REFERENCES users(id))
    """)
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS bookings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        trek_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        status TEXT NOT NULL,
        booking_state TEXT NOT NULL DEFAULT 'Active',
        booking_state_date TEXT,

        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(trek_id) REFERENCES treks(id))
    """)
    cursor.execute("""
        INSERT OR IGNORE INTO users
        (role, fullname, address, gender, email, phone, username, password, status)
        VALUES (?,?,?,?,?,?,?,?,?)""",
        ("Admin","Administration","System","Other","admin@trek.com","0000000000","admin","admin123","Active")
    )
    conn.commit()
    conn.close()

def message(title,message,back_url):
    return render_template("message.html", title=title, message=message, back_url=back_url)

@app.template_filter("format_date")
def format_date(value):
    if not value:
        return '-'
    if " " in value:
        date = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    else:
        date = datetime.strptime(value, "%Y-%m-%d")
    return date.strftime("%d-%m-%Y")

@app.template_filter("format_time")
def format_datetime(value):
    if not value:
        return ''
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").strftime("%I:%M %p")

@app.route("/")                                     #HOME ROUTE
def home():
    return render_template("home.html")

@app.route("/login")                                #LOGIN ROUTE
def login():
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])    #REGISTER ROUTE
def register():
    if request.method == "POST":

        role = request.form["role"]
        fullname = request.form["fullname"]
        address = request.form["address"]
        gender = request.form["gender"]
        email = request.form["email"]
        phone = request.form["phone"]
        if len(phone) != 10 or not phone.isdigit():         #PHONE NO. CHECK
            return message("⚠️ Invalid Phone Number!", "Please enter a valid 10-digit phone number", '/register')
        username = request.form["username"]
        if len(username) < 5:                               #USERNAME LEN CHECK
            return message("⚠️ Invalid Username" ,"Username must be at least 5 characters long!","/register")
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        if password != confirm_password:                    #PASSWORD CHECK
            return message("⚠️ Passwords do not match!", "Password and Confirm password doesn't match", "/register")
        if role == "Staff":                                 #STAFF STATUS
            status = "pending"
        else:
            status = "active"    

        conn = sqlite3.connect("trek.db")                   
        cursor = conn.cursor()
        
        cursor.execute(                                     #USERNAME CHECK
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        user = cursor.fetchone()
        if user:
            conn.close()
            return message("⚠️ Username already exists!","This Username already exists, Try with another username!","/register") 
        
        cursor.execute(                                     #EMAIL CHECK
            "SELECT * FROM users WHERE email = ?",          
            (email,)                                
        )
        user = cursor.fetchone()
        if user:
            conn.close()
            return message("⚠️ Email already exists!","This Email already exists, Try with another email!","/register")

        cursor.execute("""                                  
            INSERT INTO users(role,fullname,address,gender,email,phone,username,password,status)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (role,fullname,address,gender,email,phone,username,password,status))
        conn.commit()
        conn.close()
        return message("✅ Registered Successfully", "Welcome to the exciting treks world, click OK to login","/login" )
    return render_template("register.html")

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect("trek.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM users WHERE username=? AND password=? AND role='Admin'
            """,
            (username,password)  
        )
        admin = cursor.fetchone()
        conn.close()
        if admin:
            session["admin"] = username
            return redirect("/admin_dash")
        else:
            return message("⚠️ Invalid username or password!","Check your username or password","/admin_login")   
    return render_template("admin_login.html")

@app.route("/admin_dash")                                   #ADMIN DASH ROUTE
def admin_dash():
    if "admin" not in session:
        return redirect("/")
    conn = sqlite3.connect("trek.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users WHERE role='Staff'")
    staff_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE role='User'")
    user_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM treks")
    trek_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bookings")
    booking_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM treks WHERE trek_state='Not Started'")
    not_started_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM treks WHERE trek_state='Started'")
    started_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM treks WHERE trek_state='Completed'")
    completed_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bookings WHERE booking_state='Active'")
    active_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bookings WHERE booking_state='Completed'")
    completed_booking_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bookings WHERE booking_state='Cancelled'")
    cancelled_count = cursor.fetchone()[0]

    conn.close()
    return render_template(
        "admin_dash.html",
        page="dash",
        staff_count=staff_count,
        user_count=user_count,
        trek_count=trek_count,
        booking_count=booking_count,
        not_started_count=not_started_count,
        started_count=started_count,
        completed_count=completed_count,
        active_count=active_count,
        completed_booking_count=completed_booking_count,
        cancelled_count=cancelled_count
    )

@app.route("/manage_staff", methods=["GET", "POST"])        #MANAGE STAFF ROUTE
def manage_staff():
    if "admin" not in session:
        return redirect("/")
    if request.method == "POST":
        staff_id = request.form["staff_id"]
        action = request.form["action"]

        conn = sqlite3.connect("trek.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET status = ? WHERE id = ?",
            (action, staff_id)
        )
        conn.commit()
        conn.close()
        return redirect("/manage_staff")
    search = request.args.get('search','').strip()
    conn = sqlite3.connect("trek.db")
    cursor = conn.cursor()  
    if search:
        cursor.execute("""
            SELECT * FROM users WHERE role='Staff' 
            AND(id LIKE ?
                OR fullname LIKE ? 
                OR email LIKE ?
                OR phone LIKE ? 
                OR username LIKE ? )""",
            (f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%")
        )
    else:
        cursor.execute(
            "SELECT * FROM users WHERE role = 'Staff'"
        )
    staff = cursor.fetchall()
    conn.close()  
    return render_template("manage_staff.html", staff = staff, page = 'staff', search=search)

@app.route("/manage_staff/active")
def active_staff():
    if "admin" not in session:
        return redirect("/")
    search = request.args.get('search','').strip()
    conn = sqlite3.connect("trek.db")
    cursor = conn.cursor()  
    if search:
        cursor.execute("""
            SELECT * FROM users WHERE role='Staff' AND status = 'active'
            AND(id LIKE ?
                OR fullname LIKE ? 
                OR email LIKE ?
                OR phone LIKE ? 
                OR username LIKE ? )""",
            (f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%")
        )
    else:
        cursor.execute(
            "SELECT * FROM users WHERE role = 'Staff' AND status = 'active'"
        )
    staff = cursor.fetchall()
    conn.close()
    return render_template("manage_staff.html", staff=staff, page = 'staff', search=search)

@app.route("/manage_staff/pending")
def pending_staff():
    if "admin" not in session:
        return redirect("/")
    search = request.args.get('search','').strip()
    conn = sqlite3.connect("trek.db")
    cursor = conn.cursor()  
    if search:
        cursor.execute("""
            SELECT * FROM users WHERE role='Staff' AND status = 'pending'
            AND( id LIKE ?
                OR fullname LIKE ? 
                OR email LIKE ?
                OR phone LIKE ? 
                OR username LIKE ? )""",
            (f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%")
        )
    else:
        cursor.execute(
            "SELECT * FROM users WHERE role = 'Staff' AND status = 'pending'"
        )
    staff = cursor.fetchall()
    conn.close()
    return render_template("manage_staff.html", staff=staff, page = 'staff', search=search)

@app.route("/manage_staff/rejected")
def rejected_staff():
    if "admin" not in session:
        return redirect("/")
    search = request.args.get('search','').strip()
    conn = sqlite3.connect("trek.db")
    cursor = conn.cursor()  
    if search:
        cursor.execute("""
            SELECT * FROM users WHERE role='Staff' AND status = 'rejected'
            AND(id LIKE ?
                OR fullname LIKE ? 
                OR email LIKE ?
                OR phone LIKE ? 
                OR username LIKE ? )""",
            (f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%")
        )
    else:
        cursor.execute(
            "SELECT * FROM users WHERE role = 'Staff' AND status = 'rejected'"
        )
    staff = cursor.fetchall()
    conn.close()
    return render_template("manage_staff.html", staff=staff, page = 'staff', search=search)

@app.route("/manage_staff/blacklisted")
def blacklisted_staff():
    if "admin" not in session:
        return redirect("/")
    search = request.args.get('search','').strip()
    conn = sqlite3.connect("trek.db")
    cursor = conn.cursor()  
    if search:
        cursor.execute("""
            SELECT * FROM users WHERE role='Staff' AND status = 'blacklisted' 
            AND( id LIKE ?
                OR fullname LIKE ? 
                OR email LIKE ?
                OR phone LIKE ? 
                OR username LIKE ? )""",
            (f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%")
        )
    else:
        cursor.execute(
            "SELECT * FROM users WHERE role = 'Staff' AND status = 'blacklisted'"
        )
    staff = cursor.fetchall()
    conn.close()
    return render_template("manage_staff.html", staff=staff, page = 'staff', search=search)

@app.route("/manage_treks")
def manage_treks():
    if "admin" not in session:
        return redirect("/")
    search = request.args.get('search','').strip()
    conn = sqlite3.connect("trek.db")
    cursor = conn.cursor()  
    if search:
        cursor.execute("""
            SELECT treks.*,users.fullname
            FROM treks
            LEFT JOIN users
            ON treks.staff_id = users.id 
            WHERE( treks.id LIKE ? 
                OR treks.trek_name LIKE ?
                OR treks.location LIKE ? 
                OR treks.difficulty LIKE ?
                OR treks.duration LIKE ?
                OR treks.start_date LIKE ? 
                OR treks.end_date LIKE ?
                OR treks.available_slots LIKE ?
                OR treks.trek_state LIKE ? 
                OR users.fullname LIKE ? )
                ORDER BY treks.start_date""",
            (f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%")
        )
    else:
        cursor.execute("""
            SELECT treks.*,users.fullname
            FROM treks
            LEFT JOIN users
            ON treks.staff_id = users.id
            ORDER BY treks.start_date"""
        )
    treks = cursor.fetchall()
    conn.close()
    return render_template("manage_treks.html",treks=treks,page="treks", search=search)

@app.route("/add_trek", methods=["GET", "POST"])
def add_trek():
    if "admin" not in session:
        return redirect("/")
    if request.method == 'POST':
        trek_name = request.form['trek_name']
        location = request.form['location']
        difficulty = request.form['difficulty']
        duration = int(request.form['duration'])
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        total_slots = int(request.form['total_slots'])
        available_slots = total_slots
        status = request.form["status"]
        staff_id = request.form["staff_id"] or None
        if duration<=0:
            return message("⚠️ Invalid Duration","Duration must be greater than 0 days","/add_trek")
        if total_slots<=0:
            return message("⚠️ Invalid Total Slots","Total slots must be greater than 0","/add_trek")
        if end_date< start_date:
            return message("⚠️ Invalid Trek Dates","End date can't be before trek start date","/add_trek")
        image = request.files["image"]
        image_name = image.filename
        image.save("static/images/" + image_name)
        description = request.form['description']

        conn = sqlite3.connect("trek.db")
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO treks(trek_name,location,
            difficulty,duration,start_date,end_date,
            total_slots,available_slots,status,image,staff_id,description
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,(trek_name,location,difficulty,duration,start_date,
                end_date,total_slots,available_slots,status,image_name,staff_id,description)
        )
        conn.commit()
        conn.close()
        return redirect("/manage_treks")
    conn = sqlite3.connect("trek.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, fullname
        FROM users
        WHERE role='Staff'
        AND status='active'
        AND id NOT IN (
            SELECT staff_id
            FROM treks
            WHERE staff_id IS NOT NULL AND trek_state != 'Completed'
        )"""
    )
    staff = cursor.fetchall()
    conn.close()
    return render_template("add_trek.html", staff=staff, page = 'treks')

@app.route("/edit_trek/<int:trek_id>", methods=["GET", "POST"])
def edit_trek(trek_id):
    if "admin" not in session:
        return redirect("/")
    if request.method == 'POST':
        trek_name = request.form['trek_name']
        location = request.form['location']
        difficulty = request.form['difficulty']
        duration = int(request.form['duration'])
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        total_slots = int(request.form['total_slots'])
        status = request.form["status"]
        staff_id = request.form["staff_id"] or None
        if duration<=0:
            return message("Invalid Duration","Duration must be greater than 0 days",f"/edit_trek/{trek_id}")
        if total_slots<=0:
            return message("Invalid Total Slots","Total slots must be greater than 0",f"/edit_trek/{trek_id}")
        if end_date< start_date:
            return message("Invalid Trek Dates","End date can't be before trek start date",f"/edit_trek/{trek_id}")
        
        conn = sqlite3.connect("trek.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT total_slots, available_slots, image FROM treks WHERE id=?",
            (trek_id,)
        )
        old = cursor.fetchone()
        old_total = old[0]
        old_available = old[1]
        old_image= old[2]
        booked = old_total - old_available
        if total_slots < booked:
            conn.close()
            return message("⚠️ Invalid Total Slots ","Total slots cannot be less than booked participants.",f"/edit_trek/{trek_id}")
        description = request.form['description']
        new_available = total_slots - booked
        image = request.files["image"]
        if image.filename:
            image_name = image.filename
            image.save("static/images/" + image_name)
        else:
            image_name=old_image

        cursor.execute(
            """UPDATE treks SET trek_name=?,location=?,
            difficulty=?,duration=?,start_date=?,end_date=?,
            total_slots=?,available_slots=?,status=?,staff_id=?,image=?,description=? WHERE id = ?""",
            (trek_name,location,difficulty,duration,start_date,
            end_date,total_slots,new_available,status,staff_id,image_name,description,trek_id)
        )
        conn.commit()
        conn.close()
        return redirect("/manage_treks")
    conn = sqlite3.connect("trek.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM treks WHERE id = ?",
        (trek_id,)
    )
    trek = cursor.fetchone()
    if not trek:
        conn.close()
        return message("⚠️ Trek Not Found","The requested trek does not exist.","/manage_treks")
    cursor.execute(
        """
        SELECT id, fullname FROM users
        WHERE role = 'Staff'AND status = 'active'
        AND (
            id NOT IN (
                SELECT staff_id FROM treks
                WHERE staff_id IS NOT NULL
                AND id != ?
                AND trek_state != 'Completed'
            )
            OR id = ?
        )
        """,
        (trek_id, trek[12])
    )
    staff = cursor.fetchall()
    conn.close()
    return render_template("edit_trek.html",trek=trek, staff=staff, page="treks")

@app.route("/delete_trek/<int:trek_id>", methods=["GET", "POST"])
def delete_trek(trek_id):
    if "admin" not in session:
        return redirect("/")
    if request.method == "POST":
        conn = sqlite3.connect("trek.db")
        cursor= conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM bookings WHERE trek_id=?",
            (trek_id,)
        )
        booking_count = cursor.fetchone()[0]
        if booking_count>0:
            conn.close()
            return message("⚠️ Trek Can't Be Deleted", "This trek has booking history and cannot be deleted.", "/manage_treks")
        cursor.execute(
            "DELETE FROM treks WHERE id = ?",
            (trek_id,)
        )
        conn.commit()
        conn.close()
        return message("✅ Trek Deleted","The trek has been deleted successfully","/manage_treks")

    conn = sqlite3.connect("trek.db")
    cursor= conn.cursor()
    cursor.execute(
        "SELECT * FROM treks WHERE id = ?",
        (trek_id,)
    )
    trek = cursor.fetchone()
    conn.close()
    if not trek:
        return message("⚠️ Trek Not Found","The requested trek does not exist.","/manage_treks")
    return render_template("delete_trek.html", trek=trek, page = "treks")

@app.route("/manage_bookings")
def manage_bookings():
    if "admin" not in session:
        return redirect("/")
    search = request.args.get('search','').strip()
    conn = sqlite3.connect("trek.db")
    cursor = conn.cursor()  
    if search:
        cursor.execute("""
            SELECT
                bookings.id,
                users.id,
                users.fullname,
                treks.id,
                treks.trek_name,
                bookings.date,
                bookings.status,
                bookings.booking_state,
                bookings.booking_state_date
            FROM bookings
            JOIN users ON bookings.user_id = users.id
            JOIN treks ON bookings.trek_id = treks.id 
            WHERE( bookings.id LIKE ?
                OR users.id LIKE ?
                OR users.fullname LIKE ?
                OR treks.id LIKE ?
                OR treks.trek_name LIKE ?
                OR bookings.date LIKE ?
                OR bookings.status LIKE ?
                OR bookings.booking_state LIKE ?
                OR bookings.booking_state_date LIKE ? )
                ORDER BY bookings.id""",
            (f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%")
        )
    else:
        cursor.execute(
        """ SELECT
                bookings.id,
                users.id,
                users.fullname,
                treks.id,
                treks.trek_name,
                bookings.date,
                bookings.status,
                bookings.booking_state,
                bookings.booking_state_date
            FROM bookings
            JOIN users ON bookings.user_id = users.id
            JOIN treks ON bookings.trek_id = treks.id
            ORDER BY bookings.id"""
        )
    bookings= cursor.fetchall()
    conn.close()
    return render_template("manage_bookings.html", bookings=bookings, page= "bookings", search=search)

@app.route("/manage_users", methods =["GET","POST"])
def manage_users():
    if "admin" not in session:
        return redirect("/")

    if request.method == "POST":
        user_id = request.form["user_id"]
        status = request.form["action"]

        conn = sqlite3.connect("trek.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET status=? WHERE id=?",
            (status,user_id)
        )
        conn.commit()
        conn.close()
        return redirect("/manage_users")
    search = request.args.get('search','').strip()
    conn = sqlite3.connect("trek.db")
    cursor = conn.cursor()  
    if search:
        cursor.execute("""
            SELECT id, fullname, email, phone, username, status
            FROM users
            WHERE role = 'User' 
            AND( id LIKE ?
                OR fullname LIKE ?
                OR email LIKE ?
                OR phone LIKE ?
                OR username LIKE ?
                OR status LIKE ?)
                ORDER BY id""",
            (f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%")
        )
    else:
        cursor.execute("""
            SELECT id, fullname, email, phone, username, status
            FROM users
            WHERE role = "User"
            ORDER BY id """
        )
    users = cursor.fetchall()
    conn.close()
    return render_template("manage_users.html",page="users",users=users, search=search)

@app.route("/staff_login", methods=["GET", "POST"])         #STAFF LOG ROUTE
def staff_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("trek.db")
        cursor = conn.cursor()
        cursor.execute(                                     #STAFF LOG CHECK
            "SELECT * FROM users WHERE username = ? AND password = ? AND role = 'Staff'",
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user and user[9] == "pending":
            return message("⚠️ Account approval is pending","Your Account approval is pending. Please wait for the admin to approve.","/staff_login")
        elif user and user[9] == "active":
            session["staff_id"] = user[0]
            session["staff_name"] = user[2]
            return redirect("/staff_dash")
        elif user and user[9] == "blacklisted":
            return message("⚠️ Account has been blacklisted","Your account has been blacklisted. Please contact the admin for more information.","/staff_login")
        elif user and user[9] == "rejected":
            return message("⚠️ Account has been rejected","Your account has been rejected. Please contact the admin for more information.","/staff_login")
        else:
            return message("⚠️ Invalid username or password!","Check your username or password","/staff_login")
    return render_template("staff_login.html")

@app.route("/staff_dash")                                   #STAFF DASH ROUTE
def staff_dash():
    if "staff_id" not in session:
        return redirect("/")
    staff_id = session["staff_id"]
    staff_name = session["staff_name"]
    conn = sqlite3.connect("trek.db")
    cursor = conn.cursor()

    cursor.execute(
        " SELECT COUNT(*) FROM treks WHERE staff_id=? ",
        (staff_id,)               
    )
    assigned_treks=cursor.fetchone()[0]

    cursor.execute(
        """SELECT COUNT(*) FROM bookings JOIN treks
        ON bookings.trek_id=treks.id 
        WHERE treks.staff_id=? AND bookings.booking_state IN ('Active','Completed')""",
        (staff_id,)
    )
    participants=cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM treks WHERE staff_id=? AND status='Open' ",
        (staff_id,)
    )
    open_treks=cursor.fetchone()[0]
    
    cursor.execute(
        """SELECT trek_name,location,start_date,end_date,status, total_slots-available_slots, trek_state
        FROM treks 
        WHERE staff_id=?
        ORDER BY start_date DESC
        LIMIT 3""",
        (staff_id,)
    )
    treks_table=cursor.fetchall()
    conn.close()
    return render_template (
        "staff_dash.html", assigned_treks=assigned_treks, 
        page = "dash", participants=participants,
        open_treks=open_treks,staff_name=staff_name,
        treks_table=treks_table
    )

@app.route("/staff_treks")                                   #STAFF TREKS ROUTE
def staff_treks():
    if "staff_id" not in session:
        return redirect("/")
    staff_id = session["staff_id"]
    staff_name = session["staff_name"]
    search = request.args.get('search','').strip()
    conn = sqlite3.connect("trek.db")
    cursor = conn.cursor()  
    if search:
        cursor.execute("""
            SELECT id, trek_name, location, start_date, available_slots, status 
            FROM treks WHERE staff_id=? 
            AND( id LIKE ? 
                OR trek_name LIKE ?
                OR location LIKE ?
                OR start_date LIKE ?
                OR available_slots LIKE ?
                OR status LIKE ?
                OR trek_state LIKE ?)
                ORDER BY start_date""",
            (staff_id,f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%")
        )
    else:
        cursor.execute(
            """SELECT id, trek_name, location, start_date, available_slots, status, trek_state
            FROM treks WHERE staff_id=? ORDER BY start_date""",
            (staff_id,)
        )
    treks = cursor.fetchall()
    conn.close()
    return render_template("staff_treks.html", treks=treks, page="treks", staff_name=staff_name, search=search)

@app.route("/staff_update_trek/<int:trek_id>", methods=["GET", "POST"])
def staff_update_trek(trek_id):
    if "staff_id" not in session:
        return redirect("/")
    staff_id = session["staff_id"]
    staff_name = session["staff_name"]
    conn = sqlite3.connect('trek.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM treks WHERE id=? AND staff_id=?",
        (trek_id,staff_id)
    )
    trek=cursor.fetchone()
    conn.close()

    if not trek:
        return message("⚠️ Access Denied", "You are not assigned to manage this trek.", "/staff_treks")
    
    if request.method == "POST":
        total_slots = int(request.form['total_slots'])
        status = request.form['status']
        if total_slots<=0:
            return message("⚠️ Invalid Total Slots","Total slots must be greater than 0",f"/staff_update_trek/{trek_id}")
        conn = sqlite3.connect('trek.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT total_slots, available_slots FROM treks WHERE id=?",
            (trek_id,)
        )
        old = cursor.fetchone()
        old_total = old[0]
        old_available = old[1]
        booked = old_total - old_available
        if total_slots < booked:
            conn.close()
            return message("⚠️ Invalid Total Slots ","Total slots cannot be less than booked participants.",f"/staff_update_trek/{trek_id}")
        new_available = total_slots - booked
        cursor.execute(
            """ UPDATE treks SET total_slots=?, available_slots=?, status=? WHERE id=?""",
            (total_slots,new_available,status,trek_id)
        )
        conn.commit()
        conn.close()
        return redirect("/staff_treks")
        
    conn = sqlite3.connect('trek.db')
    cursor = conn.cursor()
    cursor.execute(
        """ SELECT * FROM treks WHERE id=?""",
        (trek_id,)
    )
    treks_table= cursor.fetchone()
    conn.close()
    return render_template("staff_update_trek.html",page = "treks", treks_table=treks_table, staff_name=staff_name)

@app.route("/update_trek_started/<int:trek_id>")
def update_trek_started(trek_id):
    if "staff_id" not in session:
        return redirect("/")
    staff_id = session["staff_id"]
    conn = sqlite3.connect("trek.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE treks SET trek_state='Started', status='Closed' WHERE id=? AND staff_id=?",
        (trek_id,staff_id)
    )
    if cursor.rowcount ==0:
        conn.close()
        return message("⚠️ Access Denied", "You are not assigned to manage this trek.", "/staff_treks")
     
    conn.commit()
    conn.close()
    return redirect(f"/staff_update_trek/{trek_id}")

@app.route("/update_trek_completed/<int:trek_id>")
def update_trek_completed(trek_id):
    if "staff_id" not in session:
        return redirect("/")
    staff_id = session["staff_id"]
    conn = sqlite3.connect("trek.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM treks WHERE id=? AND staff_id=?",
        (trek_id,staff_id)
    )
    trek = cursor.fetchone()
    if not trek:
        conn.close()
        return message("⚠️ Access Denied", "You are not assigned to manage this trek.", "/staff_treks")
    
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        """
        UPDATE bookings
        SET booking_state='Completed' ,booking_state_date=?
        WHERE trek_id=?
        AND booking_state='Active'
        """,
        (current_date, trek_id)
    )
    cursor.execute(
        """
        UPDATE treks
        SET trek_state='Completed', status='Closed'
        WHERE id=? AND staff_id=?
        """,
        (trek_id,staff_id)
    )
    conn.commit()
    conn.close()
    return redirect(f"/staff_update_trek/{trek_id}")

@app.route("/staff_participants")
def staff_participants():
    if "staff_id" not in session:
        return redirect("/")
    staff_id = session["staff_id"]
    staff_name = session["staff_name"]
    search = request.args.get('search','').strip()
    conn = sqlite3.connect("trek.db")
    cursor = conn.cursor()  
    if search:
        cursor.execute("""
            SELECT id,trek_name, location, start_date 
            FROM treks WHERE staff_id=? 
            AND( id LIKE ?
                OR trek_name LIKE ?
                OR location LIKE ?
                OR start_date LIKE ?)
                ORDER BY id""",
            (staff_id,f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%")
        )
    else:
        cursor.execute(
            """SELECT id,trek_name, location, start_date, total_slots-available_slots FROM treks WHERE staff_id=?""",
            (staff_id,)
        )
    treks = cursor.fetchall()
    conn.close()
    return render_template("staff_participants.html", treks=treks, page="participants", staff_name=staff_name, search=search)

@app.route("/staff_participants_view/<int:trek_id>")
def staff_participants_view(trek_id):
    if "staff_id" not in session:
        return redirect("/")
    staff_name = session["staff_name"]
    staff_id = session["staff_id"]
    conn = sqlite3.connect("trek.db")   
    cursor = conn.cursor()
    cursor.execute(
        """SELECT trek_name, location, start_date, end_date FROM treks WHERE id=? and staff_id=? """,
        (trek_id, staff_id)
    )
    trek = cursor.fetchone()
    if not trek:
        conn.close()
        return message("⚠️ Access Denied", "You are not assigned to manage this trek.", "/staff_participants")
    search = request.args.get('search','').strip()  
    if search:
        cursor.execute("""
            SELECT users.fullname, users.gender, users.email, users.phone, bookings.date
            FROM bookings
            JOIN users ON bookings.user_id = users.id
            WHERE bookings.trek_id = ? AND booking_state IN ('Active','Completed')
            AND( users.fullname LIKE ? 
                OR users.gender LIKE ? 
                OR users.email LIKE ? 
                OR users.phone LIKE ? 
                OR bookings.date LIKE ?)
                ORDER BY bookings.date""",
            (trek_id,f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%")
        )
    else:
        cursor.execute(
            """SELECT users.fullname, users.gender, users.email, users.phone, bookings.date
            FROM bookings
            JOIN users ON bookings.user_id = users.id
            WHERE bookings.trek_id = ? AND booking_state IN ('Active','Completed')
            ORDER BY bookings.date""",
            (trek_id,)
        )
    participants = cursor.fetchall()
    conn.close()    
    return render_template("staff_participants_view.html", 
                           participants=participants, trek=trek, 
                           page="participants", staff_name=staff_name, search=search, trek_id=trek_id)

@app.route("/staff_profile")
def staff_profile():
    if "staff_id" not in session:
        return redirect("/")
    staff_id = session["staff_id"]
    staff_name = session["staff_name"]
    conn = sqlite3.connect("trek.db")
    cursor = conn.cursor()

    cursor.execute(
        """SELECT * FROM users WHERE id=?""",
        (staff_id,)
    )
    user = cursor.fetchone()
    conn.close()
    return render_template("staff_profile.html", user=user, page="profile", staff_name=staff_name)

@app.route("/staff_prof_edit", methods=["GET", "POST"])
def staff_profile_edit():
    if "staff_id" not in session:
        return redirect("/")
    staff_id = session["staff_id"]
    staff_name = session["staff_name"]
    if request.method == "POST":
        name = request.form["fullname"]
        address = request.form["address"]
        gender = request.form["gender"]
        email = request.form["email"]
        phone = request.form["phone"]
        if len(phone) != 10 or not phone.isdigit():         #PHONE NO. CHECK
            return message("⚠️ Invalid Phone Number!", "Please enter a valid 10-digit phone number", '/staff_prof_edit')
                     
        username = request.form["username"]
        if len(username) < 5:       #USERNAME LEN CHECK
            return message("⚠️ Invalid Username" ,"Username must be at least 5 characters long!","/staff_prof_edit")                               

        conn = sqlite3.connect("trek.db")
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id FROM users WHERE email = ? AND id != ?""",
            (email, staff_id)
        )
        if cursor.fetchone():
            conn.close()
            return message("⚠️ Email already exists!","This Email already exists, Try with another email!","/staff_prof_edit") 

        
        cursor.execute(
            """SELECT id FROM users WHERE username = ? AND id != ?""",
            (username, staff_id)
        )
        if cursor.fetchone():
            conn.close()
            return message("⚠️ Username already exists!","This Username already exists, Try another with username!","/staff_prof_edit") 
                
        cursor.execute(
            """UPDATE users SET fullname=?, address=?, gender=?, email=?, phone=?, username=? WHERE id=?""",
            (name,address,gender,email,phone,username,staff_id)
        )
        conn.commit()
        conn.close()
        session["staff_name"] = name
        return redirect("/staff_profile")
    
    conn = sqlite3.connect("trek.db")
    cursor = conn.cursor()  
    cursor.execute(
        """SELECT * FROM users WHERE id=?""",
        (staff_id,)
    )
    user = cursor.fetchone()
    conn.close()
    return render_template("staff_prof_edit.html", user=user, page="profile", staff_name=staff_name)

@app.route("/user_login", methods=["GET", "POST"])          #USER LOG ROUTE
def user_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        

        conn = sqlite3.connect("trek.db")
        cursor = conn.cursor()
        cursor.execute(                                     #USER LOG CHECK
            "SELECT * FROM users WHERE username = ? AND password = ? AND role = 'User'",
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user and user[9] == "active":
            session["user_id"] = user[0]
            session["user_name"] = user[2]
            return redirect("/user_dash")
        elif user and user[9] == "blacklisted":
            return message("⚠️ Account has been blacklisted","Your account has been blacklisted. Please contact the admin for more information.","/user_login")
        else:
            return message("⚠️ Invalid username or password!","Check your username or password","/user_login")
    return render_template("user_login.html")

@app.route("/user_dash", methods=["GET", "POST"])           #USER DASH ROUTE
def user_dash():
    if "user_id" not in session:
        return redirect("/")
    user_id = session["user_id"]
    user_name = session["user_name"]
    conn = sqlite3.connect("trek.db")
    cursor = conn.cursor()
    cursor.execute(
        """SELECT * FROM treks 
        WHERE trek_state='Not Started' AND available_slots > 0 AND status='Open'
        ORDER BY start_date LIMIT 4""")
    treks = cursor.fetchall()

    cursor.execute(
        """SELECT treks.trek_name, treks.location, bookings.id, bookings.date, bookings.booking_state, treks.trek_state
        FROM bookings JOIN treks ON bookings.trek_id = treks.id 
        WHERE bookings.user_id=? AND bookings.booking_state='Active' LIMIT 2""", (user_id,)
    )
    bookings = cursor.fetchall()
    conn.close()
    return render_template("user_dash.html", user_id=user_id,
                           user_name=user_name, treks=treks, 
                           bookings=bookings, page="dash")

@app.route("/user_book_treks")
def user_book_treks():  
    if "user_id" not in session:
        return redirect("/")
    user_id = session["user_id"]
    user_name = session["user_name"]
    search = request.args.get('search','').strip()
    conn = sqlite3.connect("trek.db")
    cursor = conn.cursor()  
    if search:
        cursor.execute("""
            SELECT * FROM treks 
            WHERE trek_state='Not Started' AND available_slots > 0 AND status='Open'
            AND( trek_name LIKE ?
                OR location LIKE ?
                OR duration LIKE ?
                OR start_date LIKE ?)
                ORDER BY start_date""",
            (f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%")
        )
    else:
        cursor.execute(
            """SELECT * FROM treks 
            WHERE trek_state='Not Started' AND available_slots > 0 AND status='Open'
            ORDER BY start_date""")
    treks = cursor.fetchall()
    conn.close()
    return render_template("user_book_treks.html", user_id=user_id, 
                           user_name=user_name, treks=treks, 
                           page="treks", search=search)

@app.route("/user_book_treks/easy")
def easy_treks():  
    if "user_id" not in session:
        return redirect("/")
    user_id = session["user_id"]
    user_name = session["user_name"]
    search = request.args.get('search','').strip()
    conn = sqlite3.connect("trek.db")
    cursor = conn.cursor()  
    if search:
        cursor.execute("""
            SELECT * FROM treks 
            WHERE trek_state='Not Started' AND available_slots > 0 AND status='Open' AND difficulty = 'Easy'
            AND( trek_name LIKE ?
                OR location LIKE ?
                OR duration LIKE ?
                OR start_date LIKE ?)
                ORDER BY start_date""",
            (f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%")
        )
    else:
        cursor.execute(
            """SELECT * FROM treks 
            WHERE trek_state='Not Started' AND available_slots > 0 AND status='Open' AND difficulty = 'Easy'
            ORDER BY start_date""")
    treks = cursor.fetchall()
    conn.close()
    return render_template("user_book_treks.html", user_id=user_id, 
                           user_name=user_name, treks=treks, 
                           page="treks", search=search)

@app.route("/user_book_treks/moderate")
def moderate_treks():  
    if "user_id" not in session:
        return redirect("/")
    user_id = session["user_id"]
    user_name = session["user_name"]
    search = request.args.get('search','').strip()
    conn = sqlite3.connect("trek.db")
    cursor = conn.cursor()  
    if search:
        cursor.execute("""
            SELECT * FROM treks 
            WHERE trek_state='Not Started' AND available_slots > 0 AND status='Open' AND difficulty = 'Moderate'
            AND( trek_name LIKE ?
                OR location LIKE ?
                OR duration LIKE ?
                OR start_date LIKE ?)
                ORDER BY start_date""",
            (f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%")
        )
    else:
        cursor.execute(
            """SELECT * FROM treks 
            WHERE trek_state='Not Started' AND available_slots > 0 AND status='Open' AND difficulty = 'Moderate'
            ORDER BY start_date""")
    treks = cursor.fetchall()
    conn.close()
    return render_template("user_book_treks.html", user_id=user_id, 
                           user_name=user_name, treks=treks, 
                           page="treks", search=search)

@app.route("/user_book_treks/hard")
def hard_treks():  
    if "user_id" not in session:
        return redirect("/")
    user_id = session["user_id"]
    user_name = session["user_name"]
    search = request.args.get('search','').strip()
    conn = sqlite3.connect("trek.db")
    cursor = conn.cursor()  
    if search:
        cursor.execute("""
            SELECT * FROM treks 
            WHERE trek_state='Not Started' AND available_slots > 0 AND status='Open' AND difficulty = 'Hard'
            AND( trek_name LIKE ?
                OR location LIKE ?
                OR duration LIKE ?
                OR start_date LIKE ?)
                ORDER BY start_date""",
            (f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%")
        )
    else:
        cursor.execute(
            """SELECT * FROM treks 
            WHERE trek_state='Not Started' AND available_slots > 0 AND status='Open' AND difficulty = 'Hard'
            ORDER BY start_date""")
    treks = cursor.fetchall()
    conn.close()
    return render_template("user_book_treks.html", user_id=user_id, 
                           user_name=user_name, treks=treks, 
                           page="treks", search=search)

@app.route("/user_trek_booking/<int:trek_id>", methods=["GET", "POST"])
def user_trek_booking(trek_id):
    if "user_id" not in session:
        return redirect("/")
    user_id = session["user_id"]
    if request.method == "POST":
        
        booking_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "Booked"
        conn = sqlite3.connect("trek.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM treks
            WHERE id=?
            AND trek_state='Not Started' AND status='Open' AND available_slots >0 """,
            (trek_id,)
        )
        trek_avl = cursor.fetchone()
        if not trek_avl:
            conn.close()
            return message("⚠️ Booking Not Available", "This trek is closed, already started, completed, or has no available slots.", "/user_book_treks")
        cursor.execute(
            """
            SELECT COUNT(*) FROM bookings
            WHERE user_id=? AND trek_id=? AND booking_state='Active'""",
            (user_id, trek_id)
        )
        already = cursor.fetchone()[0]
        if already > 0:
            conn.close()
            return message("⚠️ Already booked this trek","You have already booked this trek.","/user_book_treks")
        cursor.execute(
            """INSERT INTO bookings(user_id, trek_id, date, status)
            VALUES (?, ?, ?, ?)""",
            (user_id, trek_id, booking_date, status)
        )
        cursor.execute(
            """UPDATE treks SET available_slots = available_slots - 1
            WHERE id = ? AND trek_state='Not Started' AND status='Open' AND available_slots > 0""",
            (trek_id,)
        )
        conn.commit()
        conn.close()
        return message("✅ Booking Successful", "Your trek has been booked successfully , Enjoy your trek. Thank you! ", "/user_book_treks")
    conn = sqlite3.connect("trek.db")
    cursor = conn.cursor()  
    cursor.execute(
        """SELECT * FROM treks WHERE id = ?""",
        (trek_id,)
    )
    trek = cursor.fetchone()
    conn.close()
    if not trek:
        return message("⚠️ Trek Not Found","The requested trek does not exist","/user_book_treks")
    return render_template("user_trek_booking.html", trek=trek, page="treks",user_id=user_id)

@app.route("/user_my_bookings")
def user_my_bookings():
    if "user_id" not in session:
        return redirect("/")
    user_id = session["user_id"]
    user_name = session["user_name"]
    search = request.args.get('search','').strip()
    conn = sqlite3.connect("trek.db")
    cursor = conn.cursor()  
    if search:
        cursor.execute("""
            SELECT  treks.trek_name, treks.location, bookings.id, bookings.date, bookings.booking_state
            FROM bookings JOIN treks ON bookings.trek_id = treks.id 
            WHERE bookings.user_id=? AND bookings.booking_state='Active'
            AND( treks.trek_name LIKE ?
                OR treks.location LIKE ?
                OR bookings.id LIKE ?
                OR bookings.date LIKE ?
                OR bookings.booking_state LIKE ?)
                ORDER BY bookings.date DESC""",
            (user_id,f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%")
        )
    else:
        cursor.execute(
            """SELECT  treks.trek_name, treks.location, bookings.id, bookings.date, bookings.booking_state
            FROM bookings JOIN treks ON bookings.trek_id = treks.id 
            WHERE bookings.user_id=? AND bookings.booking_state='Active' ORDER BY bookings.date DESC""", (user_id,)
        )
    bookings = cursor.fetchall()
    conn.close()
    return render_template("user_my_bookings.html", user_id=user_id,
                           user_name=user_name, bookings=bookings, page="bookings", search=search)

@app.route("/user_booking_details/<int:booking_id>", methods=["GET", "POST"])
def user_booking_details(booking_id):
    if "user_id" not in session:
        return redirect("/")
    user_id = session["user_id"]
    user_name = session["user_name"]
    if request.method == "POST":
        booking_state_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect("trek.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT trek_id FROM bookings 
            WHERE id=? AND user_id=? AND booking_state='Active'""",
            (booking_id, user_id)
        )
        bookings = cursor.fetchone()

        if not bookings:
            conn.close()
            return message("⚠️ Cancellation Not Available", "This booking does not exist, does not belong to you, or is no longer active", "/user_my_bookings")
        trek_id = bookings[0]

        cursor.execute(
            """UPDATE bookings SET booking_state='Cancelled', booking_state_date=?
            WHERE id=? AND user_id=? AND booking_state='Active' """,
            (booking_state_date, booking_id, user_id)
        )
        cursor.execute(
            """UPDATE treks SET available_slots = available_slots + 1
            WHERE id = ?""",
            (trek_id,)
        )
        conn.commit()
        conn.close()
        return message("✅ Booking Cancelled","Your booking has been cancelled. We hope to see you on another trek. Thank you!","/user_my_bookings")
    
    conn = sqlite3.connect("trek.db")
    cursor = conn.cursor()
    cursor.execute(
        """SELECT  treks.trek_name, treks.location, bookings.id, bookings.date, bookings.booking_state, bookings.booking_state_date
        FROM bookings JOIN treks ON bookings.trek_id = treks.id 
        WHERE bookings.id=? AND bookings.user_id=?""", (booking_id, user_id)
    )
    booking = cursor.fetchone()
    conn.close()
    if not booking:
        return message(
            "⚠️ Booking Not Found","The requested booking does not exist or does not belong to you.","/user_my_bookings")
    return render_template("user_booking_details.html", user_id=user_id,
                           user_name=user_name, booking=booking, page="bookings")

@app.route("/user_booking_history")
def user_booking_history():
    if "user_id" not in session:
        return redirect("/")
    user_id = session["user_id"]
    user_name = session["user_name"]
    search = request.args.get('search','').strip()
    conn = sqlite3.connect("trek.db")
    cursor = conn.cursor()  
    if search:
        cursor.execute("""
            SELECT bookings.id, treks.trek_name, treks.location, bookings.date, bookings.booking_state, bookings.booking_state_date
            FROM bookings JOIN treks ON bookings.trek_id = treks.id 
            WHERE bookings.user_id=? 
            AND( bookings.id LIKE ?
                OR treks.trek_name LIKE ?
                OR treks.location LIKE ?
                OR bookings.date LIKE ?
                OR bookings.booking_state LIKE ?
                OR bookings.booking_state_date LIKE ?)
                ORDER BY bookings.date DESC""",
            (user_id,f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%",f"%{search}%")
        )
    else:
        cursor.execute(
            """SELECT bookings.id, treks.trek_name, treks.location, bookings.date, bookings.booking_state, bookings.booking_state_date
            FROM bookings JOIN treks ON bookings.trek_id = treks.id 
            WHERE bookings.user_id=? ORDER BY bookings.date DESC""", (user_id,)
        )
    bookings = cursor.fetchall()
    conn.close()
    return render_template("user_booking_history.html", user_id=user_id,
                           user_name=user_name, bookings=bookings, page="booking_history", search=search)

@app.route("/user_profile")
def user_profile():
    if "user_id" not in session:
        return redirect("/")
    user_id = session["user_id"]
    user_name = session["user_name"]
    conn = sqlite3.connect("trek.db")
    cursor = conn.cursor()
    cursor.execute(
        """SELECT * FROM users WHERE id=?""",
        (user_id,)
    )
    user = cursor.fetchone()
    conn.close()
    return render_template("user_profile.html", user=user, page="profile", user_name=user_name)

@app.route("/user_prof_edit", methods=["GET", "POST"])
def user_profile_edit(): 
    if "user_id" not in session:
        return redirect("/")   
    user_id = session["user_id"]
    user_name = session["user_name"]
    if request.method == "POST":
        name = request.form["fullname"]
        address = request.form["address"]
        gender = request.form["gender"]
        email = request.form["email"]
        phone = request.form["phone"]
        if len(phone) != 10 or not phone.isdigit():         #PHONE NO. CHECK
            return message("⚠️ Invalid Phone Number!", "Please enter a valid 10-digit phone number", '/user_prof_edit')
        username = request.form["username"]
        if len(username) < 5:                               #USERNAME LEN CHECK
            return message("⚠️ Invalid Username" ,"Username must be at least 5 characters long!","/user_prof_edit")

        conn = sqlite3.connect("trek.db")
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id FROM users WHERE email = ? AND id != ?""",
            (email, user_id)
        )
        if cursor.fetchone():
            conn.close()
            return message("⚠️ Email already exists!","This Email already exists, Try with another email!","/user_prof_edit")
        
        cursor.execute(
            """SELECT id FROM users WHERE username = ? AND id != ?""",
            (username, user_id)
        )
        if cursor.fetchone():
            conn.close()
            return message("⚠️ Username already exists!","This Username already exists, Try with another username!","/user_prof_edit")
        cursor.execute(
            """UPDATE users SET fullname=?, address=?, gender=?, email=?, phone=?, username=?
            WHERE id=?""",
            (name, address, gender, email, phone, username, user_id)
        )
        conn.commit()
        conn.close()
        session["user_name"] = name
        return redirect("/user_profile")
    
    conn = sqlite3.connect("trek.db")
    cursor = conn.cursor()
    cursor.execute(
        """SELECT * FROM users WHERE id=?""",
        (user_id,)
    )
    user = cursor.fetchone()
    conn.close()
    return render_template("user_prof_edit.html", user=user, page="profile", user_name=user_name)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    create_database()
    app.run(debug=True)