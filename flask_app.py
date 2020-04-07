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
        try:
            conn = pymssql.connect(database='NSP', user='sa',
                                   password='1qaz2wsx#', host='192.168.10.7', port=1433)
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
        database="qctest"
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
        PartNO = request.args.get("PartNO", default="", type=str)
        PartCode = request.args.get("PartCode", default="", type=str)
        Limit = request.args.get("Limit", default=0, type=int)
        Like = request.args.get("Like", default=0, type=int)
        Host, User, Pass = queryMisConfig()
        conn = pymssql.connect(database='NSP', user=User,
                               password=Pass, host=Host, port=1433)
        cursor = conn.cursor(as_dict=True)
        if(PartCode != ""):
            sql = "SELECT C.CustomerName, C.CustomerCode, "
            sql += "     P.PartNo, P.PartName, P.PartCode, "
            sql += "     L.CurrentQTY, L.IssueDate, "
            sql += "     M.MaterialCode, M.MaterialName, M.MaterialType "
            sql += "FROM customer C "
            sql += "INNER JOIN product P "
            sql += "     ON P.CustomerID=C.CustomerID "
            sql += "INNER JOIN lot L "
            sql += "     ON L.ProductID=P.ProductID "
            sql += "INNER JOIN material M "
            sql += "     ON M.MaterialID=L.MaterialID "
            sql += "WHERE P.PartCode='{}';".format(PartCode)
        elif(LotNO != "" and PartNO != ""):
            sql = "SELECT TOP {} PartCode, CurrentQty, IssueDate FROM lot L INNER JOIN product P ON L.ProductID = P.ProductID WHERE LotNO='{}' AND PartNO='{}' ORDER BY LotID DESC".format(
                LotNO, PartNO)
        elif(PartNO != ""):
            if Limit == 0:
                Limit = 100
            if Like != 0:
                sql = "SELECT TOP {} PartNo, LotNo, PartCode, CurrentQty, IssueDate FROM lot L INNER JOIN product P ON L.ProductID = P.ProductID WHERE PartNO LIKE '%{}%' ORDER BY LotID DESC".format(
                    Limit, PartNO)
            else:
                sql = "SELECT TOP {} LotNo, PartCode, CurrentQty, IssueDate FROM lot L INNER JOIN product P ON L.ProductID = P.ProductID WHERE PartNO='{}' ORDER BY LotID DESC".format(
                    Limit, PartNO)
        elif(LotNO != ""):
            sql = "SELECT C.CustomerName AS Customer, C.CustomerCode, "
            sql += "P.PartNo AS PartNumber, P.PartName, P.PartCode, "
            sql += "L.CurrentQty, L.IssueDate, L.LotNo, "
            sql += "M.MaterialName AS Material "
            sql += "FROM customer C "
            sql += "INNER JOIN product P "
            sql += "ON P.CustomerID=C.CustomerID "
            sql += "INNER JOIN lot L "
            sql += "ON L.ProductID=P.ProductID "
            sql += "INNER JOIN material M "
            sql += "ON M.MaterialID=L.MaterialID "
            sql += "WHERE L.LotNo='{}' ORDER BY L.LotID DESC".format(LotNO)
        else:
            if Limit == 0:
                Limit = 100
            sql = "SELECT TOP {} LotNo, PartNo, PartCode, CurrentQty, IssueDate FROM lot L INNER JOIN product P ON L.ProductID = P.ProductID ORDER BY LotID DESC".format(
                Limit)
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
