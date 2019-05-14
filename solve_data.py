import csv

import numpy as np
import json

from os import listdir
from os.path import isfile, isdir, join
from sklearn.linear_model import Ridge

import matplotlib.pyplot as plt

from geojson_utils import point_in_multipolygon

mypath = "D:\\fake data"

files = listdir(mypath)

for f in files:
    fullpath = join(mypath, f)
    if isfile(fullpath) and 'fix' not in fullpath and '.py' not in fullpath and '.png' not in fullpath and '.geojson' not in fullpath:
        with open(fullpath, newline='', encoding="cp950") as rcsvfile:
            rows = list(csv.reader(rcsvfile))
            with open(fullpath.replace('.csv', '-fix.csv'), 'w', newline='') as wcsvfile:
                writer = csv.writer(wcsvfile)
                for row in rows:
                    writer.writerow(
                        [row[i].replace(" ","") for i in [0, 1, 2, 3, 4, 13, 22, 31, 40, 49, 58, 67, 76]])