###TESTING THE FOLIUM LIBRARY FOR MAP GENERATION###

#import googlemaps
#import gmaps.datasets
import folium
import webbrowser
#from data_call import data as dc
import pandas as pd

latitude = 33.593400
longitude = -116.079800

m = folium.Map(location=[latitude, longitude], zoom_start=13)

folium.Marker(location=[latitude, longitude], popup="Monitor1").add_to(m)

html_file_path = 'map.html'
m.save(html_file_path)

webbrowser.open(html_file_path)