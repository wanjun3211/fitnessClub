from flask import Blueprint, render_template, request, url_for, redirect
from flask.helpers import make_response
from datetime import datetime, date
from decimal import Decimal


# add by wanjun, according to those previous templates from COMP 636 assessment
import re
from datetime import datetime, date
import mysql.connector
from mysql.connector import FieldType
import connect

app_member = Blueprint('app_member', __name__)

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

# MEMBER

# View list of trainers and exercise sessions (victor)


@app_member.route('/member/class/', methods=['GET', 'POST'])
def trainer_and_exercise():

    # varible user_ID is from navbar.html after user clik link in the navbar left
    if request.method == 'GET':
        user_ID = request.args.get("memberid")
        connection = getCursor()
        connection.execute("select user_trainer.first_name, user_trainer.last_name, name, ec.description, ec.room, ec.time, ec.date, bk.booking_pk from user\
                       left join member as mb on user.user_pk=mb.user_fk \
                       left join booking as bk on mb.member_pk=bk.member_fk \
                       left join exerciseclass as ec on bk.exercise_class_fk=ec. exercise_class_pk \
                       left join trainer on trainer_pk=ec.trainer_fk left join user AS user_trainer on user_trainer.user_pk=trainer.user_fk\
                       where user.user_pk=%s and ec.name is not Null order by ec.date desc;", (user_ID,))
        exercise_data = connection.fetchall()
        connection.execute("select user_trainer.first_name, user_trainer.last_name, class_rate, sc.time, sc.date, bk.booking_pk from user\
                           left join member as mb on user.user_pk=mb.user_fk \
                           left join booking as bk on mb.member_pk=bk.member_fk \
                           left join specialisedclass as sc on sc.specialised_class_pk=bk.specialised_class_fk \
                           left join trainer on trainer.trainer_pk=sc.trainer_fk left join user as user_trainer on user_trainer.user_pk=trainer.user_fk\
                           where user.user_pk=%s and sc.class_rate is not Null order by sc.date desc;", (user_ID,))
        sepcial_training = connection.fetchall()
        return render_template("/member/class.html", exercise_Data=exercise_data, sepcial_Training=sepcial_training, user_iD=user_ID)

    # varible uer_ID is from payment_for_special_training.html after submitting the form
    else:
        user_ID = request.form.get("userID")
        book_id = request.form.get("bookingID")
        paid_amount = request.form.get("amount")
        special_training_pk = request.form.get("s_traing_pk")
        connection = getCursor()
        connection.execute("select user_trainer.first_name, user_trainer.last_name, name, ec.description, ec.room, ec.time, ec.date , bk.booking_pk from user\
                       left join member as mb on user.user_pk=mb.user_fk \
                       left join booking as bk on mb.member_pk=bk.member_fk \
                       left join exerciseclass as ec on bk.exercise_class_fk=ec. exercise_class_pk \
                       left join trainer on trainer_pk=ec.trainer_fk left join user AS user_trainer on user_trainer.user_pk=trainer.user_fk\
                       where user.user_pk=%s and ec.name is not Null order by ec.date desc;", (user_ID,))
        exercise_data = connection.fetchall()
        connection.execute("select user_trainer.first_name, user_trainer.last_name, class_rate, sc.time, sc.date, bk.booking_pk from user\
                           left join member as mb on user.user_pk=mb.user_fk \
                           left join booking as bk on mb.member_pk=bk.member_fk \
                           left join specialisedclass as sc on sc.specialised_class_pk=bk.specialised_class_fk \
                           left join trainer on trainer.trainer_pk=sc.trainer_fk left join user as user_trainer on user_trainer.user_pk=trainer.user_fk\
                           where user.user_pk=%s and sc.class_rate is not Null order by sc.date desc;", (user_ID,))
        sepcial_training = connection.fetchall()
        connection.execute(
            "SELECT member_pk FROM member WHERE user_fk = %s", (user_ID,))
        result = connection.fetchone()
        if result is None:
            # handle the case where no matching member is found
            return "No matching member found for user ID: {}".format(user_ID)
        member_pk = result[0]
        connection.reset()

        # Payment table need to be updated after booking, as the booking primary key is stored there.
        connection.execute("INSERT INTO payment (member_fk, booking_fk, amount, date, status) VALUES (%s, %s, %s, %s, %s)",
                           (member_pk, book_id, paid_amount, date.today(), 1))

        # insert a row to update the booking table for payment for special training
        connection.execute("INSERT INTO booking (member_fk, specialised_class_fk, exercise_class_fk) \
                       VALUES (%s, %s, %s);", (member_pk, special_training_pk, None))

        return render_template("/member/class.html", exercise_Data=exercise_data, sepcial_Training=sepcial_training, user_iD=user_ID)

# member View  profile (victor)


@app_member.route('/member/profile',  methods=['GET', 'POST'])
def member_profile():
    user_ID = request.args.get("memberid")
    connection = getCursor()
    connection.execute("select user.first_name,user.last_name, user.password, user.email, member.fitness_goals, member.subscription_expire_date\
                       from user inner join member on user.user_pk=member.user_fk\
                       where user.user_pk= %s;", (user_ID,))
    profile_data = connection.fetchall()
    return render_template("/member/profile.html", profile_Data=profile_data, MEMBER_id=user_ID)


# member update profile (victor)
@app_member.route('/edit/profile', methods=['POST'])
def member_profile_edit():
    user_ID = request.form.get('Member_id')
    connection = getCursor()
    connection.execute("select user.first_name,user.last_name, user.password, user.email, member.fitness_goals, member.subscription_expire_date\
                   from user inner join member on user.user_pk=member.user_fk\
                   where user.user_pk= %s;", (user_ID,))
    profile_data = connection.fetchall()
    return render_template("/member/profile_for_edit.html", profile_Data=profile_data, MEMBER_id=user_ID)

# present the updated profile to member(victor)


@app_member.route('/profile/edit', methods=['POST'])
def update_member_profile_edit():
    user_ID = request.form.get('Member_id')
    first_name = request.form.get('fname')
    last_name = request.form.get('lname')
    e_mail = request.form.get('email')
    fitness_new_goal = request.form.get('FG')
    connection1 = getCursor()
    connection1.execute("UPDATE user SET first_name=%s, last_name=%s, email=%s WHERE user_pk= %s;", (first_name, last_name,
                                                                                                     e_mail, user_ID))
    connection2 = getCursor()
    connection2.execute(
        "UPDATE member SET fitness_goals=%s WHERE user_fk= %s;", (fitness_new_goal, user_ID))
    connection3 = getCursor()
    connection3.execute("select user.first_name,user.last_name, user.password, user.email, member.fitness_goals, member.subscription_expire_date\
                       from user inner join member on user.user_pk=member.user_fk\
                       where user.user_pk= %s;", (user_ID,))
    profile_new_data = connection3.fetchall()
    return render_template("/member/updated_profile.html", profile_new_Data=profile_new_data)


# display traier information for special training
@app_member.route('/member/special_training/')
def special_training():
    if request.method == 'GET':
        user_id = request.args.get("memberid")
    connection = getCursor()
    connection.execute(
        "select * from trainer left join user on user.user_pk=trainer.user_fk ORDER BY trainer_pk;")
    sepcial_training = connection.fetchall()
    return render_template("member/special_training_trainer_information.html", sepcial_Training=sepcial_training,  user_Id=user_id)


# display available special training class for a chosen trainer
@app_member.route('/special/training_class', methods=['POST'])
def available_special_training_for_chosen_trainer():
    user_id = request.form.get('userID')
    trainer_ID = request.form.get('trainer_id')
    connection = getCursor()
    connection.execute("select * from specialisedclass as sc left join booking as bk on bk.specialised_class_fk=sc.specialised_class_pk \
                        where bk.booking_pk IS NULL and trainer_fk=%s;", (trainer_ID,))
    sepcial_training = connection.fetchall()
    return render_template("member/special_training_notbooked.html", sepcial_Training=sepcial_training, user_Id=user_id)


# present special training payment page(victor)
@app_member.route('/special_training/payment', methods=['POST'])
def update_bookin_and_display_payment_request():
    user_id = request.form.get('userID')
    speci_training_pk = request.form.get('speci_training_pk')
    print('test', user_id)
    print('test', speci_training_pk)

    # Get member_pk from user_id
    connection = getCursor()
    connection.execute(
        "SELECT member_pk FROM member WHERE user_fk = %s", (user_id,))
    result = connection.fetchone()
    print('result :', result)
    if result is None:
        # handle the case where no matching member is found
        return "No matching member found for user ID: {}".format(user_id)
    member_pk = result[0]
    print('test :', member_pk)

    connection.reset()
    cur = getCursor()
    #  obtain booking primary key to be used for later canceling and update payment table
    cur.execute(
        "select booking_pk from booking where specialised_class_fk=%s", (speci_training_pk,))
    bookingid = cur.fetchall()

 # obtain rate for a chosen special training class and display payment page for member to pay
    connection.execute(
        "SELECT * FROM specialisedclass where specialised_class_pk=%s", (speci_training_pk,))
    special_training_information = connection.fetchall()

    #  special_training_Information=special_training_information,
    return render_template("member/payment_for_special_training.html", special_training_Information=special_training_information, user_Id=user_id,
                           bookingId=bookingid,  speci_training_Pk=speci_training_pk)


# member cancel class afte booking (victor)
@app_member.route('/cancel/booking', methods=['POST'])
def cancel_booking():
    booking_pk = request.form.get('bookId')
    user_ID = request.form.get('userID')
    connection = getCursor()
    # payment table and booking table need to be delted together as both
    # have booking ID stored(primary key and foreign key)
    connection.execute(
        "DELETE FROM  payment  WHERE booking_fk= %s;", (booking_pk,))
    connection.execute(
        "DELETE FROM  booking  WHERE booking_pk= %s;", (booking_pk,))
    connection.execute("select user_trainer.first_name, user_trainer.last_name, name, ec.description, ec.room, ec.time, ec.date, bk.booking_pk from user\
                       left join member as mb on user.user_pk=mb.user_fk \
                       left join booking as bk on mb.member_pk=bk.member_fk \
                       left join exerciseclass as ec on bk.exercise_class_fk=ec. exercise_class_pk \
                       left join trainer on trainer_pk=ec.trainer_fk left join user AS user_trainer on user_trainer.user_pk=trainer.user_fk\
                       where user.user_pk=%s and ec.name is not Null order by ec.date desc;", (user_ID,))
    exercise_data = connection.fetchall()
    connection.execute("select user_trainer.first_name, user_trainer.last_name, class_rate, sc.time, sc.date, bk.booking_pk from user\
                           left join member as mb on user.user_pk=mb.user_fk \
                           left join booking as bk on mb.member_pk=bk.member_fk \
                           left join specialisedclass as sc on sc.specialised_class_pk=bk.specialised_class_fk \
                           left join trainer on trainer.trainer_pk=sc.trainer_fk left join user as user_trainer on user_trainer.user_pk=trainer.user_fk\
                           where user.user_pk=%s and sc.class_rate is not Null order by sc.date desc;", (user_ID,))
    sepcial_training = connection.fetchall()
    return render_template("/member/class.html", exercise_Data=exercise_data, sepcial_Training=sepcial_training, user_iD=user_ID)


@app_member.route('/member/payment', methods=['GET', 'POST'])
def payment():
    user_id = request.args.get('user_id')
    if request.method == 'POST':
        # Get form data from request object
        amount = request.form.get('amount')
        card_number = request.form.get('card_number')
        card_expiry = request.form.get('card_expiry')
        card_cvc = request.form.get('card_cvc')
        auto_pay = request.form.get('payment_type')

        # Get member_pk from user_id
        cursor = getCursor()
        cursor.execute(
            "SELECT member_pk FROM member WHERE user_fk = %s", (user_id,))
        result = cursor.fetchone()
        if result is None:
            # handle the case where no matching member is found
            return "No matching member found for user ID: {}".format(user_id)
        member_pk = result[0]

        # Determine auto_pay value based on checkbox selection
        auto_pay_value = 1 if auto_pay else 0

        # Update member data in database
        cursor.execute("UPDATE member SET card_num = %s, card_exp = %s, card_cvc = %s, auto_pay = %s, subscription_amount = %s, subscription_expire_date = DATE_ADD(CURDATE(), INTERVAL 1 MONTH) WHERE member_pk = %s",
                       (card_number, card_expiry, card_cvc, auto_pay_value, amount, member_pk))
        connection.commit()

        # Insert payment data into database
        cursor.execute("INSERT INTO payment (member_fk, booking_fk, amount, date, status) VALUES (%s, %s, %s, %s, %s)",
                       (member_pk, None, Decimal(amount), date.today(), 0))
        payment_id = cursor.lastrowid

        connection.commit()
        connection.close()

        # Redirect to payment success page
        return redirect(url_for('app_member.payment_success'))

    # Get auto_pay value from database
    cursor = getCursor()
    cursor.execute(
        "SELECT auto_pay FROM member WHERE user_fk = %s", (user_id,))
    result = cursor.fetchone()
    auto_pay = result[0]

    return render_template('/member/payment.html', user_id=user_id, auto_pay=auto_pay)


@app_member.route('/payment/success')
def payment_success():
    return render_template('/member/payment_success.html')


# Change password only


@app_member.route('/profile/edit/password', methods=['POST', 'GET'])
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
                '''UPDATE user join member on user.user_pk = member.user_fk SET user.password = %s WHERE user_pk = %s;''', (password, user_id,))
            message = "Password is changed successfully"

            c = getCursor()
            c.execute(
                "select user.first_name,user.last_name, user.password, user.email, member.fitness_goals, member.subscription_expire_date\
                        from user inner join member on user.user_pk=member.user_fk\
                        where user.user_pk= %s;", (user_id,))
            member = c.fetchall()

        return render_template('/member/profile.html', message=message, profile_Data=member)
    elif request.method == "GET":
        connection = getCursor()
        connection.execute(
            "select user.first_name,user.last_name, user.password, user.email, member.fitness_goals, member.subscription_expire_date\
                       from user inner join member on user.user_pk=member.user_fk\
                       where user.user_pk= %s;", (user_id,))
        member = connection.fetchall()

        return render_template('/member/profile_for_edit.html', profile_Data=member, changepassword=1)


# check-in Button for member(Beibei)
@app_member.route('/member',  methods=['GET', 'POST'])
def member_check_in():

    user_id = request.cookies.get('user_id')
    connection = getCursor()
    connection.execute(
        "select member.member_pk from member join user on user.user_pk = member.user_fk where user.user_pk=%s;",
        (user_id,))
    member_id_data = connection.fetchall()
    member_id = member_id_data[0][0]

    if request.method == 'POST':
        connection1 = getCursor()
        connection1.execute(
            """Select booking_pk,member_fk,specialisedclass.trainer_fk,specialisedclass.time,specialisedclass.date from booking
                inner join specialisedclass on booking.specialised_class_fk= specialisedclass.specialised_class_pk
                where member_fk = %s and specialisedclass.time BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 30 MINUTE);""", (member_id,))
        specialised_class_book = connection1.fetchall()

        connection2 = getCursor()
        connection2.execute(
            """Select booking_pk,member_fk,exerciseclass.name,exerciseclass.time,exerciseclass.date from booking
                inner join exerciseclass on booking.exercise_class_fk= exerciseclass.exercise_class_pk
                where member_fk = %s and exerciseclass.time BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 30 MINUTE);""", (member_id,))
        exercise_class_book = connection2.fetchall()

        if specialised_class_book:
            connection3 = getCursor()
            time_str = str(specialised_class_book[0][3])
            time = datetime.strptime(time_str, '%H:%M:%S').time()
            new_date = datetime.combine(datetime.now(), time)
            connection3.execute(
                """ INSERT INTO `attendance` (`member_fk`, `attendance_type`, `date`, `start_time`, `end_time`)
                VALUES(%s, 'Specialised class', CURDATE(), CURTIME(), date_add(%s, interval 1 hour));""", (member_id, new_date,))
        elif exercise_class_book:
            connection3 = getCursor()
            time_str = str(exercise_class_book[0][3])
            time = datetime.strptime(time_str, '%H:%M:%S').time()
            new_date = datetime.combine(datetime.now(), time)
            connection3.execute(
                """ INSERT INTO `attendance` (`member_fk`, `attendance_type`, `date`, `start_time`, `end_time`)
                VALUES(%s, 'Exercise class', CURDATE(), CURTIME(), date_add(%s, interval 1 hour));""", (member_id, new_date,))
        else:
            connection3 = getCursor()
            connection3.execute(
                """ INSERT INTO `attendance` (`member_fk`, `attendance_type`, `date`, `start_time`, `end_time`)
                VALUES(%s, 'GYM', CURDATE(), CURTIME(), date_add(CURTIME(), interval 1 hour));""", (member_id, ))

    return render_template('index.html', message=message)


# Book a Exercise class function to member(Beibei)


@app_member.route('/member/bookclass', methods=['GET', 'POST'])
def book_exercise_class():
    user_id = request.cookies.get('user_id')
    connection2 = getCursor()
    connection2.execute(
        "select member.member_pk from member join user on user.user_pk = member.user_fk where user.user_pk=%s;", (user_id,))
    member_id_data = connection2.fetchall()
    member_id = member_id_data[0][0]

    sort_by = request.args.get('sort_by')
    booked = request.args.get('booked')
    # Get sort results
    if request.method == 'POST':
        sort_by = request.form.get('inputGroupSelect')
    # Get the class id of button
    elif request.method == 'GET':
        class_id = request.args.get('class_id')
        if class_id != None:
            # Cancel booking button function
            connection1 = getCursor()
            if booked == "1":
                connection1.execute(
                    "DELETE FROM booking WHERE member_fk = %s and exercise_class_fk = %s ", (member_id, class_id))
            # Booking button function
            else:
                connection1.execute(
                    "INSERT INTO booking (member_fk,exercise_class_fk) VALUES(%s, %s); ", (member_id, class_id))

    # Set default values for sort
    if sort_by == None:
        sort_by = 'week'

    # # Three ways for sort
    connection = getCursor()
    if sort_by == 'week':
        connection.execute("""select exerciseclass.exercise_class_pk,exerciseclass.name, CONCAT(user.first_name,' ', user.last_name), exerciseclass.room ,date,time,(30 - count(booking.exercise_class_fk)),exerciseclass.description,IF(sum(booking.member_fk = %s),1,0)
            from exerciseclass
            left join booking on exerciseclass.exercise_class_pk = booking.exercise_class_fk
            join trainer on  exerciseclass.trainer_fk = trainer.trainer_pk
            join user on trainer.user_fk= user.user_pk
            where date > NOW() AND date < DATE_ADD(NOW(), INTERVAL 7 DAY)
            group by exerciseclass.exercise_class_pk
            order by date,time ;""", (member_id,))
    elif sort_by == 'month':
        connection.execute("""select exerciseclass.exercise_class_pk,exerciseclass.name,CONCAT(user.first_name,' ', user.last_name), exerciseclass.room,date,time,(30 - count(booking.exercise_class_fk)),exerciseclass.description,IF(sum(booking.member_fk = %s),1,0)
            from exerciseclass
            left join booking on exerciseclass.exercise_class_pk = booking.exercise_class_fk
            join trainer on  exerciseclass.trainer_fk = trainer.trainer_pk
            join user on trainer.user_fk= user.user_pk
            WHERE date between NOW() and DATE_ADD(NOW(), INTERVAL 1 MONTH)
            group by exerciseclass.exercise_class_pk
            order by date,time ; """, (member_id,))
    elif sort_by == 'quarter':
        connection.execute("""select exerciseclass.exercise_class_pk,exerciseclass.name, CONCAT(user.first_name,' ', user.last_name), exerciseclass.room ,date,time,(30 - count(booking.exercise_class_fk)),exerciseclass.description,IF(sum(booking.member_fk = %s),1,0)
            from exerciseclass
            left join booking on exerciseclass.exercise_class_pk = booking.exercise_class_fk
            join trainer on  exerciseclass.trainer_fk = trainer.trainer_pk
            join user on trainer.user_fk= user.user_pk
            WHERE date between NOW() and DATE_ADD(NOW(), INTERVAL 3 MONTH)
            group by exerciseclass.exercise_class_pk
            order by date,time ; """, (member_id,))

    class_data = connection.fetchall()

    return render_template("/member/book_exercise_class.html", class_data=class_data, sort_by=sort_by)

# Reminders (Sabrina)


@app_member.route("/member/reminder", methods=['GET', 'POST'])
def updateReminder():
    if request.method == "POST":
        if 'paynow-reminder' in request.form:
            print("I AM GOING TO THE PAYMENT PAGE")
            amount = 50  # Need to set this value for monthly subscription
            user_id = request.form.get("user_id")
            print(user_id)
            connection = getCursor()
            connection.execute("""update member m 
            inner join user u
            on m.user_fk = u.user_pk
            SET m.reminder = NULL
            WHERE u.user_pk = %s;""", (user_id,))
            return render_template('/member/payment.html', amount=amount)
        elif 'cancel-autopay' in request.form:
            user_id = request.form.get("user_id")
            connection = getCursor()
            connection.execute("""update member m 
            inner join user u
            on m.user_fk = u.user_pk
            SET m.auto_pay = 0
            WHERE u.user_pk = %s;""", (user_id,))

            return redirect(url_for('index'))
        elif 'acknowledge' in request.form:
            user_id = request.form.get("user_id")
            print(user_id)
            connection = getCursor()
            connection.execute("""update member m 
            inner join user u
            on m.user_fk = u.user_pk
            SET m.reminder = NULL
            WHERE u.user_pk = %s;""", (user_id,))

            print("UPDATED")

            return redirect(url_for('index'))
