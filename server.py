from flask import Flask, render_template, url_for, request, redirect, make_response, jsonify
import pymysql
from pymysql.cursors import DictCursor

class Db:

    def __init__(self, host, user, password, db):
        try:
            self.connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            db=db,
            cursorclass=DictCursor,
            )
        except Exception as ex:
            print(ex)

    def request(self, query):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                self.connection.commit()
                return cursor.fetchall()
        except Exception as ex:
            return ex

    def select(self, table):
        req = f"SELECT * FROM `{table}`;"
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(req)
                self.connection.commit()
                return cursor.fetchall()
        except Exception as ex:
            return ex

    def insert(self, table, arg={}):
        k = list(arg.keys())
        req = f"INSERT INTO `{table}`(`{k[0]}`, `{k[1]}`) VALUES ('{arg.get(k[0])}', '{arg.get(k[1])}');"
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(req)
                self.connection.commit()
                return cursor.fetchall()
        except Exception as ex:
            return ex

    def drop(self, table):
        req = f"DELETE FROM `{table}` WHERE 1;"
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(req)
                self.connection.commit()
                return cursor.fetchall()
        except Exception as ex:
            return ex

    def check(self, table, arg={}):
        if len(arg) == 1:
            k = list(arg.keys())
            req = f"SELECT * FROM `{table}` WHERE {k[0]} = '{arg.get(k[0])}';"
        else:
            k = list(arg.keys())
            req = f"SELECT * FROM `{table}` WHERE {k[0]} = '{arg.get(k[0])}' AND {k[1]} = '{arg.get(k[1])}';"
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(req)
                self.connection.commit()
                a = cursor.fetchall()
                if len(a) == 1:
                    return True
                elif len(a) == 0:
                    return False
                else:
                    return "Error"
        except Exception as ex:
            return ex


#MySQL db
try:
    db = Db(
        host='127.0.0.1',
        db='ChatFlaskPython',
        user='root',
        password='31415926Lot/'
        )
    print('#'*20)
except Exception as ex:
    print(ex)

app = Flask(__name__)


@app.route('/', methods=["POST", "GET"])
@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        name = request.form['name']
        password = request.form['password']
        if db.check("ChatUsers", {"name": name, "password": password}):
            response = make_response(render_template('chat.html'))
            response.set_cookie('username', value=name)
            return response
        else:
            return render_template("login.html")
    else:
        return render_template("login.html")


@app.route('/reg', methods=["POST", "GET"])
def reg():
    if request.method == "POST":
        name = request.form['name']
        password = request.form['password']
        password2 = request.form['password2']
        if not db.check("ChatUsers", {"name": name, "password": password}) and password == password2:
            db.insert("ChatUsers", {'name': name, 'password': password})
            response = make_response(render_template('chat.html'))
            response.set_cookie('username', value=name)
            return response
        else:
            return render_template("reg.html")
    else:
        return render_template("reg.html")


@app.route('/chat', methods=["GET"])
def chat():
    if request.cookies.get("username"):
        response = make_response(render_template("chat.html"))
        response.set_cookie('username', value=request.cookies.get("username"))
        return response
    else:
        return make_response("login.html")


@app.route('/send', methods=["POST"])
def send():
    '''if request.cookies.get("username") and request.method == "POST":
        mes = request.form['mes']
        db.insert("ChatMessages", {"name": request.cookies.get('username'), "message": mes})
        response = make_response(render_template("chat.html"))
        response.set_cookie('username', value=request.cookies.get("username"))
        return response'''
    if request.cookies.get("username") and request.method == 'POST':
        data = request.json
        received_text = data.get('text')
        db.insert("ChatMessages", {"name": request.cookies.get('username'), "message": received_text})
        # Do something with the received text (e.g., print or process)
        print("Received text:", received_text)
        return "Text received successfully!", 200


@app.route('/mes')
def mes():
    text = '\n'.join([i['name'] + ': ' + i["message"] + ' #' + str(i["time"]) for i in list(db.select("ChatMessages"))])
    return jsonify(text)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4148)      #