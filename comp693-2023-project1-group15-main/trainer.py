from flask import Blueprint, render_template, request, url_for, redirect
from flask.helpers import make_response

# add by wanjun, according to those previous templates from COMP 636 assessment
import re
from datetime import datetime
import mysql.connector
from mysql.connector import FieldType
import connect
import datetime
from datetime import date, timedelta


app_trainer = Blueprint('app_trainer', __name__)

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

# TRAINER


@app_trainer.route('/trainer/profile')
def trainer_profile():
    # Fetch the trainer's information from the database using their user_id

    user_id = request.cookies.get('user_id')
    connection = getCursor()
    connection.execute(
        "SELECT first_name, last_name, email, description FROM user inner join trainer on user.user_pk = trainer.user_fk where user_pk = %s;", (user_id,))
    trainer = connection.fetchall()

    return render_template('/trainer/trainer_profile.html', trainer=trainer)


@app_trainer.route('/trainer/profile/update', methods=['GET', 'POST'])
def update_profile():
    user_id = request.cookies.get('user_id')
    if request.method == 'GET':
        connection = getCursor()
        connection.execute(
            "SELECT first_name, last_name, email, description FROM user inner join trainer on user.user_pk = trainer.user_fk where user_pk = %s;", (user_id,))
        trainer = connection.fetchall()

        return render_template('/trainer/update_profile.html', trainer=trainer)
    else:
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        description = request.form.get('description')
        connection = getCursor()
        connection.execute('''UPDATE user join trainer on user.user_pk = trainer.user_fk SET user.first_name = %s, user.last_name = %s, user.email = %s,
          trainer.description = %s WHERE user_pk = %s;''', (firstname, lastname, email, description, user_id,))
        return redirect(url_for('app_trainer.trainer_profile'))


@app_trainer.route('/trainer/profile/changepassword', methods=['GET', 'POST'])
def changepassword():
    user_id = request.cookies.get('user_id')
    if request.method == "POST":

        password = request.form.get('newpass')
        confirm_password = request.form.get('newpass2')

        if password != confirm_password:
            message = "Passwords do not match"
        else:
            connection = getCursor()
            connection.execute(
                '''UPDATE user join trainer on user.user_pk = trainer.user_fk SET user.password = %s WHERE user_pk = %s;''', (password, user_id,))
            message = "Password is changed successfully"

            c = getCursor()
            c.execute(
                "SELECT first_name, last_name, email, description FROM user inner join trainer on user.user_pk = trainer.user_fk where user_pk = %s;", (user_id,))
            trainer = c.fetchall()

        return render_template('/trainer/trainer_profile.html', message=message, trainer=trainer)
    elif request.method == "GET":
        connection = getCursor()
        connection.execute(
            "SELECT password FROM user inner join trainer on user.user_pk = trainer.user_fk where user_pk = %s;", (user_id,))
        trainer = connection.fetchall()

        return render_template('/trainer/update_profile.html', trainer=trainer, changepassword=1)

    # if request.method == 'GET':
    #     connection = getCursor()
    #     connection.execute(
    #         "SELECT first_name, last_name, email, password, description FROM user inner join trainer on user.user_pk = trainer.user_fk where user_pk = %s;", (user_id,))
    #     trainer = connection.fetchall()
    #     return render_template('/trainer/update_profile.html', trainer=trainer)
    # else:
    #     firstname = request.form.get('firstname')
    #     lastname = request.form.get('lastname')
    #     email = request.form.get('email')
    #     description = request.form.get('description')
    #     connection = getCursor()
    #     connection.execute('''UPDATE user join trainer on user.user_pk = trainer.user_fk SET user.first_name = %s, user.last_name = %s, user.email = %s,
    #       trainer.description = %s WHERE user_pk = %s;''', (firstname, lastname, email, description, user_id,))
    #     return redirect(url_for('app_trainer.trainer_profile'))


@app_trainer.route('/trainer/viewtrainee', methods=['GET', 'POST'])
def view_trainee_info():
    user_id = request.cookies.get('user_id')
    sort_by_id = True
    sort_time = 'all'
    start_time = datetime.date.today()
    end_time = '2500-01-01'
    connection = getCursor()
    search_info = True
    history_info_display = request.args.get('history_info')
    if request.method == 'GET':
        if history_info_display == "1":
            start_time = '1900-01-01'
            end_time = datetime.date.today()
    elif request.method == 'POST':
        search = request.form.get('search')
        if search != None:
            search_info = False

        else:
            sort_by_id = request.form.get('options') == "sort_id"
            sort_time = request.form.get('inputGroupSelect')
            # Set default values for sort
            if sort_time == None:
                sort_time = 'all'
            elif sort_time == 'week':
                end_time = start_time + datetime.timedelta(days=7)
            elif sort_time == 'month':
                end_time = start_time + datetime.timedelta(days=30)

    if search_info:
        if sort_by_id:
            connection.execute('''select member.member_pk, member.fitness_goals, user.first_name, user.last_name, user.email, specialisedclass.date AS date, 
                specialisedclass.time AS time,
                'specialisedclass' AS class_name
                from member inner join user on member.user_fk = user.user_pk 
                    inner join booking
                    on member.member_pk = booking.member_fk 
                    inner join specialisedclass on booking.specialised_class_fk = specialisedclass.specialised_class_pk 
                    inner join trainer on specialisedclass.trainer_fk = trainer.trainer_pk  where trainer.user_fk = %s AND date between %s and %s
                    union 
                    select member.member_pk, member.fitness_goals, user.first_name, user.last_name, user.email, exerciseclass.date AS date, 
               exerciseclass.time AS time,
                'exerciseclass' AS class_name
                 from member inner join user on member.user_fk = user.user_pk 
                    inner join booking
                    on member.member_pk = booking.member_fk 
                    inner join exerciseclass on booking.exercise_class_fk = exerciseclass.exercise_class_pk 
                    inner join trainer on exerciseclass.trainer_fk = trainer.trainer_pk where trainer.user_fk = %s  AND date between %s and %s order by member_pk;''',
                               (user_id, start_time,end_time,user_id,start_time,end_time,))
        else:
            connection.execute('''select member.member_pk, member.fitness_goals, user.first_name, user.last_name, user.email, specialisedclass.date AS date, 
                specialisedclass.time AS time,
                'specialisedclass' AS class_name
                from member inner join user on member.user_fk = user.user_pk 
                    inner join booking
                    on member.member_pk = booking.member_fk 
                    inner join specialisedclass on booking.specialised_class_fk = specialisedclass.specialised_class_pk 
                    inner join trainer on specialisedclass.trainer_fk = trainer.trainer_pk  where trainer.user_fk = %s AND date between %s and %s
                    union 
                    select member.member_pk, member.fitness_goals, user.first_name, user.last_name, user.email, exerciseclass.date AS date, 
                exerciseclass.time AS time,
                'exerciseclass' AS class_name
                 from member inner join user on member.user_fk = user.user_pk 
                    inner join booking
                    on member.member_pk = booking.member_fk 
                    inner join exerciseclass on booking.exercise_class_fk = exerciseclass.exercise_class_pk 
                    inner join trainer on exerciseclass.trainer_fk = trainer.trainer_pk where trainer.user_fk = %s AND date between %s and %s order by first_name;''',
                               (user_id, start_time,end_time,user_id,start_time,end_time,))

    else:
        connection.execute('''select member.member_pk, member.fitness_goals, user.first_name, user.last_name, user.email,specialisedclass.date AS date, 
                    specialisedclass.time AS time,
                    'specialisedclass' AS class_name
                          from member inner join user on member.user_fk = user.user_pk 
                                inner join booking
                                on member.member_pk = booking.member_fk 
                                inner join specialisedclass on booking.specialised_class_fk = specialisedclass.specialised_class_pk 
                                inner join trainer on specialisedclass.trainer_fk = trainer.trainer_pk  where trainer.user_fk = %s
                                AND (user.first_name LIKE %s OR user.last_name LIKE %s OR member.member_pk = %s) 
                                union 
                                select member.member_pk, member.fitness_goals, user.first_name, user.last_name, user.email, exerciseclass.date AS date, 
                    exerciseclass.time AS time,
                    'exerciseclass' AS class_name
                      from member inner join user on member.user_fk = user.user_pk 
                                inner join booking
                                on member.member_pk = booking.member_fk 
                                inner join exerciseclass on booking.exercise_class_fk = exerciseclass.exercise_class_pk 
                                inner join trainer on exerciseclass.trainer_fk = trainer.trainer_pk where trainer.user_fk = %s 
                                AND (user.first_name LIKE %s OR user.last_name LIKE %s OR member.member_pk = %s);''',
                           (user_id, search, search, search, user_id, search,search,search,))

    traineeList = connection.fetchall()

    return render_template('/trainer/view_trainee_info.html', traineelist=traineeList, sort_by_id=sort_by_id,sort_time=sort_time,history_info_display=history_info_display)
