from flask import Flask, render_template, request, url_for, redirect
from flask.helpers import make_response

from datetime import datetime, date
from decimal import Decimal


# add by wanjun, according to those previous templates from COMP 636 assessment
import re
from datetime import datetime
import mysql.connector
from mysql.connector import FieldType
import connect

from admin import app_admin
from trainer import app_trainer
from member import app_member
app = Flask(__name__)
app.register_blueprint(app_admin)
app.register_blueprint(app_trainer)
app.register_blueprint(app_member)

# DB connection
dbconn = None
connection = None


def getCursor():
    global dbconn
    global connection
    if dbconn == None:
        connection = mysql.connector.connect(user=connect.dbuser,
                                             password=connect.dbpass, host=connect.dbhost,
                                             database=connect.dbname, autocommit=True)
        dbconn = connection.cursor()
        return dbconn
    else:
        if connection.is_connected():
            return dbconn
        else:
            connection = None
            dbconn = None
            return getCursor()


@app.context_processor
def inject_user():
    user_id = request.cookies.get('user_id')
    user_name = request.cookies.get('user_name')
    user_role = request.cookies.get('user_role')
    return dict(user_id=user_id, user_name=user_name, user_role=user_role)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_email = request.form.get('user_email')
        user_password = request.form.get('user_password')
        cur = getCursor()
        cur.execute(
            "select user_pk, first_name, last_name, password, email, user_role from user;")
        users = cur.fetchall()
        for user in users:
            if user_email == user[4] and user_password == user[3]:
                user_id = str(user[0])
                user_name = user[1] + " " + user[2]
                user_role = str(user[5])
                resp = make_response(redirect('/'))
                # cookie does not accept integer value, so change it to string
                resp.set_cookie('user_id', user_id)
                resp.set_cookie('user_name', user_name)
                resp.set_cookie('user_role', user_role)
                return resp
            elif user_email == "" or user_password == "":
                return render_template('login.html',
                                       error_msg="You haven't entered your email or password.Please try again.")

        return render_template('login.html', users=users, error_msg="The email or password you entered is "
                                                                    "invalid. Please try again.")
    return render_template('login.html')


@app.route('/logout', methods=['GET'])
def logout():
    resp = make_response(redirect('/login'))
    resp.delete_cookie('user_id')
    resp.delete_cookie('user_name')
    resp.delete_cookie('user_role')
    return resp


@app.route("/")
def index():
    paymentpage = ""
    cancelautopay = ""
    user_id = request.cookies.get('user_id')
    user_name = request.cookies.get('user_name')
    user_role = request.cookies.get('user_role')

    if user_role == '1' or user_role == '2':  # trainer and member
        c = getCursor()
        c.execute("""select member.member_pk,member.reminder,member.subscription_expire_date,member.auto_pay 
        from member join user on user.user_pk = member.user_fk where user.user_pk = %s;""", (user_id,))
        member_id_data = c.fetchall()
        print("LENGTH: ", len(member_id_data))
        if len(member_id_data) > 0:  # member only will return results
            print("REMINDER: ", member_id_data[0][1])
            if member_id_data[0][1]:
                reminder = member_id_data[0][1]
                expire_date = member_id_data[0][2]

                autoPayStatus = member_id_data[0][3]
                print("AutoPay:", autoPayStatus)

                if reminder == 1 and autoPayStatus == 0:
                    paymentpage = 1
                    message = "Remember to renew your subscription! Your subscription expires on: " + \
                        expire_date.strftime("%d/%m/%Y")

                elif reminder == 1 and autoPayStatus == 1:
                    cancelautopay = 1
                    message = "Your auto-paying subscription is rolling over on: " + \
                        expire_date.strftime("%d/%m/%Y")
                else:
                    message = ""
            else:
                message = ""

            print("User ID: " + user_id)

            if user_role == '1':
                connection = getCursor()
                connection.execute(
                    """select news_pk,title,content,CONCAT(user.first_name,' ', user.last_name),
                    create_date from news join user on news.user_fk = user.user_pk order by news_pk desc;""")
                news_list = connection.fetchall()

            return render_template('index.html', message=message, user_id=user_id, paymentpage=paymentpage, news_list=news_list, cancelautopay=cancelautopay)
        else:  # for trainer as it will not return result
            return render_template('index.html')
    elif user_role == '0':  # admin only
        return render_template('index.html')
    # elif user_id:
    #     connection = getCursor()
    #     connection.execute(
    #         "select news_pk,title,content,CONCAT(user.first_name,' ', user.last_name),create_date from news join user on news.user_fk = user.user_pk order by news_pk desc;")

    #     news_list = connection.fetchall()
    #     print(news_list)
    #     return render_template('index.html', news_list=news_list)
    else:
        return redirect('/login')


if __name__ == "__main__":
    app.run(debug=True)
