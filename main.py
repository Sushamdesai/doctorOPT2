from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import smtplib
from datetime import date

app = Flask(__name__)
app.secret_key = "medapp1"
logins = {}


def build_connection_with_database():
    conn = psycopg2.connect(database="medapp1", host="localhost", port="5432", user="postgres", password="123")
    return conn


def close_connection_with_database(cur, conn):
    conn.commit()
    cur.close()
    conn.close()


@app.route("/homepage")
def home():
    return render_template("homepage.html")


@app.route('/doctor_login', methods=['POST', 'GET'])
def doctor_login():
    if request.method == "POST":
        name = request.form["name"]
        reg_no = request.form["reg_no"]
        query = f"SELECT * FROM doctors WHERE dr_name = '{name}'"
        conn = build_connection_with_database()
        cur = conn.cursor()
        cur.execute(query)
        data = cur.fetchone()
        reg_no_ = data[1]
        close_connection_with_database(cur, conn)
        if reg_no_ == reg_no:
            logins["doctor"] = name
            return redirect(url_for("doctor_dashboard"))
        else:
            return "Wrong Reg no."
    return render_template("doctor_login.html")


@app.route("/doctor_register", methods=['POST', 'GET'])
def doctor_register():
    if request.method == 'POST':
        name = request.form["name"]
        reg_no = request.form["reg_no"]
        area_code = request.form["area_code"]
        speciality = request.form["specialty"]
        link = request.form['link']
        mobile = request.form['mobile']
        hospital = request.form['hospital']
        query = f"INSERT INTO doctors(dr_name, reg_no, area_code, speciality, link, phone_no, hospital) VALUES ('{name}', '{reg_no}', '{area_code}', '{speciality}', '{link}', '{mobile}', '{hospital}')"
        table_name = name.split()[0] + name.split()[-1]
        query1 = f"CREATE TABLE {table_name}(patient varchar)"
        query2 = f"CREATE TABLE {table_name}1 (patient varchar, date date)"
        query3 = f"INSERT INTO ACCOUNTS(dr_name, payment) VALUES ('{name}', 0)"
        conn = build_connection_with_database()
        cur = conn.cursor()
        cur.execute(query)
        cur.execute(query1)
        cur.execute(query2)
        cur.execute(query3)
        close_connection_with_database(cur, conn)
        return redirect(url_for("doctor_login"))
    return render_template("doctor_register.html")


@app.route("/user_login", methods=['POST', 'GET'])
def user_login():
    if request.method == 'POST':
        name = request.form["name"]
        password = request.form["password"]
        conn = build_connection_with_database()
        cur = conn.cursor()
        query = f"SELECT * FROM users WHERE name = '{name}'"
        cur.execute(query)
        data = cur.fetchone()
        password_ = data[3]
        close_connection_with_database(cur,conn)
        if password_ == password:
            logins["user"] = name
            return redirect(url_for("user_dashboard_main"))
        else:
            return "Wrong Password!"
    return render_template("user_login.html")


@app.route("/user_register", methods=['POST', 'GET'])
def user_register():
    if request.method == 'POST':
        name = request.form['name']
        area_code = request.form['area_code']
        mobile = request.form['mobile']
        email = request.form['email']
        password = request.form['password']
        age = request.form['age']
        query = f"INSERT INTO users(name, area_code, mobile, password, email, age) VALUES ('{name}', '{area_code}', '{mobile}','{password}', '{email}', '{age}')"
        conn = build_connection_with_database()
        cur = conn.cursor()
        cur.execute(query)
        close_connection_with_database(cur, conn)
        return redirect(url_for("user_login"))
    return render_template("user_register.html")


@app.route('/user_dashboard_main')
def user_dashboard_main():
    return render_template("user_dashboard_main.html")


@app.route("/user_dashboard", methods=['POST', 'GET'])
def user_dashboard():
    conn = build_connection_with_database()
    cur = conn.cursor()
    query = f"SELECT * FROM live_dr"
    cur.execute(query)
    data = cur.fetchall()
    close_connection_with_database(cur, conn)
    curr_date = date.today()
    if request.method == 'POST':
        val_ = request.form["book"]
        if val_:
            conn = build_connection_with_database()
            cur = conn.cursor()
            query1 = f"DELETE FROM live_dr WHERE dr_name = '{val_}' "
            table_name = val_.split()[0] + val_.split()[-1]
            query2 = f"INSERT INTO {table_name}(patient) VALUES ('{logins['user']}')"
            query3 = f"INSERT INTO {table_name}1 (patient, date) VALUES ('{logins['user']}', '{curr_date}')"
            cur.execute(query1)
            cur.execute(query2)
            cur.execute(query3)
            close_connection_with_database(cur, conn)
    #         Twilio se message
    return render_template("user_dashboard.html", data=data)


@app.route("/doctor_dashboard", methods=['POST', 'GET'])
def doctor_dashboard():
    table_name = logins['doctor'].split()[0] + logins['doctor'].split()[-1]
    if request.method == "POST":
        input = request.form["live"]
        if input:
            conn = build_connection_with_database()
            cur = conn.cursor()
            query = f"SELECT * FROM doctors WHERE dr_name = '{logins['doctor']}'"
            cur.execute(query)
            data = cur.fetchone()
            specialty = data[3]
            link = data[4]
            hospital = data[6]
            query1 = f"INSERT INTO live_dr(dr_name, specialty, link, hospital) VALUES ('{logins['doctor']}', '{specialty}', '{link}', '{hospital}')"
            query2 = f"TRUNCATE {table_name}"
            cur.execute(query1)
            cur.execute(query2)
            close_connection_with_database(cur, conn)
            return "You are live"

    conn = build_connection_with_database()
    cur = conn.cursor()
    table_name = logins['doctor'].split()[0] + logins['doctor'].split()[-1]
    query = f"SELECT * FROM {table_name}"
    cur.execute(query)
    data = cur.fetchall()
    return render_template("doctor_dashboard.html", data=data)


@app.route('/prescription', methods=['POST', 'GET'])
def prescription():
    if request.method == 'POST':
        table_name = logins['doctor'].split()[0] + logins['doctor'].split()[-1]
        conn = build_connection_with_database()
        cur = conn.cursor()
        query = f"SELECT * FROM {table_name}"
        cur.execute(query)
        data = cur.fetchone()
        patient_name = data[0]
        query1 = f"SELECT * FROM users WHERE name = '{patient_name}'"
        cur.execute(query1)
        data1 = cur.fetchone()
        rec_email = data1[4]
        patient_age = data1[5]
        prescription_ = request.form["prescription"]
        message = f"""
        Doctor Name : {logins['doctor']} \n
        Patient : {patient_name} \n
        age : {patient_age}\n
        Medicines : {prescription_}
        """
        # Twilio se SMS for Payment
        # Suppose Payment Received
        payment = 250
        query2 = f"UPDATE ACCOUNTS SET payment = {payment} + payment WHERE dr_name = '{logins['doctor']}'"
        cur.execute(query2)
        close_connection_with_database(cur, conn)
        sender_email = "shreekantpukale0@gmail.com"
        password = "idoh gdte pjuo sasb"
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, rec_email, message)
    return render_template("prescription.html")


@app.route("/patient_history")
def patient_history():
    table_name = logins['doctor'].split()[0] + logins['doctor'].split()[-1]
    conn = build_connection_with_database()
    cur = conn.cursor()
    query = f"SELECT * FROM {table_name}1 ORDER BY date ASC"
    cur.execute(query)
    data = cur.fetchall()
    close_connection_with_database(cur,conn)
    return render_template("patient_history.html", data=data)


if "__main__" == __name__:
    app.run(debug=True)

# Payment
# https://buy.stripe.com/test_eVa3eRbd8ey66CQfYY
