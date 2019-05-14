#!/usr/bin/python
# -*- coding: utf-8 -*-
import csv

import numpy as np
import json

from os import listdir
from os.path import isfile, isdir, join
from sklearn.linear_model import Ridge

import matplotlib.pyplot as plt

from flask import Flask, request, send_file

from geojson_utils import point_in_multipolygon

mypath = "./"

files = listdir(mypath)

def production(longitude,latitude):

    FeatureCollection = None
    with open('./taiwan.geojson', encoding='utf-8') as json_file:
        FeatureCollection = json.load(json_file)["features"]
    target = None # "中壢區"
    etarget = None
    point = json.loads('{"type": "Point", "coordinates": [ %s, %s ]}'%(longitude,latitude))
    # point = json.loads('{"type": "Point", "coordinates": [ 121.185419019000051, 25.012535921000032 ]}'
    for Feature in FeatureCollection:
        if point_in_multipolygon(point, Feature["geometry"]):
            target = Feature["properties"]["TOWNNAME"]
            etarget = Feature["properties"]["TOWNENG"]            

    data = []
    xtrick = []
    predict_data = []

    for f in files:
        fullpath = join(mypath, f)
        if isfile(fullpath) and 'fix' in fullpath:
            with open(fullpath, newline='', encoding="utf-8") as csvfile:
                rows = list(csv.reader(csvfile))
                for row in rows:
                    if target in row:
                        predict_data.append(float(row[6]))
                        data.append(float(row[6]))
                        xtrick.append(row[-1])

    if target:
        xtrick.append("107Y3S")

        predict = np.array(predict_data)
        time = np.array(list(range(len(predict_data))))

        lm = Ridge(alpha = .5)
        lm.fit(np.reshape(time, (len(time), 1)), np.reshape(predict, (len(predict), 1)))

        to_be_predicted = np.array([len(data)])
        predicted_sales = lm.predict(np.reshape(to_be_predicted, (len(to_be_predicted), 1)))
        predict_data.append(predicted_sales.tolist()[0][0])

        with open("107年3季行政區不動產實價登錄建物成交單價中位數—按屋齡分_鄉鎮市區.csv", newline='', encoding="cp950") as csvfile:
            rows = list(csv.reader(csvfile))
            for row in rows:
                if target in row:    
                    print(row)                
                    data.append(float(row[13]))

    print(json.dumps([data,predict_data,xtrick]))
    fig = plt.figure()
    plt.title(etarget)
    plt.plot(list(range(len(data))),data,'b-',label="True data")
    plt.plot(list(range(len(predict_data))),[x+50000 for x in predict_data],'r',dashes=[6, 2],label="Predict data")
    plt.xticks(list(range(len(data))),xtrick, rotation=30)
    plt.legend(loc=4)
    fig.savefig(longitude+" "+latitude+".png")

app = Flask(__name__)
 
@app.route('/', methods=['POST'])
def hello_world():
    longitude = request.args.get('longitude')
    latitude = request.args.get('latitude')
    production(longitude, latitude)
    return send_file(longitude+" "+latitude+".png", mimetype='image/png')

if __name__ == '__main__':
    app.debug = True
    app.run() 
    