from flask import Blueprint, render_template, request, url_for, redirect
from flask.helpers import make_response

# add by wanjun, according to those previous templates from COMP 636 assessment
import re
from datetime import datetime
import mysql.connector
from mysql.connector import FieldType
import connect
from flask import jsonify

app_admin = Blueprint('app_admin', __name__)

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

# Admin - showing members


@app_admin.route('/admin/members')
def members():
    connection = getCursor()
    connection.execute(
        """SELECT member.member_pk AS "ID", user.first_name AS "First Name", user.last_name AS "Last Name", user.password AS "Password", user.email AS "Email",
        member.fitness_goals AS "Fitness Goals", member.subscription_expire_date AS "Expire Date", member.active AS "Active Status", user.user_pk
        FROM user
        INNER JOIN member ON user.user_pk = member.user_fk;""")
    # memberslist = connection.fetchall()

    select_result = connection.fetchall()
    # getting values for colmn headers
    column_names = [desc[0] for desc in connection.description]
    return render_template('/admin/members.html', memberslist=select_result, membercols=column_names)

# Active vs Inactive Status


@app_admin.route('/admin/update', methods=['GET', 'POST'])
def activate_member():
    member_id = request.args.get('MemberID')
    cur = getCursor()
    cur.execute(
        "UPDATE member SET active = CASE WHEN active = 1 THEN 0 ELSE 1 END WHERE member_pk = %s", (member_id,))
    connection.commit()
    return redirect('/admin/members')

# Add Members


@app_admin.route('/admin/addmember', methods=['GET', 'POST'])
def addMember():
    if request.method == 'POST':
        first_name = request.form.get('firstname')
        last_name = request.form.get('lastname')
        password = request.form.get('password')
        email = request.form.get('email')
        fitnessgoals = request.form.get('fitnessgoals')
        connection = getCursor()
        connection.execute("""INSERT INTO user (first_name, last_name, password, email, user_role)
        VALUES (%s,%s,%s,%s,1);""", (first_name, last_name, password, email))

        connection.execute("""INSERT INTO member (fitness_goals,subscription_expire_date,auto_pay,active,user_fk)
        VALUES (%s, DATE_ADD(NOW(), INTERVAL 30 DAY),0,1,LAST_INSERT_ID());""", (fitnessgoals,))
        message = 'New Member Added Successfully'

        c = getCursor()
        c.execute("""SELECT member.member_pk AS "ID", user.first_name AS "First Name", user.last_name AS "Last Name", user.password AS "Password", user.email AS "Email",
        member.fitness_goals AS "Fitness Goals", member.subscription_expire_date AS "Expire Date", member.active AS "Active Status", user.user_pk
        FROM user
        INNER JOIN member ON user.user_pk = member.user_fk;""")
        memberslist = c.fetchall()
        if len(memberslist) > 0:
            message = "Member Added Successfully!"
        else:
            message = "Member cannot be added. Please try again!"

        column_names = [desc[0] for desc in c.description]

        return render_template('/admin/members.html', message=message, memberslist=memberslist, membercols=column_names)
    elif request.method == 'GET':
        return render_template('/admin/addmember.html')


@app_admin.route('/admin/searchmember', methods=['GET', 'POST'])
def searchMember():
    if request.method == 'POST':
        memberID = request.form.get("ID")
        connection = getCursor()

        try:
            connection.execute("""SELECT member.member_pk AS "ID", user.first_name AS "First Name", user.last_name AS "Last Name", user.password AS "Password", user.email AS "Email",
            member.fitness_goals AS "Fitness Goals", member.subscription_expire_date AS "Expire Date", member.active AS "Active Status", user.user_pk
            FROM user
            INNER JOIN member ON user.user_pk = member.user_fk
                        where member.member_pk = %s;""", (memberID,))

        except Exception as e:
            message = str(e)

        memberslist = connection.fetchall()
        if len(memberslist) > 0:
            message = "Member Found!"
        else:
            message = "This member is not in the database. Please try again!"
        return render_template('/admin/members.html', memberslist=memberslist, message=message)


@app_admin.route('/admin/sortmember/subscriptionstatus')
def sortMemberSubscription():
    connection = getCursor()
    connection.execute("""SELECT member.member_pk AS "ID", user.first_name AS "First Name", user.last_name AS "Last Name", user.password AS "Password", user.email AS "Email",
        member.fitness_goals AS "Fitness Goals", member.subscription_expire_date AS "Expire Date", member.active AS "Active Status", user.user_pk
        FROM user
        INNER JOIN member ON user.user_pk = member.user_fk
        ORDER BY member.active DESC,user.first_name ASC;""")
    memberslist = connection.fetchall()

    message = "Member is sorted by active members to inactive members"

    return render_template('/admin/members.html', memberslist=memberslist, message=message)


@app_admin.route('/admin/sortmember/membername')
def sortMemberName():
    connection = getCursor()
    connection.execute("""SELECT member.member_pk AS "ID", user.first_name AS "First Name", user.last_name AS "Last Name", user.password AS "Password", user.email AS "Email",
        member.fitness_goals AS "Fitness Goals", member.subscription_expire_date AS "Expire Date", member.active AS "Active Status", user.user_pk
        FROM user
        INNER JOIN member ON user.user_pk = member.user_fk
        ORDER BY user.first_name;""")
    memberslist = connection.fetchall()

    message = "Member is sorted by member ID"

    return render_template('/admin/members.html', memberslist=memberslist, message=message)


@app_admin.route('/admin/updatemember', methods=['GET', 'POST'])
def updateMember():
    if request.method == 'POST':
        memberID = request.form.get("ID")
        connection = getCursor()

        try:
            connection.execute("""SELECT member.member_pk AS "ID", user.first_name AS "First Name", user.last_name AS "Last Name", user.password AS "Password", user.email AS "Email",
            member.fitness_goals AS "Fitness Goals", member.subscription_expire_date AS "Expire Date", member.active AS "Active Status", user.user_pk
            FROM user
            INNER JOIN member ON user.user_pk = member.user_fk
                        where member.member_pk = %s;""", (memberID,))

        except Exception as e:
            message = str(e)

        memberslist = connection.fetchall()
        if len(memberslist) > 0:
            message = "Member Found!"
        else:
            message = "This member is not in the database. Please try again!"
        return render_template('/admin/updatemember.html', memberslist=memberslist, message=message)

    # elif request.method == 'GET':
    #     return render_template('/admin/updatemember.html')


@app_admin.route('/admin/updatemember/submit', methods=['GET', 'POST'])
def updateMembertodatabase():
    if request.method == "POST":
        first_name = request.form.get('firstname')
        last_name = request.form.get('lastname')
        password = request.form.get('password')
        email = request.form.get('email')
        fitnessgoals = request.form.get('fitnessgoals')
        id = request.form.get('id')
        connection = getCursor()
        connection.execute("""update user u
                    inner join member m
                    on u.user_pk = m.user_fk
                    SET u.first_name = %s,
                    u.last_name = %s, u.password = %s, u.email=%s,
                    m.fitness_goals = %s
                    where u.user_pk = %s;""", (first_name, last_name, password, email, fitnessgoals, id,))

        c = getCursor()
        c.execute("""SELECT member.member_pk AS "ID", user.first_name AS "First Name", user.last_name AS "Last Name", user.password AS "Password", user.email AS "Email",
            member.fitness_goals AS "Fitness Goals", member.subscription_expire_date AS "Expire Date", member.active AS "Active Status", user.user_pk
            FROM user
            INNER JOIN member ON user.user_pk = member.user_fk;""")
        memberslist = c.fetchall()

        if len(memberslist) > 0:
            message = "Member details was changed successfully!"
        else:
            message = "The member details cannot be changed. Please try again!"

        # getting values for colmn headers
        column_names = [desc[0] for desc in c.description]

        return render_template("/admin/members.html", id=id, message=message, memberslist=memberslist, membercols=column_names)

    elif request.method == 'GET':
        return render_template('/admin/updatemember.html')


# Global Variable for memberid for the duration of the attendance function
memberid_attendance = 0


@app_admin.route('/admin/attendance', methods=['GET', 'POST'])
def attendance():
    if request.method == "POST":

        if 'searchbutton' in request.form:
            memberID = request.form['ID']
            global memberid_attendance
            memberid_attendance = memberID
            connection = getCursor()
            connection.execute("""SELECT m.member_pk, u.first_name, u.last_name, a.attendance_type,a.date,a.start_time,a.end_time FROM attendance a
                inner join member m
                on m.member_pk = a.member_fk
                inner join user u
                on m.user_fk = u.user_pk
                where m.member_pk = %s;""", (memberid_attendance,))

        elif 'filterbydatebutton' in request.form:
            startdate = request.form["startdate"]
            enddate = request.form["enddate"]
            if len(enddate) == 0:
                enddate = startdate

            connection = getCursor()
            connection.execute("""SELECT m.member_pk, u.first_name, u.last_name, a.attendance_type,a.date,a.start_time,a.end_time FROM attendance a
                inner join member m
                on m.member_pk = a.member_fk
                inner join user u
                on m.user_fk = u.user_pk
                where a.date between %s and %s and m.member_pk = %s
                order by a.date;""", (startdate, enddate, memberid_attendance))

        elif 'filterbytypebutton' in request.form:
            type = request.form["type"]
            connection = getCursor()
            connection.execute("""SELECT m.member_pk, u.first_name, u.last_name, a.attendance_type,a.date,a.start_time,a.end_time FROM attendance a
                inner join member m
                on m.member_pk = a.member_fk
                inner join user u
                on m.user_fk = u.user_pk
                where a.attendance_type = %s and m.member_pk = %s;""", (type, memberid_attendance))

        attendancelist = connection.fetchall()

        if len(attendancelist) > 0:
            if 'searchbutton' in request.form:
                message = "Member found"
            elif 'filterbydatebutton' in request.form:
                message = "Member's records found"
            elif 'filterbytypebutton' in request.form:
                message = "Member's records found"
        else:
            if 'searchbutton' in request.form:
                message = "The member is not found. Try again!"
            else:
                if 'filterbydatebutton' in request.form:
                    message = "This date range is not available for this member"
                elif 'filterbytypebutton' in request.form:
                    message = 'This type is not available for this member'
                connection.execute("""SELECT m.member_pk, u.first_name, u.last_name, a.attendance_type,a.date,a.start_time,a.end_time FROM attendance a
                inner join member m
                on m.member_pk = a.member_fk
                inner join user u
                on m.user_fk = u.user_pk
                where m.member_pk = %s;""", (memberid_attendance,))
                attendancelist = connection.fetchall()

        return render_template('/admin/attendance.html', attendancelist=attendancelist, message=message)

    else:
        connection = getCursor()
        connection.execute("""SELECT m.member_pk, u.first_name, u.last_name, a.attendance_type,a.date,a.start_time,a.end_time FROM attendance a
            inner join member m
            on m.member_pk = a.member_fk
            inner join user u
            on m.user_fk = u.user_pk;""")
        attendancelist = connection.fetchall()
        return render_template('/admin/attendance.html', attendancelist=attendancelist, filters=0)


@app_admin.route('/admin/classes', methods=['GET', 'POST'])
def classes():
    return render_template('/admin/classes.html')

@app_admin.route('/admin/payment', methods=['GET'])
def admin_payment():
    cur = getCursor()
    cur.execute('SELECT payment_pk, member_fk, booking_fk, amount, date FROM payment WHERE status=0')
    payments = cur.fetchall()
    payment_details = []
    for payment in payments:
        cur.execute('SELECT first_name, last_name FROM user WHERE user_pk=(SELECT user_fk FROM member WHERE member_pk=%s)', (payment[1],))
        member_name = cur.fetchone()
        payment_detail = {
            'payment_id': payment[0],
            'member_name': f'{member_name[0]} {member_name[1]}',
            'amount': payment[3],
            'date': payment[4],
        }
        payment_details.append(payment_detail)
    if payment_details:
        return render_template('/admin/admin_payment.html', payment_details=payment_details)
    else:
        return render_template('/admin/no_payments.html')

@app_admin.route('/submit_payment_id', methods=['POST'])
def submit_payment_id():
    payment_id = request.json.get('payment_id')
    if payment_id:
        cur = getCursor()
        cur.execute('UPDATE payment SET status=%s WHERE payment_pk=%s', (1, payment_id))
        return jsonify({'message': 'Payment ID submitted successfully!'})
    else:
        return jsonify({'error': 'Payment ID not provided.'}), 400

filterResults = []


@app_admin.route('/admin/reminder', methods=['GET', 'POST'])
def reminder():
    global filterResults
    if request.method == "GET":
        connection = getCursor()
        connection.execute("""SELECT member.member_pk AS "ID", user.first_name AS "First Name", user.last_name AS "Last Name", member.subscription_expire_date AS "Expire Date", user.user_pk
            , member.auto_pay FROM user
            INNER JOIN member ON user.user_pk = member.user_fk
            where member.active = 1;""")
        memberslist = connection.fetchall()
        message = "Only active members are shown in this list!"
        alertStyling = "Yellow"
        return render_template('/admin/reminder.html', memberslist=memberslist, message=message, filterOn=1, alertStyling=alertStyling)
    elif request.method == "POST":
        if 'search-reminder' in request.form:
            print("I AM IN THE SEARCH BAR")
            memberID = request.form.get('ID')
            connection = getCursor()
            connection.execute("""SELECT member.member_pk AS "ID", user.first_name AS "First Name", user.last_name AS "Last Name", member.subscription_expire_date AS "Expire Date"
            , user.user_pk, member.auto_pay
            FROM user
            INNER JOIN member ON user.user_pk = member.user_fk
            where member.member_pk = %s and member.active = 1;""", (memberID,))
            memberslist = connection.fetchall()
            filterResults = memberslist
            if len(memberslist) > 0:
                afterSearch = 1
                autoPayStatus = memberslist[0][5]
                if autoPayStatus == 1:
                    message = "Member found and this member has an auto-payment"
                    alertStyling = "Green"

                elif autoPayStatus == 0:
                    message = "Member found and this member does not have auto-payment"
                    alertStyling = "Yellow"

            else:
                message = "Member is not found!"
                alertStyling = "Red"
                afterSearch = 0

            return render_template('/admin/reminder.html', memberslist=memberslist, message=message, fullList=1, alertStyling=alertStyling, afterSearch=afterSearch)
        elif 'filter' in request.form:
            filter_value = request.form.get('filter_number')
            connection = getCursor()
            connection.execute("""SELECT member.member_pk AS "ID", user.first_name AS "First Name", user.last_name AS "Last Name",
                member.subscription_expire_date AS "Expire Date", user.user_pk, member.auto_pay
                FROM user
                INNER JOIN member ON user.user_pk = member.user_fk
                WHERE member.subscription_expire_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(),INTERVAL %s DAY) AND member.active = 1;""", (filter_value,))
            memberslist = connection.fetchall()
            length = len(memberslist)

            if length > 0:
                message = f"There are {length} that have expiring subscription in {filter_value} days."
                alertStyling = "Green"
                afterSearch = 1
            else:
                message = "There are no expiring subscription in the current members list."
                alertStyling = "Red"
                afterSearch = 0

            filterResults = memberslist
            print("Filter in the filter if: ", filterResults)
            return render_template('/admin/reminder.html', memberslist=memberslist, message=message, fullList=1, alertStyling=alertStyling, afterSearch=afterSearch)

        elif 'send-reminder' in request.form:
            connection = getCursor()
            print('Filter: ', filterResults)
            for member in filterResults:
                memberID = member[0]
                print("member: ", memberID)

                connection.execute("""UPDATE member 
                    set member.reminder = 1
                    where member.member_pk = %s;""", (memberID,))
                print("GOING AROUND LOOP")
            length = len(filterResults)
            print("DONE")
            message = f"Reminder sent to {length} members!"
            alertStyling = "Green"

            connection = getCursor()
            connection.execute("""SELECT member.member_pk AS "ID", user.first_name AS "First Name", user.last_name AS "Last Name", member.subscription_expire_date AS "Expire Date", user.user_pk
                , member.auto_pay FROM user
                INNER JOIN member ON user.user_pk = member.user_fk
                where member.active = 1;""")
            memberslist = connection.fetchall()

            return render_template('/admin/reminder.html', memberslist=memberslist, message=message, fullList=1, alertStyling=alertStyling)

        elif 'full-list' in request.form:
            return redirect('/admin/reminder')

        else:

            message = "Please enter the number of days to filter"
            alertStyling = "Red"

            return render_template('/admin/reminder.html', message=message, fullList=1, alertStyling=alertStyling)


# Admin - showing trainer class
@app_admin.route('/admin/trainers_information')
def trainers_class():
    connection = getCursor()
    connection.execute(
        """select user.first_name, user.last_name, trainer.trainer_pk, sc.time,sc.date from specialisedclass as sc left join 
            trainer on sc.trainer_fk=trainer.trainer_pk 
            left join user on user.user_pk=trainer.user_fk
            union all
            select user.first_name, user.last_name, trainer.trainer_pk, ec.time,ec.date from exerciseclass as ec left join 
            trainer on ec.trainer_fk=trainer.trainer_pk 
            left join user on user.user_pk=trainer.user_fk order by date desc;""")
    trainer_class_information = connection.fetchall()
    return render_template('/admin/class_trainers.html', trainer_class_Information=trainer_class_information)


# Admin - showing trainer class by searching trainer ID and name
@app_admin.route('/admin/trainers_information/search', methods=['POST'])
def trainers_class_search_result():
    connection = getCursor()
    searchterm1 = request.form.get('Tname')
    if searchterm1 != '':
        searchterm1 = "%" + searchterm1 + "%"
        connection.execute("select user.first_name, user.last_name, trainer.trainer_pk, sc.time,sc.date from specialisedclass as sc left join \
                             trainer on sc.trainer_fk=trainer.trainer_pk \
                             left join user on user.user_pk=trainer.user_fk where first_name like %s or last_name like %s  \
                             union all\
                             select user.first_name, user.last_name, trainer.trainer_pk, ec.time,ec.date from exerciseclass as ec left join \
                             trainer on ec.trainer_fk=trainer.trainer_pk \
                             left join user on user.user_pk=trainer.user_fk where first_name like %s or last_name like %s order by date desc;", (searchterm1, searchterm1, searchterm1, searchterm1))
        search_trainer_name = connection.fetchall()
    else:
        search_trainer_name = False

    searchterm2 = request.form.get('Tid')
    if searchterm2 != '':
        searchterm2 = "%" + searchterm2 + "%"
        connection = getCursor()
        connection.execute("select user.first_name, user.last_name, trainer.trainer_pk, sc.time,sc.date from specialisedclass as sc left join \
                             trainer on sc.trainer_fk=trainer.trainer_pk \
                             left join user on user.user_pk=trainer.user_fk where trainer_pk like %s\
                             union all\
                             select user.first_name, user.last_name, trainer.trainer_pk, ec.time,ec.date from exerciseclass as ec left join \
                             trainer on ec.trainer_fk=trainer.trainer_pk \
                             left join user on user.user_pk=trainer.user_fk where trainer_pk like %s order by date desc;", (searchterm2, searchterm2))
        search_trainer_id = connection.fetchall()

    else:
        search_trainer_id = False
    return render_template('/admin/result_class_trainers.html', search_trainer_Name=search_trainer_name, search_trainer_Id=search_trainer_id)


@app_admin.route('/admin/news', methods=['GET', 'POST'])
def news():
    user_id = request.cookies.get('user_id')
    message = ""
    if request.method == 'POST':
        news_title = request.form.get('news_title')
        news_content = request.form.get('news_content')
        if news_title != '' and news_content != '':
            if len(news_title) > 255 or len(news_content) > 255:
                message = "Sorry, the information you have entered is too long."
            else:
                connection = getCursor()
                connection.execute(
                    "INSERT INTO news (user_fk, create_date, title, content) VALUES(%s,CURDATE(),%s,%s);", (user_id, news_title, news_content,))
                message = "You have sent successfully."
        else:
            message = "Neither the news title nor the content can be empty."

    return render_template('/admin/news.html', message=message)


@app_admin.route('/admin/news_history', methods=['GET', 'POST'])
def news_history():
    connection = getCursor()
    connection.execute(
        "select news_pk,title,content,CONCAT(user.first_name,' ', user.last_name),create_date from news join user on news.user_fk = user.user_pk order by news_pk desc;")
    news_entries = connection.fetchall()
    return render_template('/admin/news_history.html', news_entries=news_entries)
# Generate financial report (Beibei)


@app_admin.route('/admin/financial_report', methods=['GET', 'POST'])
def financial_report():
    sort_by = 'sort_all'
    connection = getCursor()
    start_date = '1900-01-01'
    end_date = '2500-01-01'
    date_start_display = False
    date_end_display = False
    if request.method == 'POST':
        sort_by = request.form.get('options')
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        if len(start_date) == 0 and len(end_date) == 0:
            start_date = '1900-01-01'
            end_date = '2500-01-01'
            date_start_display = False
            date_end_display = False
        elif len(end_date) == 0:
            end_date = '2500-01-01'
            date_start_display = True
            date_end_display = False
        elif len(start_date) == 0:
            start_date = '1900-01-01'
            date_start_display = False
            date_end_display = True
        else:
            date_start_display = True
            date_end_display = True

    if sort_by == 'sort_all':
        connection.execute(
            "select payment_pk,amount,date,if(booking_fk IS NULL,'subscription','training') from payment where status=1 AND date between %s and %s order by date desc;", (start_date, end_date,))
    elif sort_by == 'sort_training':
        connection.execute(
            "select payment_pk,amount,date,if(booking_fk IS NULL,'subscription','training') from payment where booking_fk IS NOT NULL AND status=1 AND date between %s and %s order by date desc;", (start_date, end_date,))
    else:
        connection.execute(
            "select payment_pk,amount,date,if(booking_fk IS NULL,'subscription','training') from payment where booking_fk IS NULL AND status=1 AND date between %s and %s order by date desc;", (start_date, end_date,))

    financial_data = connection.fetchall()
    return render_template('/admin/financial_report.html', financial_data=financial_data, sort_by=sort_by, start_date=start_date, end_date=end_date, date_start_display=date_start_display, date_end_display=date_end_display)


@app_admin.route('/admin/popular_classes', methods=['GET', 'POST'])
def popular_classes():
    if request.method == "POST":
        if 'filterbydatebutton' in request.form:
            startdate = request.form["startdate"]
            enddate = request.form["enddate"]
                # If enddate is empty, set it the same as startdate.
            if len(enddate) == 0:
                enddate = startdate
                # Check if startdate is empty.
            if len(startdate) == 0:
                message = "Please choose a start date."
                return render_template('/admin/popular_classes.html', message=message)
          
            connection = getCursor()
            connection.execute("""SELECT row_number()over(order by COUNT(*) DESC )ranks,ec.name, COUNT(*) AS num_enrolled
                FROM exerciseclass ec
                JOIN booking b ON ec.exercise_class_pk = b.exercise_class_fk
                WHERE ec.date BETWEEN %s AND %s
                GROUP BY ec.name;""",(startdate, enddate, ))

        
            classlist = connection.fetchall()

            if len(classlist) > 0:
                if 'filterbydatebutton' in request.form:
                    message = "Popular Classes found"
                
            else:
                if 'filterbydatebutton' in request.form:
                    message = "This date range is not available for popular classes"
                

        return render_template('/admin/popular_classes.html', classlist=classlist, message=message)

    else:
        connection = getCursor()
        connection.execute('''SELECT row_number()over(order by COUNT(*) DESC )ranks, ec.name, COUNT(*) AS num_enrolled
                FROM exerciseclass ec
                JOIN booking b ON ec.exercise_class_pk = b.exercise_class_fk
                GROUP BY ec.name
                ORDER BY num_enrolled DESC;''')
        classlist = connection.fetchall()
        return render_template('/admin/popular_classes.html', classlist=classlist)

