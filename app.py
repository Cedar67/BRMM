from decimal import Decimal
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
import re
from datetime import datetime
import mysql.connector
from mysql.connector import FieldType
import connect

app = Flask(__name__)

dbconn = None
connection = None

def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost, \
    database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn



def runsCalculate(runDetail):
    # Calculate the Run Totals
    # Return a list including the course type, driver id, time, cones hit, WD status and the Run Totals.

    # Define the list include Run totals
    update_list = []

    for listRun in runDetail:
        # Calculate WD time
        if listRun[11] == 1:
            wd_time = 10
        elif listRun[11] == 0:
            wd_time = 0
        elif listRun[11] == None:
            wd_time = 0
        else:
            print("\nerror: Invalid WD data\n")
            return -1
        # Get time
        if listRun[9] == None :
            time = 0
        elif type(listRun[9]) in (float,int) :
            time = listRun[9]
        else:
            print("\nerror: Invalid Time data\n")
            return -1
        # Make sure time is recorded to the nearest 0.01 of a second
        time = Decimal(time).quantize(Decimal("0.00"))

        # Get num of cones
        if listRun[10] == None:
            cones_time = 0
        elif type(listRun[10]) == int:
            cones_time = listRun[10]
        else:
            print("\nerror: Invalid Cones data\n")
            return -1
        # Calculate total time
        run_total = time + cones_time*5 + wd_time

        # Put into a list with the course type, driver id, basic time, cones hit, WD status and the Run Totals.
        run = (
                listRun[0],
                listRun[1],
                listRun[2],
                listRun[3],
                listRun[4],
                listRun[5],
                listRun[6],
                listRun[7],
                listRun[8],
                listRun[9],
                listRun[10],
                listRun[11],
                run_total)
        update_list.append(list(run))

    return update_list



def overallCalculate(runDetail):
    # Calculate the Overall Results and add it into return list

    # Sort Run Details list
    # Sort rule: first by surname, then by firstname, then by Course ID, then by Run Total.
    sort_list = sorted(runDetail, key=lambda x:(x[2],x[1],x[6],x[12]))

    # Put all courses results of one driver into one list
    temp_list = []
    j = 0
    while j<len(sort_list):
        list = []
        for i in range(0, 6):
            list.append(sort_list[j][i])

        for i in range(1, 13):
            list.append(sort_list[j][12])
            j=j+1
        temp_list.append(list)


    # Calculate the overall result
    overall_list = []
    for list in temp_list:
        list2 = []
        overallResult = 0.0
        for i in range(0, 6):
            list2.append(list[i])
        # Choose the best of two run results for each course
        for i in range(6, 18, 2):
            if list[i+1] == 0.0:
                list2.append(0.0)
                overallResult = 999999  # overallResult Value 999999 means NQ
            elif list[i] == 0.0:
                list2.append(list[i+1])
            else:
                list2.append(min(list[i],list[i+1]))
        
        # Calculate the overall result
        if overallResult != 999999:
            for i in range(6, 12):
                overallResult = Decimal(overallResult).quantize(Decimal("0.00"))
                overallResult = list2[i] + overallResult
        
        list2.append(overallResult)

        overall_list.append(list2)

    # Sort Overall Results list
    # Sort rule: first by Overall Results, then by surname, then by firstname.
    overall_list = sorted(overall_list, key=lambda x:(x[12],x[2],x[1]))
    
    # Winner get "cup" flag, the next 4 get "prize" flag
    resultsNum = len(overall_list)
    if resultsNum > 4:
        overall_list[0].append("cup")
        for i in range(1, 5):
            overall_list[i].append("prize")
    elif resultsNum == 1:
        overall_list[0].append("cup")
    elif resultsNum < 5:
        overall_list[0].append("cup")
        for i in range(1, resultsNum):
            overall_list[i].append("prize")

    return overall_list



@app.route("/")
def home():
    return render_template("home.html")



@app.route("/admin")
def admin():
    return render_template("admin.html")



@app.route("/base")
def base():
    return render_template("base.html")



@app.route("/listdrivers")
def listdrivers():
    connection = getCursor()
    sql = """   SELECT * FROM driver 
                INNER JOIN car ON driver.car = car.car_num
                ORDER BY driver.surname, driver.first_name;"""

    connection.execute(sql)
    driverList = connection.fetchall()
    for list in driverList:
        print(list)
    return render_template("driverlist.html", driver_list = driverList)    



@app.route("/listjuniordrivers")
def listjunior():
    connection = getCursor()
    sql = """   SELECT d1.driver_id, d1.first_name, d1.surname, d1.age, 
                car.model, car.drive_class, d2.first_name, d2.surname FROM driver d1  
                INNER JOIN car ON d1.car = car.car_num
                LEFT JOIN driver d2 ON d1.caregiver = d2.driver_id
                ORDER BY d1.age DESC, d1.surname;"""

    connection.execute(sql)
    driverList = connection.fetchall()
    for list in driverList:
        print(list)
    return render_template("juniorlist.html", driver_list = driverList)    



@app.route("/listcourses")
def listcourses():
    connection = getCursor()
    connection.execute("SELECT * FROM course;")
    courseList = connection.fetchall()
    return render_template("courselist.html", course_list = courseList)



@app.route("/graph")
def showgraph():

    connection = getCursor()
    sql = """  SELECT driver.driver_id, driver.first_name, driver.surname, driver.age, 
                car.model, car.drive_class, run.crs_id, course.name, 
                run.run_num, run.seconds, run.cones, run.wd
				FROM driver 
                INNER JOIN car ON driver.car = car.car_num
                INNER JOIN run ON driver.driver_id = run.dr_id
                INNER JOIN course ON course.course_id = run.crs_id
                ORDER BY run.crs_id;"""
    connection.execute(sql)
    runDetail = connection.fetchall()
    
    # Calculate the Run Total
    runDetailUpdate = runsCalculate(runDetail)
    
    # Calculate the Overall Result
    overallResults = overallCalculate(runDetailUpdate)
    # Insert code to get top 5 drivers overall, ordered by their final results.
    # Use that to construct 2 lists: bestDriverList containing the names, resultsList containing the final result values
    # Names should include their ID and a trailing space, eg '133 Oliver Ngatai '
    # bestDriverList = {1,2}
    resultsList = {3,40}
    bestDriverList = {'apple ','mango ','banana ','pear ','test '}
    return render_template("top5graph.html", name_list = bestDriverList, value_list = resultsList)



@app.route("/rundetail", methods=['POST','GET'])
def rundetail():
    # Get driver name list and order by first name
    connection = getCursor()
    sql=""" SELECT distinct driver.driver_id, driver.first_name, driver.surname
            FROM driver
            INNER JOIN car ON driver.car = car.car_num
            INNER JOIN run ON driver.driver_id = run.dr_id
            INNER JOIN course ON course.course_id = run.crs_id
            order by driver.surname;"""
    connection.execute(sql)
    driverList = connection.fetchall()

    connection = getCursor()
    sql1 = """  SELECT driver.driver_id, driver.first_name, driver.surname, driver.age, 
                car.model, car.drive_class, run.crs_id, course.name, 
                run.run_num, run.seconds, run.cones, run.wd
				FROM driver 
                INNER JOIN car ON driver.car = car.car_num
                INNER JOIN run ON driver.driver_id = run.dr_id
                INNER JOIN course ON course.course_id = run.crs_id"""
    
    if request.method == 'POST':
        # Get driver id that user selects from rundetail.html
        driverId = request.form.get('driver')
    elif request.method == 'GET':
        # Get driver id that user clicks from driverlist.html
        driverId = request.args.get('driverid')

    #If driverId can be converted to an integer, convert to integer, otherwise set to None.
    try:
        driverId=int(driverId)
    except:
        driverId=None

    defaulDriver = None
    # if request.method == 'POST' and driverId is not None:
    if driverId is not None:
        sql2 = "where driver.driver_id = %s"
        parameters = (driverId,)
        defaulDriver = driverId
    else:
        sql2 = ""
        parameters = ()

    # Order by course id
    sql3 = "ORDER BY run.crs_id;"""

    # Combine all of the SQL parts into one SQL string. 
    # SQL2 will be "" if no value passed. 
    # Spaces avoid errors if no space between the strings.
    sql = sql1 + ' ' + sql2 + ' ' +sql3
    connection.execute(sql, parameters)
    runDetail = connection.fetchall()
    
    # Calculate the Run Total
    runDetailUpdate = runsCalculate(runDetail)
    
    # Debug print
    for list in runDetailUpdate:
        print(list)
    
    return render_template("rundetail.html", run_detail = runDetailUpdate, driver_List = driverList, defaul_driver = defaulDriver)  



@app.route("/overall", methods=['GET'])
def overall():
    # Get driver name list and order by first name
    connection = getCursor()
    sql=""" SELECT distinct driver.driver_id, driver.first_name, driver.surname
            FROM driver
            INNER JOIN car ON driver.car = car.car_num
            INNER JOIN run ON driver.driver_id = run.dr_id
            INNER JOIN course ON course.course_id = run.crs_id
            order by driver.surname;"""
    connection.execute(sql)
    driverList = connection.fetchall()

    connection = getCursor()
    sql1 = """  SELECT driver.driver_id, driver.first_name, driver.surname, driver.age, 
                car.model, car.drive_class, run.crs_id, course.name, 
                run.run_num, run.seconds, run.cones, run.wd
				FROM driver 
                INNER JOIN car ON driver.car = car.car_num
                INNER JOIN run ON driver.driver_id = run.dr_id
                INNER JOIN course ON course.course_id = run.crs_id"""
    
    if request.method == 'POST':
        # Get driver id that user selects from rundetail.html
        driverId = request.form.get('driver')
    elif request.method == 'GET':
        # Get driver id that user clicks from driverlist.html
        driverId = request.args.get('driverid')

    #If driverId can be converted to an integer, convert to integer, otherwise set to None.
    try:
        driverId=int(driverId)
    except:
        driverId=None

    defaulDriver = None
    # if request.method == 'POST' and driverId is not None:
    if driverId is not None:
        sql2 = "where driver.driver_id = %s"
        parameters = (driverId,)
        defaulDriver = driverId
    else:
        sql2 = ""
        parameters = ()

    # Order by course id
    sql3 = "ORDER BY run.crs_id;"""

    # Combine all of the SQL parts into one SQL string. 
    # SQL2 will be "" if no value passed. 
    # Spaces avoid errors if no space between the strings.
    sql = sql1 + ' ' + sql2 + ' ' +sql3
    connection.execute(sql, parameters)
    runDetail = connection.fetchall()
    
    # Calculate the Run Total
    runDetailUpdate = runsCalculate(runDetail)
    
    # Calculate the Overall Result
    overallResults = overallCalculate(runDetailUpdate)

    # Debug print
    for list in overallResults:
        print(list)
    
    return render_template("overall.html", run_detail = overallResults, driver_List = driverList, defaul_driver = defaulDriver)  



@app.route("/runedit", methods=['POST','GET'])
def runedit():
    # Get driver name list and order by first name
    connection = getCursor()
    sql=""" SELECT distinct driver.driver_id, driver.first_name, driver.surname
            FROM driver
            INNER JOIN car ON driver.car = car.car_num
            INNER JOIN run ON driver.driver_id = run.dr_id
            INNER JOIN course ON course.course_id = run.crs_id
            order by driver.surname;"""
    connection.execute(sql)
    driverList = connection.fetchall()

    # Get course list and order by course id
    connection = getCursor()
    sql=""" SELECT * FROM course order by course.course_id;"""
    connection.execute(sql)
    courseList = connection.fetchall()


    connection = getCursor()
    sql1 = """  SELECT driver.driver_id, driver.first_name, driver.surname, driver.age, 
                car.model, car.drive_class, course.name, 
                run.run_num, run.seconds, run.cones, run.wd
				FROM driver 
                INNER JOIN car ON driver.car = car.car_num
                INNER JOIN run ON driver.driver_id = run.dr_id
                INNER JOIN course ON course.course_id = run.crs_id"""
    
    # Get driver id that user selects from runedit.html
    driverId = request.form.get('driver')
    # Get course id that user selects from runedit.html
    courseId = request.form.get('course')

    #If driverId can be converted to an integer, convert to integer, otherwise set to None.
    try:
        driverId=int(driverId)
    except:
        driverId=None

    #If courseId is not None and course id, then convert it to None.
    if courseId is not None:
        if len(courseId)>1:
            courseId=None

    defaulDriver = None
    defaulCourse = None
    
    if driverId is not None:
        sql2 = "where driver.driver_id = %s"
        parameters = (driverId,)
        defaulDriver = driverId
    elif courseId is not None:
        sql2 = "where course.course_id = %s"
        parameters = (courseId,)
        defaulCourse = courseId
    else:
        sql2 = ""
        parameters = ()

    # Order by course id
    sql3 = "ORDER BY run.crs_id, driver.surname;"""

    # Combine all of the SQL parts into one SQL string. 
    # SQL2 will be "" if no value passed. 
    # Spaces avoid errors if no space between the strings.
    sql = sql1 + ' ' + sql2 + ' ' +sql3
    connection.execute(sql, parameters)
    runDetail = connection.fetchall()
    
    # Calculate the Run Total
    runDetailUpdate = runsCalculate(runDetail)
    
    # Debug print
    for list in runDetailUpdate:
        print(list)
    for list in courseList:
        print(list)
    
    return render_template("runedit.html", run_detail = runDetailUpdate, driver_List = driverList, course_List = courseList, defaul_driver = defaulDriver, defaul_course = defaulCourse)  



@app.route("/driveradd")
def driveradd():
    return render_template("driveradd.html")



@app.route("/searchdriver")
def searchdriver():
    connection = getCursor()
    sql = """   SELECT d1.driver_id, d1.first_name, d1.surname, d1.age, 
                car.model, car.drive_class, d2.first_name, d2.surname FROM driver d1  
                INNER JOIN car ON d1.car = car.car_num
                LEFT JOIN driver d2 ON d1.caregiver = d2.driver_id
                ORDER BY d1.surname;"""

    connection.execute(sql)
    driverList = connection.fetchall()
    for list in driverList:
        print(list)

    return render_template("driversearch.html", driver_list = driverList)



@app.route("/searchdriver/filter", methods=["POST"])
def searchdriverfilter():
    driverName = request.form.get('driver')
    connection = getCursor()
    sql = """   SELECT d1.driver_id, d1.first_name, d1.surname, d1.age, 
                car.model, car.drive_class, d2.first_name, d2.surname FROM driver d1  
                INNER JOIN car ON d1.car = car.car_num
                LEFT JOIN driver d2 ON d1.caregiver = d2.driver_id    
                WHERE d1.first_name like %s OR d1.surname like %s
                ORDER BY d1.surname, d1.first_name;"""
    parameters = (f'%{driverName}%',f'%{driverName}%',)
    connection.execute(sql,parameters)
    driverList = connection.fetchall()
    for list in driverList:
        print(list)
        
    return render_template("driversearch.html", driver_list = driverList)  
