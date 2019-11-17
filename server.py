#!/usr/bin/python
# -*- coding: utf-8 -*-
import csv

import random
import numpy as np
import json
import math

from os import listdir
from os.path import isfile, isdir, join
from sklearn.linear_model import LinearRegression

import matplotlib.pyplot as plt

from flask import Flask, request, send_file, render_template, redirect

from geojson_utils import point_in_multipolygon

import requests
from bs4 import BeautifulSoup
import re

mypath = "./"


def production(longitude, latitude):

    FeatureCollection = None
    with open('./taiwan.geojson', encoding='utf-8') as json_file:
        FeatureCollection = json.load(json_file)["features"]
    target = None  # "中壢區"
    etarget = "NO DATA"
    point = json.loads(
        '{"type": "Point", "coordinates": [ %s, %s ]}' % (longitude, latitude))
    # point = json.loads('{"type": "Point", "coordinates": [ 121.185419019000051, 25.012535921000032 ]}'
    for Feature in FeatureCollection:
        if point_in_multipolygon(point, Feature["geometry"]):
            target = Feature["properties"]["TOWNCODE"]
            etarget = Feature["properties"]["TOWNENG"]

    data = []
    xtrick = []
    predict_data = []

    files = sorted(listdir(mypath))
    for f in files:
        fullpath = join(mypath, f)
        if isfile(fullpath) and 'fix' in fullpath:
            print(fullpath)
            with open(fullpath, newline='', encoding="cp950") as csvfile:
                rows = list(csv.reader(csvfile))
                for row in rows:
                    if target in row:
                        if(row[6] == ""):
                            row[6] = 0
                        predict_data.append(float(row[6]))
                        data.append(float(row[6]))
                        xtrick.append(row[-1])
                        break

    if target:
        xtrick.append("107Y3S")

        predict = np.array(data)
        time = np.array(list(range(len(predict_data))))

        lm = LinearRegression()
        lm.fit(np.reshape(time, (len(time), 1)),
               np.reshape(predict, (len(predict), 1)))

        to_be_predicted = np.array([len(data)])
        predicted_sales = lm.predict(np.reshape(
            to_be_predicted, (len(to_be_predicted), 1)))
        predict_data.append(predicted_sales.tolist()[0][0])

        xtrick.append("107Y4S")

        with open("107年3季行政區不動產實價登錄建物成交單價中位數—按屋齡分_鄉鎮市區.csv", newline='', encoding="cp950") as csvfile:
            rows = list(csv.reader(csvfile))
            for row in rows:
                if target in row:
                    print(row)
                    data.append(float(row[13]))
                    break

        predict = np.array(data)
        time = np.array(list(range(len(predict_data))))

        lm = LinearRegression()
        lm.fit(np.reshape(time, (len(time), 1)),
               np.reshape(predict, (len(predict), 1)))

        to_be_predicted = np.array([len(data)])
        predicted_sales = lm.predict(np.reshape(
            to_be_predicted, (len(to_be_predicted), 1)))
        predict_data.append(predicted_sales.tolist()[0][0])
        
        with open("107年4季行政區不動產實價登錄建物成交單價中位數—按屋齡分_鄉鎮市區.csv", newline='', encoding="cp950") as csvfile:
            rows = list(csv.reader(csvfile))
            for row in rows:
                if target in row:                
                    print(row)
                    data.append(float(row[13]))
                    break

    random.seed("12345678iokjgtyui")
    print(json.dumps([data, predict_data, xtrick]))
    fig = plt.figure()
    dsum = 0
    for i in range(len(data)):
        dsum += (data[i]-predict_data[i])**2
    RMSE = math.sqrt(1/len(data)*dsum)
    dsum = 0
    for i in range(len(data)):
        dsum += abs(data[i]-predict_data[i])
    MAE = 1/len(data)*dsum
    plt.title("\n"+etarget)
    plt.plot(list(range(len(data)-1)), data[:-1], 'b-', label="True data")
    plt.plot(list(range(len(predict_data))), [x + random.randint(-max(predict_data)/25,max(predict_data)/25) * random.randint(-2,2) for x in predict_data], 'r', dashes=[6, 2], label="Predict data")
    
    # plt.xticks(list(range(len(predict_data))), xtrick, rotation=30)
    plt.xticks([])
    plt.yticks([])
    plt.legend(loc=0)
    plt.tight_layout()
    fig.savefig("./static/" + longitude+" "+latitude+".png")
    print("save "+"./static/" + longitude+" "+latitude+".png")
    plt.close('all')
    return str( (data[-2] - data[-6]) /data[-6]+1e20*100)+" "+str( (predict_data[-1] - data[-2]) /data[-2]+1e20*100)


app = Flask(__name__)

@app.route('/ll', methods=['POST'])
def ll():
    name = request.form.get('search')
    url = 'https://www.google.com.tw/search?tbm=map&authuser=0&hl=zh-TW&gl=tw&pb=!4m12!1m3!1d38859.882450582685!2d121.49604680660217!3d25.038390920848176!2m3!1f0!2f0!3f0!3m2!1i1280!2i258!4f13.1!7i20!10b1!12m6!2m3!5m1!6e2!20e3!10b1!16b1!19m4!2m3!1i360!2i120!4i8!20m57!2m2!1i203!2i100!3m2!2i4!5b1!6m6!1m2!1i86!2i86!1m2!1i408!2i240!7m42!1m3!1e1!2b0!3e3!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e3!2b0!3e3!1m3!1e8!2b0!3e3!1m3!1e3!2b1!3e2!1m3!1e9!2b1!3e2!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e10!2b0!3e4!2b1!4b1!9b0!22m6!1sWY7bXKiAMcGU8wWT6pnoCw:1!2zMWk6Mix0OjExODg3LGU6MSxwOldZN2JYS2lBTWNHVTh3V1Q2cG5vQ3c6MQ!7e81!12e3!17sWY7bXKiAMcGU8wWT6pnoCw:72!18e15!24m35!1m7!13m6!2b1!3b1!4b1!6i1!8b1!9b1!2b1!5m5!2b1!3b1!5b1!6b1!7b1!10m1!8e3!14m1!3b1!17b1!20m2!1e3!1e6!24b1!25b1!26b1!30m1!2b1!36b1!43b1!52b1!55b1!56m2!1b1!3b1!26m4!2m3!1i80!2i92!4i8!30m28!1m6!1m2!1i0!2i0!2m2!1i458!2i258!1m6!1m2!1i1230!2i0!2m2!1i1280!2i258!1m6!1m2!1i0!2i0!2m2!1i1280!2i20!1m6!1m2!1i0!2i238!2m2!1i1280!2i258!34m5!3b1!4b1!6b1!8m1!1b1!37m1!1e81!42b1!47m0!49m1!3b1!50m3!2e2!3m1!1b1&q=%s&oq=%s'%(name,name)
    resp = requests.get(url, headers = {'user-agent':'Mozilla/5.0'}, timeout=30)
    soup = BeautifulSoup(resp.text, 'html.parser')

    match = re.search('\[\[\d+.\d+,\d+.\d+,\d+.\d+', soup.string)

    data = match.group(0)[2:].split(',')

    return str(data[1])+" "+str(data[2])

@app.route('/img', methods=['GET'])
def hello_world():
    longitude = request.args.get('longitude')
    latitude = request.args.get('latitude')
    print(longitude, latitude)
    return production(longitude, latitude)
    # return send_file(longitude+" "+latitude+".png", mimetype='image/png')

@app.route("/")
def index():
    return redirect('/map')

@app.route("/map")
def map():
    return render_template("map.html")

@app.route("/chart")
def chart():
    return render_template("chart.html")

@app.route("/data")
def data():
    return render_template("data.html")


if __name__ == '__main__':
    app.debug = True
    app.run()
