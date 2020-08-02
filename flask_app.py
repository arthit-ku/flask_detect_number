import pymssql
import os
import json
import mysql.connector
from io import BytesIO
from flask import Flask, render_template, request, jsonify, make_response
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS

import time

app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
# Enable CORS
CORS(app)


@app.route("/")
def addpic():
    return {'error': 'true', 'message': 'params error!'}


@app.route("/machine", methods=['POST', 'GET'])
def getMachine():
    if(request.method == 'GET'):
        Limit = request.args.get("Limit", default=0, type=int)
        Host, User, Pass = queryMisConfig()
        try:
            conn = pymssql.connect(database='NSP', user=User,
                                   password=Pass, host=Host, port=1433)
        except Exception:
            return {'error': 'true', 'message': 'connect db error!'}
        cursor = conn.cursor(as_dict=True)
        if(Limit == 0):
            Limit = 100
        sql = "SELECT TOP {} MachineID, MachineNo, ModelName, Brand FROM machine ORDER BY MachineID ASC".format(
            Limit)
        cursor.execute(sql)
        ReturnArray = []
        for row in cursor:
            Return = {}
            Return = row
            ReturnArray.append(Return)
        return make_response(json.dumps(ReturnArray, ensure_ascii=True, indent=4, sort_keys=True))
    elif(request.method == 'POST'):
        return {'error': 'true', 'message': 'method not used error!'}
    else:
        return {'error': 'true', 'message': 'params error!'}


def queryMisConfig():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="qctest123",
        database="qc_test4"
    )
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT IpAddress, DbUsername, DbPassword FROM mis_config ORDER BY MisConfigID DESC LIMIT 0,1")
    myresult = mycursor.fetchone()
    return myresult[0], myresult[1], myresult[2]


@app.route("/mis", methods=['POST', 'GET'])
def getmis():
    if request.method == 'GET':
        LotNO = request.args.get("LotNO", default="", type=str)
        LocationID = request.args.get("LocationID", default=1,type=str)
        Host, User, Pass = queryMisConfig()
        try:
            conn = pymssql.connect(database='NSP', user=User,
                                   password=Pass, host=Host, port=1433)
        except Exception:
            return {'error': 'true', 'message': 'connect db error!'}

        cursor = conn.cursor(as_dict=True)
        sql = "SELECT L.*,P.PartCode FROM Lot_Travel L  INNER JOIN product P ON L.ProductID=P.ProductID"
        if LocationID=="1":
            sql += " WHERE L.LotNo='{}' AND (L.ProcessID=36 OR L.ProcessID=503) ORDER BY LotID DESC".format(LotNO)
        elif LocationID=="2":
            sql += " WHERE L.LotNo='{}' AND (L.ProcessID=35 OR L.ProcessID=505) ORDER BY LotID DESC".format(LotNO)
        elif LocationID=="3":
            sql += " WHERE L.LotNo='{}' AND L.ProcessID=75 ORDER BY LotID DESC".format(LotNO)
        elif LocationID=="4":
            sql += " WHERE L.LotNo='{}' AND L.ProcessID=422 ORDER BY LotID DESC".format(LotNO)
        cursor.execute(sql)
        ReturnArray = []
        for row in cursor:
            Return = {}
            Return = row
            ReturnArray.append(Return)
        return make_response(json.dumps(ReturnArray, indent=4, sort_keys=True, default=str))
    elif request.method == 'POST':
        return {'error': 'true', 'message': 'method not used for here!'}
    else:
        return {'error': 'true', 'message': 'params error!'}

# @app.route("/upload", methods=['POST'])
# def upload():
#     st = time.time()
#     target = os.path.join(APP_ROOT, 'images/')
#     # print(target)

#     if not os.path.isdir(target):
#         os.mkdir(target)

#     for file in request.files.getlist("file"):
#         # print(file)
#         filename = file.filename
#         filename = str(random.randint(1, 100)) + filename
#         destination = target + filename
#         file.save(destination)
#         # return destination
#         img_value = tr.recg(destination)
#         # return "xxx"
#         if img_value.count('.') <= 1:
#             img_value = img_value
#         else:
#             img_value = None
#             # img_value = "Please Try Again Later"

#         et = time.time()
#         seconds = et - st
#         print("Seconds since epoch = {} s".format(seconds))
#     return {'reading': img_value}


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port="8080")
