# Bankside Rakaia Motorkhana Mavens

<br>

## Product Background & Requirements
**[Please click here to view.](/PRD%20-%20WebApp%20-%20Motorkhana.pdf)**

<br>

## Templates Introduction

| Template  | Purpose | User |
| ------------- |-------------|:-------------:|
| base.html      |Basic template HTML for drivers   |All|
| home.html      |Homepage for all users and entrance for administrator    |All|
| courselist.html      |Course list |All|
| driverlist.html      |Driver list     |All|
| rundetail.html      |Run detail   |All|
| overall.html      |Overall list   |All|
| top5graph.html      |Bar graph for top 5 overall  |All|
| admin.html      |Basic template HTML for admin    |Administrator|
| adminhome.html      |Homepage for admin   |Administrator|
| driversearch.html      |Driver search     |Administrator|
| juniorlist.html      |Junior driver list  |Administrator|
| runedit.html      |Edit run   |Administrator|
| driveradd.html      |Add driver - Step 1 - Enter basic information (driver name and car)  and select driver type |Administrator|
| driveraddnonjunior.html      |Add driver - Step 2 -  Submit the add operation for driver aged above 25      |Administrator|
| driveraddbirthday.html      |Add driver - Step 2 - Enter birthday and submit the add operation for driver aged 16-25  |Administrator|
| driveraddunder16.html      |Add driver - Step 2 - Enter birthday, caregiver and submit the add operation for driver aged 12-16   |Administrator|

<br>

## Relationship - Between Routes and Templates


| Route | Function Name  | From Template     | Return Type   | Return Destination   | Methods   | Arguments |
| -------------|-------------|-------------|------------|-------------|:-------------:|--------|
| / |home() |root   | render_template  |    home.html   |GET    |   |
| /admin    |admin()    |basic template | render_template  |    admin.html  |GET    |   |
| /adminhome    |adminhome()    |home.html  | render_template  |    adminhome.html  |GET    |   |
| /base |base() |basic template | render_template  |    base.html   |GET    |   |
| /listdrivers  |listdrivers()  |home.html  | render_template  |    listdrivers.html    |GET    |   |
| /listcourses  |listcourses()  |home.html  | render_template  |    courselist.html |GET    |   |
| /graph    |showgraph()    |home.html  | render_template  |    top5graph.html  |GET    |   |
| /rundetail    |rundetail()    |home.html  | render_template  |    rundetail.html  |GET    |   |
|   |   |rundetail.html | render_template  |    rundetail.html  |POST   |driver id  |
|   |   |listdrivers.html   | render_template  |    rundetail.html  |GET    |driver id  |
| /overall  |overall()  |home.html  | render_template  |    overall.html    |GET    |   |
| /listjuniordrivers    |listjunior()   |adminhome.html | render_template  |    listjuniordrivers.html  |GET    |   |
| /runedit  |runedit()  |adminhome.html | render_template  |    runedit.html    |GET    |   |
|   |   |runedit.html   | render_template  |    runedit.html    |POST   |driver id  |
|   |   |runedit.html   | render_template  |    runedit.html    |POST   |course id  |
| /runedit/update   |runeditupdate()    |runedit.html   | redirect route  | /runedit    |POST   |driver id<br>course id<br>run num<br>time<br>cones<br>wd   |
| /driveradd    |driveradd()    |adminhome.html | render_template  |    driveradd.html  |GET    |   |
|   |   |driveraddnonjunior.html    | render_template  |    driveradd.html  |GET    |   |
|   |   |driveraddbirthday.html | render_template  |    driveradd.html  |GET    |   |
|   |   |driveraddunder16.html  | render_template  |    driveradd.html  |GET    |   |
| /driveraddnext    |driveraddnext()    |driveradd.html | render_template  |    driveraddbirthday.html<br>driveraddnonjunior.html<br>driveraddunder16.html  |POST   |driver name<br>car<br>driver age type  |
| /driveraddnonjunior   |driveraddnonjunior()   |driveraddnonjunior.html    | redirect route  | /searchdriverfilter |POST   |driver name<br>car |
| /driveraddjunior  |driveraddjunior()  |driveraddbirthday.html | redirect route  | /searchdriverfilter |POST   |driver name<br>car<br>birthday |
| /driveraddunder16 |driveraddunder16() |driveraddunder16.html  | redirect route  | /searchdriverfilter |POST   |driver name<br>car<br>birthday<br>caregiver    |
| /searchdriver |searchdriver() |adminhome.html | render_template  |    driversearch.html   |GET    |   |
| /searchdriver/filter  |searchdriverfilter()   |driversearch.html  | render_template  |    driversearch.html   |POST   |driver id  |
|   |   |driveraddnonjunior.html    | render_template  |    driversearch.html   |GET    |driver name<br>driver id   |
|   |   |driveraddbirthday.html | render_template  |    driversearch.html   |GET    |driver name<br>driver id   |
|   |   |driveraddunder16.html  | render_template  |    driversearch.html   |GET    |driver name<br>driver id   |

<br>

## Functions

| Function Name  | Input Arguments   | Return Type   | Return Content   |
|-------------|-------------|-------------|-------------|
|getCursor  |user, password, host, port, dbname |MYSQLcursor    |Access to MySQL    |
|ageCalculate   |date(yyyy-mm-dd)    |Dictionary |age, birthday  |
|runsCalculate  |runDetail list without run total   |List   |runDetail include run total    |
|overallCalculate   |runDetail include run total    |List   |Overall and prize result   |

<br>

## Assumptions

* __*Overall results page - Display all 6 course times for each driver.*__

>
>When I saw this description in this requirements document, I encountered confusion. 
What I am not clear about is whether it is necessary to display each run of each Course. 
If displayed all run nums, then the table will have too many columns, which may affect the user experience. 
If NOT displayed all run nums, it may not meet the user's requirements for content integrity. 
>
>So I thought clarifying and confirming this demand point with the demander (teachers) was necessary. 
My approach was to draw a sketch of the two solutions and ask the demander to choose which one. 
The answer is that only the best Run total of each Course needs to be displayed. 
>
>I read the requirements document carefully again. 
In fact, at the top of the document, there is a description of Course Time that it’s the best Run Total ever.
>
>Through this experience, I understand that demand clarification is very important. 
And thinking about how to express demand clarification can help everyone efficiently.


## Design Decisions

__1. Colour scheme__

>The overall colour scheme is considered to be royalblue and black. 
>
>Royalblue is a mild and calm colour, easy to be accepted by most people. 
And it is also my favourite colour. 
So royalblue is used as the colour of the title, navigation bar and buttons. 
>
>The table data is more serious content, so black is more appropriate. 
It also creates a colour contrast.


__2. Use different basic HTML templates for driver and administrator users.__
>
>The driver user base template is base.html. All driver user pages are extended from it.
The administrator user base template is admin.html. All admin user pages are extended from it.
The link between admin and driver users is placed in home.html in the root path.
>
>The reason for this design is, it can reduce the difficulty of designing template inheritance. 
It also makes the routes and templates clearer and simpler. 
>
>In addition, if there are more user roles overlap, it may be necessary to consider more meaningful inheritance of the template design.


__3. When adding drivers, different age types are distinguished by different templates.__

>Adding a driver is done in two steps.
>
>The step-1 is to enter the basic information, including driver name and car selection. 
This information is necessary for all drivers. 
In this step, the age type of the driver is selected, so that it can be used in the step-2 with different templates.
>
>The step-2 has three branches, depending on the age type selected in the first step, three different templates will be displayed. 
>
>The reason for this design is that it is logically clear.
It also matchs two of the requirements: Not use JavaScript technology; Displays the age and caregiver inputs as needed.

<br>

## Database Questions

__1. What SQL statement creates the car table and defines its three fields/columns?__
```
CREATE TABLE IF NOT EXISTS car
(
car_num INT PRIMARY KEY NOT NULL,
model VARCHAR(20) NOT NULL,
drive_class VARCHAR(3) NOT NULL
);
```
__2. Which line of SQL code sets up the relationship between the car and driver tables?__
```
FOREIGN KEY (car) REFERENCES car(car_num)
```
__3. Which 3 lines of SQL code insert the Mini and GR Yaris details into the car table?__
```
INSERT INTO car VALUES
(11,'Mini','FWD'),
(17,'GR Yaris','4WD')
```
__4. Set a default value of ‘RWD’ for the driver_class field.__
```
CREATE TABLE IF NOT EXISTS car
(
drive_class VARCHAR(3) NOT NULL  DEFAULT 'RWD'
);
```
__5. Why is it important for drivers and the club admin to access different routes? As part of your answer, give two specific examples__

>On the one hand, for reasons of personal privacy. 
By distinguishing between different routes, it is possible to protect personal information from being accessed by the public. 
Some sensitive personal information should not be disclosed without permission. 
For example, driver's birthday and age are private information. 
If we don't differentiate between routes, any driver can access another driver's birthday, which is not reasonable. 
When routes are distinguished, only administrators can access this private information. 
This is a better way to protect user privacy.
>
>On the other hand, distinguishing between different routes protects data security. 
Results data is very important information. 
These data should not be altered arbitrarily, otherwise the validity and authenticity of the competition will be affected. 
For example, if a normal user has access to the Edit Run page, there is no guarantee that the data will not be altered. 
When routes are distinguished, only authorised administrators can modify these critical data according to their specific needs. 
This provides better data security.

<br>

## Project Schedule
**[Please click here to view.](https://docs.google.com/spreadsheets/d/1ru8RfZqSTfCWRcV7RW6NCX90a4ZVW_8HXqwLZyoBPUg/edit?usp=sharing)**


## Job Log 
**[Please click here to view.](https://docs.google.com/spreadsheets/d/1ru8RfZqSTfCWRcV7RW6NCX90a4ZVW_8HXqwLZyoBPUg/edit#gid=1914338260)**

## Q & A
**[Please click here to view.](https://docs.google.com/spreadsheets/d/1ru8RfZqSTfCWRcV7RW6NCX90a4ZVW_8HXqwLZyoBPUg/edit#gid=485308682)**

<br>
