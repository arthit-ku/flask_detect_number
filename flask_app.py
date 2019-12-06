# TrainAndTest.py

import os
import random
import TrainAndTest as tr
from io import BytesIO
from flask import Flask, render_template, request, jsonify
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
import time

app = Flask(__name__)
APP_ROOT=os.path.dirname(os.path.abspath(__file__))
# Enable CORS
CORS(app)


@app.route("/")
def addpic():
    return render_template('upload.html')

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
        filename = str(random.randint(1,100))+filename
        destination = target+filename
        file.save(destination)
        #return destination
        img_value = tr.recg(destination)
        #return "xxx"
        if img_value.count('.') <= 1:
            img_value = img_value
        else:
            img_value = None
            #img_value = "Please Try Again Later"

        et = time.time()
        seconds = et-st
        print("Seconds since epoch = {} s".format(seconds))
    return {'reading':img_value} 

if __name__ == "__main__":
    app.run(host="0.0.0.0",port = "8080",debug=True)
