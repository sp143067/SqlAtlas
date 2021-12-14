import os
from pathlib import Path
from flask import Flask, render_template, request, Response, redirect, session, send_file, make_response
import pandas as pd
from pandas_profiling import ProfileReport
import matplotlib.pyplot as myplot
import seaborn as mysns
mysns.set_style("darkgrid")
import pyodbc


# Reading the data from a .csv file and creating a DataFrame
us_hosuing_df = pd.read_csv("USA_Housing.csv").head(100)
# us_hosuing_df.info()
us_hosuing_df.rename(columns={"Avg. Area Income": "Avg_Area_Income", "Avg. Area House Age": "Avg_Area_House_Age",
                              "Avg. Area Number of Rooms": "Avg_Area_Number_of_Rooms",
                              "Avg. Area Number of Bedrooms": "Avg_Area_Number_of_Bedrooms",
                              "Area Population": "Area_Population"}, inplace=True)


az_sql_server = 'sxpatlas.database.windows.net'
az_sql_database = 'atlas_db'
az_sql_username = 'sxpadmin'
az_sql_password = 'sada1234'
az_sql_driver = '{ODBC Driver 17 for SQL Server}'
az_sql_table = 'usa_housing'

# https://docs.sqlalchemy.org/en/14/core/engines.html#microsoft-sql-server
# az_sql_connection = 'mssql+pyodbc://{username}:{password}@{server}:1433/{database}?driver={driver}'.format(
#     username=az_sql_username, password=az_sql_password, server=az_sql_server, database=az_sql_database,
#     driver=az_sql_driver.replace(' ', '+'))



# Reference: Constructing a Azure SQL DB connection pipeline
# https://docs.microsoft.com/en-us/azure/azure-sql/database/connect-query-python

########## Creating the usa_housing table  #############
az_sql_connection = pyodbc.connect(
    'DRIVER='+az_sql_driver + ';SERVER=' + az_sql_server + ';DATABASE=' + az_sql_database + ';UID=' + az_sql_username + ';PWD=' + az_sql_password)

print('Creating the usa_housing table....')
# Create table query
create_sql = ( "if not exists (select * from sysobjects where name='usa_housing' and xtype='U')"
    "CREATE TABLE usa_housing ( Avg_Area_Income FLOAT NOT NULL, Avg_Area_House_Age FLOAT NOT NULL,"
    "Avg_Area_Number_of_Rooms FLOAT NOT NULL, Avg_Area_Number_of_Bedrooms FLOAT NOT NULL, Area_Population FLOAT NOT NULL,"
    "Price FLOAT NOT NULL,Address VARCHAR(200))"
)
create_cursor = az_sql_connection.cursor()
create_cursor.execute(create_sql)
create_cursor.commit()
print('table created successfully!')
########################################################

####  Ingest the Dataframe into the created "usa_housing" table on the "sqlatlas" database:
insert_cursor = az_sql_connection.cursor()
print('Starting the Data Ingestion process........')
# Insert Dataframe into SQL Server:
for index, row in us_hosuing_df.iterrows():
    insert_cursor.execute("INSERT INTO usa_housing (Avg_Area_Income, Avg_Area_House_Age, Avg_Area_Number_of_Rooms, Avg_Area_Number_of_Bedrooms, Area_Population, Price, Address) values(?,?,?,?,?,?,?)",
                   row.Avg_Area_Income, row.Avg_Area_House_Age, row.Avg_Area_Number_of_Rooms, row.Avg_Area_Number_of_Bedrooms, row.Area_Population, row.Price, row.Address)
insert_cursor.commit()

print('Data ingestion has completed successfully!')
############################################################################################


# Read the data from Azure SQL DB/Table into Panda's DataFrame
select_sql = 'SELECT * FROM [dbo].[usa_housing]'
sql_to_df = pd.read_sql(select_sql,az_sql_connection)
#print(sql_to_df.head())
#az_sql_connection.close()



# Check for already backed-up 'qda.html' file is exist or not,
# if not, then create one!
qda_file = Path("templates/qda.html")
if not qda_file.is_file():
    print('Report html is not present!, Creating One....')
    usa_housing_profile = ProfileReport(sql_to_df, title="Data Analysis Report",
                                        explorative=True)  # explorative=True
    usa_housing_profile.to_file('templates/qda.html')

app = Flask(__name__)
app.secret_key= os.urandom(28)
#mail = Mail(app)


# LogIn/Home Page
@app.route('/')
def home():
    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/login')
def login():
    if 'user_id' in session:
        return render_template('index.html')
    else:
        return redirect('/')


@app.route('/home')
def homeLogin():
    if 'user_id' in session:
        return render_template('index.html')
    else:
        return redirect('/')


@app.route('/AboutMe')
def aboutme():
    return render_template('AboutMe.html')


@app.route('/index')
def index():
    if 'user_id' in session:
        return render_template('index.html')
    else:
        return redirect('/')

########## Creating the "usertable" table  #############
#localConn = mysql.connector.connect(host='localhost', port=3306, user='root', password='Think@987', database='userdb')
userCursor = az_sql_connection.cursor()
# localCursor.execute("""SELECT * FROM usertable where name = '{}' AND password = '{}'""".format('sp1430', 'sp@1430'))
# print(localCursor.fetchall())
# localConn.close()
user_create_sql = ( "if not exists (select * from sysobjects where name='usertable' and xtype='U')"
        "create table usertable("
       "user_count INT NOT NULL IDENTITY(1, 1),"
       "name VARCHAR(100) NOT NULL,"
       "emailid VARCHAR(100) NOT NULL,"
       "password VARCHAR(100) NOT NULL);"
)
usercreate_cursor = az_sql_connection.cursor()
usercreate_cursor.execute(user_create_sql)
usercreate_cursor.commit()
print('usertable created successfully!')


@app.route('/validate_credentials', methods=['POST'])
def validate_credentials():
    email = request.form.get('email')
    password = request.form.get('password')
    valQuery = "SELECT * FROM usertable WHERE emailid='{}' AND password='{}'".format(email, password)
    userCursor.execute(valQuery)
    userlist = userCursor.fetchall()

    nameQuery = "SELECT name FROM usertable WHERE emailid='{}'".format(email)
    userCursor.execute(nameQuery)
    namelist = userCursor.fetchall()
    print(namelist[0][0])
    if len(userlist) > 0:
        session['user_id'] = userlist[0][0]
        session['user_name'] = namelist[0][0]
        return redirect('/index')
    else:
        return redirect('/login')


@app.route('/register_credentials', methods=['POST'])
def register_credentials():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    insQuery = "INSERT INTO usertable (name, emailid, password) VALUES ('{}', '{}', '{}')".format(name, email, password)
    userCursor.execute(insQuery)
    userCursor.commit()

    valQuery = "SELECT * FROM usertable WHERE emailid='{}'".format(email)
    userCursor.execute(valQuery)
    selectRow = userCursor.fetchall()
    #print(selectRow)
    session['user_id'] = selectRow[0][0]
    session['user_name'] = selectRow[0][1]
    return redirect('/index')


@app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect('/')


# To render the dataframe in tabular format on the website
@app.route('/dataframe', methods=("POST", "GET"))
def GK():
    if 'user_id' in session:
        return render_template('pandas.html',
                               PageTitle="dataframe",
                               table=[us_hosuing_df.to_html(classes='data', index=False, header=True)],
                               titles=us_hosuing_df.columns.values)
    else:
        return redirect('/')


# To render the quick data analysis report on the created dataframe
@app.route('/quick_data_analysis', methods=("POST", "GET"))
def quick_data_analysis():
    if 'user_id' in session:
        return render_template('qda.html')
    else:
        return redirect('/')


@app.route('/describe', methods=("POST", "GET"))
def describe():
    describe_data = us_hosuing_df.describe()
    #print(describe_data)
    return describe_data.to_html()



@app.route('/pair_plot', methods=("POST", "GET"))
def pair_plot():
    mysns.pairplot(us_hosuing_df)
    myplot.savefig('images/pairplot.png')
    return send_file('images/pairplot.png', mimetype='image/png')
    #return Response("<img src='images/pairplot.png'>")


if __name__ == '__main__':
    app.run()  # debug=True, port=5003  # To run the APPLICATION in DEBUG mode
