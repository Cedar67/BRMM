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
    # Return a list including the run id, course type, driver id, basic time, cones hit, WD status and the Run Totals.

    # Convert the dictionary data into a list that displays the required data fields
    update_list = []

    for listRun in runDetail:
        # Calculate WD time and make WD Value as Yes/No
        if listRun[10] == 1:
            wd_time = 10
        elif listRun[10] == 0:
            wd_time = 0
        elif listRun[10] == None:
            wd_time = 0
        else:
            print("\nerror: Invalid WD data\n")
            return -1
        # Get basic time
        if listRun[8] == None :
            time = 0
        elif type(listRun[8]) in (float,int) :
            time = listRun[8]
        else:
            print("\nerror: Invalid Time data\n")
            return -1
        # Make sure time is recorded to the nearest 0.01 of a second
        time = Decimal(time).quantize(Decimal("0.00"))

        # Get num of cones
        if listRun[9] == None:
            cones_time = 0
        elif type(listRun[9]) == int:
            cones_time = listRun[9]
        else:
            print("\nerror: Invalid Cones data\n")
            return -1
        # Calculate total time
        run_total = time + cones_time*5 + wd_time

        # Put into a list with the run id, course type, driver id, basic time, cones hit, WD status and the Run Totals.
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
                run_total)
        update_list.append(list(run))

    return update_list

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/listdrivers")
def listdrivers():
    connection = getCursor()
    sql = """   SELECT * FROM driver 
                INNER JOIN car 
                ON driver.car = car.car_num
                ORDER BY driver.surname, driver.first_name;"""

    connection.execute(sql)
    driverList = connection.fetchall()
    for list in driverList:
        print(list)
    return render_template("driverlist.html", driver_list = driverList)    

@app.route("/listcourses")
def listcourses():
    connection = getCursor()
    connection.execute("SELECT * FROM course;")
    courseList = connection.fetchall()
    return render_template("courselist.html", course_list = courseList)

@app.route("/graph")
def showgraph():
    connection = getCursor()
    # Insert code to get top 5 drivers overall, ordered by their final results.
    # Use that to construct 2 lists: bestDriverList containing the names, resultsList containing the final result values
    # Names should include their ID and a trailing space, eg '133 Oliver Ngatai '
    bestDriverList = {}
    resultsList = {}
    return render_template("top5graph.html", name_list = bestDriverList, value_list = resultsList)

@app.route("/rundetail", methods=['POST','GET'])
def rundetail():
    # Get driver id that user selects from rundetail.html
    driverId = request.form.get('driver')
    #If driverId can be converted to an integer, convert to integer, otherwise set to None.
    try:
        driverId=int(driverId)
    except:
        driverId=None
    # Get driver name list and order by first name
    connection = getCursor()
    sql=""" SELECT distinct driver.driver_id, driver.first_name, driver.surname
            FROM driver
            INNER JOIN car ON driver.car = car.car_num
            INNER JOIN run ON driver.driver_id = run.dr_id
            INNER JOIN course ON course.course_id = run.crs_id
            order by driver.first_name;"""
    connection.execute(sql)
    driverList = connection.fetchall()


    connection = getCursor()
    sql1 = """   SELECT driver.driver_id, driver.first_name, driver.surname, driver.age, 
                car.model, car.drive_class, course.name, 
                run.run_num, run.seconds, run.cones, run.wd
				FROM driver 
                INNER JOIN car ON driver.car = car.car_num
                INNER JOIN run ON driver.driver_id = run.dr_id
                INNER JOIN course ON course.course_id = run.crs_id"""
    
    if request.method == 'POST' and driverId is not None:
        sql2 = "where driver.driver_id = %s"
        parameters = (driverId,)
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
    
    return render_template("rundetail.html", run_detail = runDetailUpdate, driver_List = driverList)  

