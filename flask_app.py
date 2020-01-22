# TrainAndTest.py

import pymssql
import os
import random
import TrainAndTest as tr
from io import BytesIO
from flask import Flask, render_template, request, jsonify
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
import time

app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
# Enable CORS
CORS(app)


@app.route("/")
def addpic():
    return render_template('upload.html')


@app.route("/mis", methods=['POST', 'GET'])
def getmis():
    if request.method == 'GET':
        LotNO = request.args.get("LotNO", default="", type=str)
        conn = pymssql.connect(database='NSP', user='sa',
                               password='prim', host='192.168.10.2', port=1433)
        cursor = conn.cursor()
        sql = "SELECT PartNo, PartCode, StartQty FROM lot L INNER JOIN product P ON L.ProductID = P.ProductID WHERE LotNo = '{}';".format(
            LotNO)
        cursor.execute(sql)
        row = cursor.fetchone()
        Return = {}
        if row:
            Return["PartNO"] = row[0]
            Return["PartCode"] = row[1]
            Return["StartQty"] = row[2]
            Return["LotNO"] = LotNO
        else:
            Return["PartNO"] = None
            Return["PartCode"] = None
            Return["StartQty"] = None
            Return["LotNO"] = LotNO
        return jsonify(Return)
    elif request.method == 'POST':
        LotNO = request.form.get("LotNO", default="", type=str)
        conn = pymssql.connect(database='NSP', user='sa',
                               password='prim', host='192.168.10.2', port=1433)
        cursor = conn.cursor()
        sql = "SELECT PartNo, PartCode, StartQty FROM lot L INNER JOIN product P ON L.ProductID = P.ProductID WHERE LotNo = '{}';".format(
            LotNO)
        cursor.execute(sql)
        row = cursor.fetchone()
        Return = {}
        if row:
            Return["PartNO"] = row[0]
            Return["PartCode"] = row[1]
            Return["StartQty"] = row[2]
            Return["LotNO"] = LotNO
        else:
            Return["PartNO"] = None
            Return["PartCode"] = None
            Return["StartQty"] = None
            Return["LotNO"] = LotNO
        return jsonify(Return)
    else:
        return {'status': 'params error!'}


@app.route("/upload", methods=['POST'])
def upload():
    st = time.time()
    target = os.path.join(APP_ROOT, 'images/')
    # print(target)

    if not os.path.isdir(target):
        os.mkdir(target)

    for file in request.files.getlist("file"):
        # print(file)
        filename = file.filename
        filename = str(random.randint(1, 100)) + filename
        destination = target + filename
        file.save(destination)
        # return destination
        img_value = tr.recg(destination)
        # return "xxx"
        if img_value.count('.') <= 1:
            img_value = img_value
        else:
            img_value = None
            # img_value = "Please Try Again Later"

        et = time.time()
        seconds = et - st
        print("Seconds since epoch = {} s".format(seconds))
    return {'reading': img_value}


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port="8080")
