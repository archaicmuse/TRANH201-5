import sys
from os import path
from csv import reader
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import ImageGrid


# configurations
database_extension = ".csv"
database_folder = path.split(path.abspath(__file__))[0] + "/database/"
database_file = database_folder + sys.argv[1] + database_extension

if path.exists(database_file):
    temperatures = []
    f = open(database_file)
    lines = reader(f, skipinitialspace=True)
    next(lines) # don't read first line
    for line in lines:
        line = list(map(int, line))
        temperatures.append([(line[0], line[1]), line[2]])
    print(temperatures)