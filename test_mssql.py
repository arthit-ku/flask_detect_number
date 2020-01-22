import pymssql
LotNO = "29120610J16B"

server = "192.168.10.10"
user = "sa"
password = "prim"
dbname = "NSP"
conn = pymssql.connect(database='NSP', user='sa',
                       password='prim', host='192.168.10.2', port=1433)
cursor = conn.cursor()
sql = "SELECT PartNo, PartCode, StartQty FROM lot L INNER JOIN product P ON L.ProductID = P.ProductID WHERE LotNo = '{}' ;".format(
    LotNO)
cursor.execute(sql)
row = cursor.fetchone()
Return = {}
Return["PartNo"] = row[0]
Return["PartCode"] = row[1]
Return["SampleQty"] = row[2]
Return["LotNO"] = LotNO
print(Return)
