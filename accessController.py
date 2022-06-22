import mysql.connector
from mysql.connector import Error

import pusher

import time
import datetime
import multiprocessing as mp

import os
from dotenv import load_dotenv

load_dotenv()

def FetchData(q, connection):

    mycursor = connection.cursor()

    mycursor.execute("SELECT * FROM users")
    
    data =  mycursor.fetchall()
    q.put(data)
    
    print("\nupdated")

def FetchProsses(q, connection):
    while 1:
        FetchData(q, connection)
        time.sleep(9000)

def HandleAccessGranted(user):

    cursor = connection.cursor()

    currenttime = str(datetime.datetime.now())

    query = """
    INSERT INTO accessed (access_time, user) VALUES (%s,%s)
    """

    queryData = (currenttime, user[0])

    cursor.execute(query, queryData)
    connection.commit()
    cursor.close()

    pusher_client = pusher.Pusher(
        app_id=os.getenv("APP_ID"),
        key=os.getenv("KEY"),
        secret=os.getenv("SECRET"),
        cluster='eu',
        ssl=True
    )

    pusher_client.trigger('update_channel', 'Acces_update', {'message': user})

def CheckAccess(accessToken, data):

    for x in data:
        if  accessToken == x[3] and x[1]:
            access_granted = 1
            user = x
            break

    if access_granted:
        HandleAccessGranted(user)
    else: 
        print("access denied")


if __name__ == "__main__":

    try:
        connection = mysql.connector.connect(host= os.getenv("DB_HOST"),
                                            database= os.getenv("DB"),
                                            user= os.getenv("DB_USER"),
                                            password= os.getenv("DB_PASSWORD"))
        if not connection.is_connected():
            print("not able to connect")
            exit()
        
    except Error as e:
        print("Error while connecting to MySQL", e)
        exit()

    access_granted = 0
    debug = ""

    q = mp.Queue()
    fetchDataProcess = mp.Process(target= FetchProsses, args=(q, connection))
    fetchDataProcess.start()

    while 1:
        debug = input("type a command: ")

        data = q.get()

        if debug == "c":

            accessToken = input("input your access token: ")
            CheckAccess(accessToken, data)

            debug = ''
        elif debug == "u":
            FetchData(q, connection)
            debug = ''
        elif debug == "q":
            fetchDataProcess.terminate()
            connection.close()
            exit()
        else:
            print("not a valid command")
