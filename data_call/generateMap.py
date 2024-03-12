import data as dc
import mysql.connector
import sys
import folium
import webbrowser

#dc.mapGeneration()
def generateMap(pm_type):
    dc.mapGeneration(pm_type=pm_type)

if len(sys.argv) > 1:
    pm_type = sys.argv[1]
    dc.mapGeneration(pm_type=pm_type)
else:
    print("Need a pm")