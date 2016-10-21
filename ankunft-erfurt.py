#!/usr/bin/python
import requests
import json
from BeautifulSoup import BeautifulSoup

url = 'http://www.mdr.de/verkehr/erfurt-weimar/flughafen-erfurt100.html'
response = requests.get(url)
html = response.content

soup = BeautifulSoup(html)
table = soup.find('table', attrs={'summary': 'Ankunft Flughafen'})

list_of_rows = []
for row in table.findAll('thead'):
    list_of_cells = []
    for cell in row.findAll('th'):
        text = cell.text.replace('&nbsp;', '')
        list_of_cells.append(text)
    list_of_rows.append(list_of_cells)

for row in table.findAll('tr')[1:]:
    list_of_cells = []
    for cell in row.findAll('td'):
        text = cell.text.replace('&nbsp;', '')
        list_of_cells.append(text)
    list_of_rows.append(list_of_cells)

flighttable = {}
flighttable["erfurt"] = {}
flighttable["erfurt"]["arrivals"] = []

for flight in list_of_rows[1:]:
  flighttable["erfurt"]["arrivals"].append( { 'flight':flight[0], 'from':flight[1], 'awaited-by-plan':flight[2], 'awaited':flight[3], 'status':flight[4] } )

print(json.dumps(flighttable))
