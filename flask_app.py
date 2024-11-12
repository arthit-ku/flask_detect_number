import pymssql
import os
import json
import mysql.connector
from io import BytesIO
from flask import Flask, render_template, request, jsonify, make_response
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
import datetime
import datetime

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


@app.route("/mis_sync_product", methods=['POST','GET'])
def sync_product():
    if request.method == 'GET':

        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="qctest123",
            database="tool_store_db"
        )
        mycursor = mydb.cursor()
        mycursor.execute("SELECT IFNULL(MAX(id),0) FROM products")
        myresult = mycursor.fetchone()
        id = myresult[0]
        sql = "SELECT * FROM product WHERE ProductID>"+ str(id)
        Host, User, Pass = queryMisConfig()
        try:
            conn = pymssql.connect(database='NSP', user=User, password=Pass, host=Host, port=1433)
        except Exception:
            return {'error': 'true', 'message': 'connect db error!'}

        cursor = conn.cursor(as_dict=True)
        cursor.execute(sql)
        
        ReturnArray = []
        for row in cursor:
            sql="INSERT INTO `products`(`id`, `part_no`, `part_name`, `part_code`, `customer_id`, `is_delete`, `created_at`, `created_user_id`, `updated_at`, `updated_user_id`)"
            sql+=" VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            val=(row['ProductID'],row["PartNo"],row["PartName"],row["PartCode"],row["CustomerID"],'N',
                datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1,datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1)
            mycursor.execute(sql,val)
            mydb.commit()
            ReturnArray = []
            Return = row
            ReturnArray.append(Return)
        return make_response(json.dumps(ReturnArray, indent=4, sort_keys=True, default=str))
    elif request.method == 'POST':
        return {'error': 'true', 'message': 'method not used for here!'}
    else:
        return {'error': 'true', 'message': 'params error!'}

@app.route("/mis_sync_spare_part", methods=['POST','GET'])
def sync_spare_part():
    if request.method == 'GET':

        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="qctest123",
            database="tool_store_db"
        )
        mycursor = mydb.cursor()
        mycursor.execute("SELECT IFNULL(MAX(id),0) FROM spare_parts")
        myresult = mycursor.fetchone()
        id = myresult[0]
        sql = "SELECT * FROM spare_parts WHERE CategoryID IN (5,6,8,9,14) AND SparePartID >"+ str(id)
        Host, User, Pass = queryMisConfig()
        try:
            conn = pymssql.connect(database='NSP', user=User, password=Pass, host=Host, port=1433)
        except Exception:
            return {'error': 'true', 'message': 'connect db error!'}

        cursor = conn.cursor(as_dict=True)
        cursor.execute(sql)
        ReturnArray = []
        for row in cursor:
            sql="INSERT INTO `spare_parts`(`id`, `spare_part_name`, `spare_part_code`, `category_id`, `image_url`, `is_delete`, `created_at`, `created_user_id`, `updated_at`, `updated_user_id`)"
            sql+=" VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            val=(row["SparePartID"],row["SparePartName"],row["SparePartCode"],row["CategoryID"],'','N',
                datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1,datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1)
            mycursor.execute(sql,val)
            sql="INSERT INTO `spare_part_stores`(`spare_part_id`,`store_id`,`balance_qty`,`created_at`, `created_user_id`, `updated_at`,`updated_user_id`)"
            sql+=" VALUES (%s,%s,%s,%s,%s,%s,%s)"
            val=(row["SparePartID"],'1','0',datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1,datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1)
            mycursor.execute(sql,val)
            sql="INSERT INTO `spare_part_stores`(`spare_part_id`,`store_id`,`balance_qty`,`created_at`, `created_user_id`, `updated_at`,`updated_user_id`)"
            sql+=" VALUES (%s,%s,%s,%s,%s,%s,%s)"
            val=(row["SparePartID"],'2','0',datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1,datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1)
            mycursor.execute(sql,val)
            
            sql="INSERT INTO `regrind_spare_stores`(`spare_part_id`,`regrind_store_id`,`balance_qty`,`created_at`, `created_user_id`, `updated_at`,`updated_user_id`)"
            sql+=" VALUES (%s,%s,%s,%s,%s,%s,%s)"
            val=(row["SparePartID"],'1','0',datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1,datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1)
            mycursor.execute(sql,val)
            sql="INSERT INTO `regrind_spare_stores`(`spare_part_id`,`regrind_store_id`,`balance_qty`,`created_at`, `created_user_id`, `updated_at`,`updated_user_id`)"
            sql+=" VALUES (%s,%s,%s,%s,%s,%s,%s)"
            val=(row["SparePartID"],'2','0',datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1,datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1)
            mycursor.execute(sql,val)

            mydb.commit()
            ReturnArray = []
            Return = row
            ReturnArray.append(Return)
        return make_response(json.dumps(ReturnArray, indent=4, sort_keys=True, default=str))
    elif request.method == 'POST':
        return {'error': 'true', 'message': 'method not used for here!'}
    else:
        return {'error': 'true', 'message': 'params error!'}

@app.route("/mis_sync_customer", methods=['POST','GET'])
def sync_customer():
    if request.method == 'GET':

        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="qctest123",
            database="tool_store_db"
        )
        mycursor = mydb.cursor()
        mycursor.execute("SELECT IFNULL(MAX(id),0) FROM customers")
        myresult = mycursor.fetchone()
        id = myresult[0]
        sql = "SELECT * FROM customer WHERE CustomerID >"+ str(id)
        Host, User, Pass = queryMisConfig()
        try:
            conn = pymssql.connect(database='NSP', user=User, password=Pass, host=Host, port=1433)
        except Exception:
            return {'error': 'true', 'message': 'connect db error!'}

        cursor = conn.cursor(as_dict=True)
        cursor.execute(sql)
        ReturnArray = []
        for row in cursor:
            sql="INSERT INTO `customers`(`id`, `customer_code`, `customer_name`, `is_delete`, `created_at`, `created_user_id`, `updated_at`, `updated_user_id`)"
            sql+=" VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
            val=(row["CustomerID"],row["CustomerCode"],row["CustomerName"],'N',
                datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1,datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1)
            mycursor.execute(sql,val)
            mydb.commit()
            ReturnArray = []
            Return = row
            ReturnArray.append(Return)
        return make_response(json.dumps(ReturnArray, indent=4, sort_keys=True, default=str))
    elif request.method == 'POST':
        return {'error': 'true', 'message': 'method not used for here!'}
    else:
        return {'error': 'true', 'message': 'params error!'}

@app.route("/mis_sync_machine", methods=['POST','GET'])
def sync_machine():
    if request.method == 'GET':

        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="qctest123",
            database="tool_store_db"
        )
        mycursor = mydb.cursor()
        mycursor.execute("SELECT IFNULL(MAX(id),0) FROM machines")
        myresult = mycursor.fetchone()
        id = myresult[0]
        sql = "SELECT * FROM machine WHERE MachineID >"+ str(id)
        Host, User, Pass = queryMisConfig()
        try:
            conn = pymssql.connect(database='NSP', user=User, password=Pass, host=Host, port=1433)
        except Exception:
            return {'error': 'true', 'message': 'connect db error!'}

        cursor = conn.cursor(as_dict=True)
        cursor.execute(sql)
        ReturnArray = []
        for row in cursor:
            sql="INSERT INTO `machines`(`id`, `machine_no`, `machine_name`, `model_id`, `is_delete`, `created_at`, `created_user_id`, `updated_at`, `updated_user_id`)"
            sql+=" VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            val=(row["MachineID"],row["MachineNo"],row["MachineNo"],1,'N',
                datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1,datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1)
            mycursor.execute(sql,val)
            mydb.commit()
            ReturnArray = []
            Return = row
            ReturnArray.append(Return)
        return make_response(json.dumps(ReturnArray, indent=4, sort_keys=True, default=str))
    elif request.method == 'POST':
        return {'error': 'true', 'message': 'method not used for here!'}
    else:
        return {'error': 'true', 'message': 'params error!'}

@app.route("/mis_sync_vendor", methods=['POST','GET'])
def sync_vendor():
    if request.method == 'GET':

        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="qctest123",
            database="tool_store_db"
        )
        mycursor = mydb.cursor()
        mycursor.execute("SELECT IFNULL(MAX(id),0) FROM vendors")
        myresult = mycursor.fetchone()
        id = myresult[0]
        sql = "SELECT * FROM vendor WHERE VendorID >"+ str(id)
        Host, User, Pass = queryMisConfig()
        try:
            conn = pymssql.connect(database='NSP', user=User, password=Pass, host=Host, port=1433)
        except Exception:
            return {'error': 'true', 'message': 'connect db error!'}

        cursor = conn.cursor(as_dict=True)
        cursor.execute(sql)
        ReturnArray = []
        for row in cursor:
            sql="INSERT INTO `vendors`(`id`, `vendor_code`, `vendor_name`, `is_delete`, `created_at`, `created_user_id`, `updated_at`, `updated_user_id`)"
            sql+=" VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
            val=(row["VendorID"],row["VendorCode"],row["VendorName"],'N',
                datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1,datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1)
            mycursor.execute(sql,val)
            mydb.commit()
            ReturnArray = []
            Return = row
            ReturnArray.append(Return)
        return make_response(json.dumps(ReturnArray, indent=4, sort_keys=True, default=str))
    elif request.method == 'POST':
        return {'error': 'true', 'message': 'method not used for here!'}
    else:
        return {'error': 'true', 'message': 'params error!'}

@app.route("/mis_sync_process", methods=['POST','GET'])
def sync_process():
    if request.method == 'GET':

        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="qctest123",
            database="tool_store_db"
        )
        mycursor = mydb.cursor()
        mycursor.execute("SELECT IFNULL(MAX(id),0) FROM processes")
        myresult = mycursor.fetchone()
        id = myresult[0]
        sql = "SELECT * FROM process WHERE ProcessID >"+ str(id)
        Host, User, Pass = queryMisConfig()
        try:
            conn = pymssql.connect(database='NSP', user=User, password=Pass, host=Host, port=1433)
        except Exception:
            return {'error': 'true', 'message': 'connect db error!'}

        cursor = conn.cursor(as_dict=True)
        cursor.execute(sql)
        ReturnArray = []
        for row in cursor:
            sql="INSERT INTO `processes`(`id`, `process_name`,`spec`, `shop`, `is_delete`, `created_at`, `created_user_id`, `updated_at`, `updated_user_id`)"
            sql+=" VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            val=(row["ProcessID"],row["ProcessName"],row["Spec"],row["Shop"],'N',
                datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1,datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1)
            mycursor.execute(sql,val)
            mydb.commit()
            ReturnArray = []
            Return = row
            ReturnArray.append(Return)
        return make_response(json.dumps(ReturnArray, indent=4, sort_keys=True, default=str))
    elif request.method == 'POST':
        return {'error': 'true', 'message': 'method not used for here!'}
    else:
        return {'error': 'true', 'message': 'params error!'}

@app.route("/mis_sync_product_process", methods=['POST','GET'])
def sync_product_process():
    if request.method == 'GET':
        product_id = request.args.get('product_id')
        process_type = request.args.get('process_type')
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="qctest123",
            database="tool_store_db"
        )
        mycursor = mydb.cursor()
        mycursor.execute("UPDATE product_processes SET is_delete='Y',updated_at=NOW() WHERE product_id="+product_id+" AND process_type="+process_type)
        mydb.commit()
        sql = "SELECT PP.*,P.Spec FROM product_process PP INNER JOIN process P ON PP.ProcessID=P.ProcessID WHERE PP.ProductID="+product_id+" AND PP.ProcessType="+process_type+" ORDER BY SeqNo"
        Host, User, Pass = queryMisConfig()
        try:
            conn = pymssql.connect(database='NSP', user=User, password=Pass, host=Host, port=1433)
        except Exception:
            return {'error': 'true', 'message': 'connect db error!'}

        cursor = conn.cursor(as_dict=True)
        cursor.execute(sql)
        ReturnArray = []
        sql="INSERT INTO `product_processes`(`product_id`, `process_id`,`process_type`,`seq_no`,`spec`,`on_pocket`,`master_cost`,`last_cost`, `is_delete`, `created_at`, `created_user_id`, `updated_at`, `updated_user_id`)"
        sql+=" VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        val=(product_id,1,process_type,0,'','N','0.00','0.00','N',
            datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1,
            datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1)
        mycursor.execute(sql,val)
        mydb.commit()
        
        ReturnArray = []
        i=1
        for row in cursor:
            sql="INSERT INTO `product_processes`(`product_id`, `process_id`,`process_type`,`seq_no`,`spec`,`on_pocket`,`master_cost`,`last_cost`, `is_delete`, `created_at`, `created_user_id`, `updated_at`, `updated_user_id`)"
            sql+=" VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            val=(row["ProductID"],row["ProcessID"],row["ProcessType"],row["SeqNo"],row["Spec"],row["OnPocket"],'0.00','0.00','N',
                datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1,datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1)
            mycursor.execute(sql,val)
            mydb.commit()
            Return = row
            ReturnArray.append(Return)
            i=i+1
        sql="INSERT INTO `product_processes`(`product_id`, `process_id`,`process_type`,`seq_no`,`spec`,`on_pocket`,`master_cost`,`last_cost`, `is_delete`, `created_at`, `created_user_id`, `updated_at`, `updated_user_id`)"
        sql+=" VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        val=(product_id,2,process_type,i,'','N','0.00','0.00','N',
            datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1,datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1)
        mycursor.execute(sql,val)
        mydb.commit()

        return make_response(json.dumps(ReturnArray, indent=4, sort_keys=True, default=str))
    elif request.method == 'POST':
        return {'error': 'true', 'message': 'method not used for here!'}
    else:
        return {'error': 'true', 'message': 'params error!'}

@app.route("/mis_sync_spare_receive", methods=['POST','GET'])
def sync_spare_receive():
    if request.method == 'GET':

        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="qctest123",
            database="tool_store_db"
        )
        mycursor = mydb.cursor()
        mycursor.execute("SELECT IFNULL(MAX(id),44918) FROM spare_receives")
        myresult = mycursor.fetchone()
        id = myresult[0]
        sql = "SELECT * FROM spare_receives WHERE SpareReceiveID >"+ str(id)
        Host, User, Pass = queryMisConfig()
        try:
            conn = pymssql.connect(database='NSP', user=User, password=Pass, host=Host, port=1433)
        except Exception:
            return {'error': 'true', 'message': 'connect db error!'}

        cursor = conn.cursor(as_dict=True)
        cursor.execute(sql)
        ReturnArray = []
        for row in cursor:
            sql="INSERT INTO `spare_receives`(`id`, `vendor_id`, `inv_no`, `receive_date`,`currency`, `created_at`, `created_user_id`, `updated_at`, `updated_user_id`)"
            sql+=" VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            val=(row["SpareReceiveID"],row["VendorID"],row["InvNo"],row["ReceiveDate"].date().isoformat(),row["Currency"],
                datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1,datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1)
            mycursor.execute(sql,val)
            mydb.commit()
            ReturnArray = []
            Return = row
            ReturnArray.append(Return)
        return make_response(json.dumps(ReturnArray, indent=4, sort_keys=True, default=str))
    elif request.method == 'POST':
        return {'error': 'true', 'message': 'method not used for here!'}
    else:
        return {'error': 'true', 'message': 'params error!'}

@app.route("/mis_sync_spare_receive_detail", methods=['POST','GET'])
def sync_spare_receive_detail():
    if request.method == 'GET':

        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="qctest123",
            database="tool_store_db"
        )
        mycursor = mydb.cursor()
        mycursor.execute("SELECT IFNULL(MAX(id),108585) FROM spare_receive_details")
        myresult = mycursor.fetchone()
        id = myresult[0]
        sql = "SELECT * FROM spare_receive_details WHERE SpareReceiveDetailID >"+ str(id)
        Host, User, Pass = queryMisConfig()
        try:
            conn = pymssql.connect(database='NSP', user=User, password=Pass, host=Host, port=1433)
        except Exception:
            return {'error': 'true', 'message': 'connect db error!'}

        cursor = conn.cursor(as_dict=True)
        cursor.execute(sql)
        ReturnArray = []
        for row in cursor:
            sql="INSERT INTO `spare_receive_details`(`id`, `spare_receive_id`, `spare_part_id`, `spare_qty`, `thb_price`, `created_at`, `created_user_id`, `updated_at`, `updated_user_id`)"
            sql+=" VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            val=(row["SpareReceiveDetailID"],row["SpareReceiveID"],row["SparePartID"],row["SpareQty"],row["THBPrice"],
                datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1,datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1)
            mycursor.execute(sql,val)
            mydb.commit()
            sql="INSERT INTO `spare_part_qty_logs`(`spare_part_id`,`store_id`, `operation_type`, `update_qty`, `ref_id`, `created_at`, `created_user_id`, `updated_at`, `updated_user_id`)"
            sql+=" VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            val=(row["SparePartID"],'1','RECV',row["SpareQty"],row["SpareReceiveDetailID"],datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1,
                datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1)
            mycursor.execute(sql,val)
            sql="UPDATE `spare_part_stores` SET `balance_qty`=`balance_qty` + " + str(row["SpareQty"])+" WHERE `spare_part_id`=" + str(row["SparePartID"])+" AND `store_id`='1'"
            mycursor.execute(sql)
            sql="UPDATE `spare_parts` SET `last_price`=" + str(row["THBPrice"]) + " WHERE `id`=" + str(row["SparePartID"])
            mycursor.execute(sql)
            mydb.commit()
            ReturnArray = []
            Return = row
            ReturnArray.append(Return)
        return make_response(json.dumps(ReturnArray, indent=4, sort_keys=True, default=str))
    elif request.method == 'POST':
        return {'error': 'true', 'message': 'method not used for here!'}
    else:
        return {'error': 'true', 'message': 'params error!'}

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
            return {'error': 'true', 'message': 'connect db error!:'}

        cursor = conn.cursor(as_dict=True)
        sql = "SELECT L.*,P.PartCode,P.PartNo AS PartNumber,P.PartName,C.CustomerName AS Customer,M.MaterialName AS Material"
        sql += " FROM Lot_Travel L"
        sql += " INNER JOIN product P ON L.ProductID=P.ProductID"
        sql += " INNER JOIN customer C ON P.CustomerID=C.CustomerID"
        sql += " INNER JOIN material M ON L.MaterialID=M.MaterialID"
        if LocationID=="1":
            sql += " WHERE L.LotNo='{}' AND L.ProcessID=36 ORDER BY LotID DESC".format(LotNO)
        elif LocationID=="2":
            sql += " WHERE L.LotNo='{}' AND L.ProcessID=35 ORDER BY LotID DESC".format(LotNO)
        elif LocationID=="3":
            sql += " WHERE L.LotNo='{}' AND L.ProcessID=75 ORDER BY LotID DESC".format(LotNO)
        elif LocationID=="4":
            sql += " WHERE L.LotNo='{}' AND L.ProcessID=422 ORDER BY LotID DESC".format(LotNO)
        elif LocationID=="5":
            sql += " WHERE L.LotNo='{}' AND L.ProcessID=422 ORDER BY LotID DESC".format(LotNO)
        elif LocationID=="7":
            sql += " WHERE L.LotNo='{}' AND L.ProcessID=505 ORDER BY LotID DESC".format(LotNO)
        elif LocationID=="8":
            sql += " WHERE L.LotNo='{}' AND L.ProcessID=503 ORDER BY LotID DESC".format(LotNO)
        elif LocationID=="9":
            sql += " WHERE L.LotNo='{}' AND L.ProcessID=626 ORDER BY LotID DESC".format(LotNO)
        elif LocationID=="10":
            sql += " WHERE L.LotNo='{}' AND L.ProcessID=615 ORDER BY LotID DESC".format(LotNO)
        elif LocationID=="11":
            sql += " WHERE L.LotNo='{}' AND L.ProcessID=614 ORDER BY LotID DESC".format(LotNO)
        elif LocationID=="12":
            sql += " WHERE L.LotNo='{}' AND L.ProcessID=617 ORDER BY LotID DESC".format(LotNO)
        elif LocationID=="13":
            sql += " WHERE L.LotNo='{}' AND L.ProcessID=616 ORDER BY LotID DESC".format(LotNO)
        elif LocationID=="14":
            sql += " WHERE L.LotNo='{}' AND L.ProcessID=646 ORDER BY LotID DESC".format(LotNO)
        else:
            sql += " WHERE L.LotNo='{}' AND L.ProcessID=0 ORDER BY LotID DESC".format(LotNO)
        ReturnArray = []
        cursor.execute(sql)
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

@app.route("/mis_sync_spare_part_mt", methods=['POST','GET'])
def sync_spare_part_mt():
    if request.method == 'GET':

        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="qctest123",
            database="tool_store_db"
        )
        mycursor = mydb.cursor()
        mycursor.execute("SELECT IFNULL(MAX(id),0) FROM spare_parts")
        myresult = mycursor.fetchone()
        id = myresult[0]
        sql = "SELECT * FROM spare_parts WHERE CategoryID IN (5,9) AND SparePartID NOT IN (744,8007,13721,16941,24523)"
        Host, User, Pass = queryMisConfig()
        try:
            conn = pymssql.connect(database='NSP', user=User, password=Pass, host=Host, port=1433)
        except Exception:
            return {'error': 'true', 'message': 'connect db error!'}

        cursor = conn.cursor(as_dict=True)
        cursor.execute(sql)
        ReturnArray = []
        for row in cursor:
            sql="INSERT INTO `spare_parts`(`id`, `spare_part_name`, `spare_part_code`, `category_id`, `image_url`, `is_delete`, `created_at`, `created_user_id`, `updated_at`, `updated_user_id`)"
            sql+=" VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            val=(row["SparePartID"],row["SparePartName"],row["SparePartCode"],row["CategoryID"],'','N',
                datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1,datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1)
            mycursor.execute(sql,val)
            sql="INSERT INTO `spare_part_stores`(`spare_part_id`,`store_id`,`balance_qty`,`created_at`, `created_user_id`, `updated_at`,`updated_user_id`)"
            sql+=" VALUES (%s,%s,%s,%s,%s,%s,%s)"
            val=(row["SparePartID"],'1','0',datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1,datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1)
            mycursor.execute(sql,val)
            sql="INSERT INTO `spare_part_stores`(`spare_part_id`,`store_id`,`balance_qty`,`created_at`, `created_user_id`, `updated_at`,`updated_user_id`)"
            sql+=" VALUES (%s,%s,%s,%s,%s,%s,%s)"
            val=(row["SparePartID"],'2','0',datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1,datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1)
            mycursor.execute(sql,val)
            
            sql="INSERT INTO `regrind_spare_stores`(`spare_part_id`,`regrind_store_id`,`balance_qty`,`created_at`, `created_user_id`, `updated_at`,`updated_user_id`)"
            sql+=" VALUES (%s,%s,%s,%s,%s,%s,%s)"
            val=(row["SparePartID"],'1','0',datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1,datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1)
            mycursor.execute(sql,val)
            sql="INSERT INTO `regrind_spare_stores`(`spare_part_id`,`regrind_store_id`,`balance_qty`,`created_at`, `created_user_id`, `updated_at`,`updated_user_id`)"
            sql+=" VALUES (%s,%s,%s,%s,%s,%s,%s)"
            val=(row["SparePartID"],'2','0',datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1,datetime.datetime.now().replace(microsecond=0).isoformat().replace("T"," "),1)
            mycursor.execute(sql,val)

            mydb.commit()
            ReturnArray = []
            Return = row
            ReturnArray.append(Return)
        return make_response(json.dumps(ReturnArray, indent=4, sort_keys=True, default=str))
    elif request.method == 'POST':
        return {'error': 'true', 'message': 'method not used for here!'}
    else:
        return {'error': 'true', 'message': 'params error!'}

if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port="8080")
