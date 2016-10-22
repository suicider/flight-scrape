#!/usr/bin/python
import csv
import requests
import json
import re
from BeautifulSoup import BeautifulSoup

from datetime import datetime

def statusCol(status):
  if status == "GELANDET" or "gelandet":
    return COL_GREEN
  elif status =="GESTARTET":
    return COL_GREEN
  else:
    return ""

def isStateADate(state):
  pattern = re.compile("^([0-9]{2})\.([0-9]{2})\.$")
  result  = pattern.match(state)
  
  if result:
    return (datetime.now().strftime("%Y") +"-"+ result.group(2) +"-"+ result.group(1))
  else:
    return False

def isVia(origin_or_destination):
  pattern = re.compile("^(.)+ VIA (.)+$")
  result  = pattern.match(origin_or_destination)
  
  if result:
    return ( { 'origin_or_destination':result.group(1), 'via':result.group(2) } )
  else:
    return False


#--------------Setup------------#
cities = {'erfurt'  : 'http://www.mdr.de/verkehr/erfurt-weimar/flughafen-erfurt100.html',
          'leipzig' : 'http://www.mdr.de/verkehr/leipzig-halle/index.html',
          'dresden' : 'http://www.mdr.de/verkehr/dresden/index.html'
         }
flighttable = {}


#-----------Main logic-----------#
# Iterate over each city and build new structure
for city in cities:
  url = cities[city]
  response = requests.get(url)
  html = response.content

  soup = BeautifulSoup(html)
  table = soup.find('table', attrs={'summary': 'Ankunft Flughafen'})

  arrivals_list_of_rows = []
  for row in table.findAll('thead'):
      list_of_cells = []
      for cell in row.findAll('th'):
          text = cell.text.replace('&nbsp;', '')
          list_of_cells.append(text)
      arrivals_list_of_rows.append(list_of_cells)

  for row in table.findAll('tr')[1:]:
      list_of_cells = []
      for cell in row.findAll('td'):
          text = cell.text.replace('&nbsp;', '')
          list_of_cells.append(text)
      arrivals_list_of_rows.append(list_of_cells)

  table = soup.find('table', attrs={'summary': 'Abflug Flughafen'})

  departures_list_of_rows = []
  for row in table.findAll('thead'):
      list_of_cells = []
      for cell in row.findAll('th'):
          text = cell.text.replace('&nbsp;', '')
          list_of_cells.append(text)
      departures_list_of_rows.append(list_of_cells)

  for row in table.findAll('tr')[1:]:
      list_of_cells = []
      for cell in row.findAll('td'):
          text = cell.text.replace('&nbsp;', '')
          list_of_cells.append(text)
      departures_list_of_rows.append(list_of_cells)

  flighttable[city] = {}
  flighttable[city]["arrivals"] = []
  flighttable[city]["departures"] = []

  for flight in arrivals_list_of_rows[1:]:
    # parse the date from flight[4]
    date = isStateADate(flight[4])
    if date:
      date = date
      flight[4]=""
    else:
      #fill with todays date
      date = datetime.now().strftime("%Y-%m-%d")

    via = isVia(flight[1])
    if via:
      flight[1] = via["origin_or_destination"]
      via       = via["via"]
    else:
      via       = ""
    flighttable[city]["arrivals"].append( { 'date':date, 'flight':flight[0], 'from':flight[1], 'via':via , 'awaited-by-plan':flight[2], 'awaited':flight[3], 'status':flight[4] } )


  for flight in departures_list_of_rows[1:]:
    # parse the date from flight[4]
    date = isStateADate(flight[4])
    if date:
      date = date
      flight[4]=""
    else:
      # fill with todays date
      date = datetime.now().strftime("%Y-%m-%d")

    via = isVia(flight[1])
    if via:
      flight[1] = via["origin_or_destination"]
      via       = via["via"]
    else:
      via       = ""
    flighttable[city]["departures"].append( { 'date':date, 'flight':flight[0], 'from':flight[1], 'via':via , 'awaited-by-plan':flight[2], 'awaited':flight[3], 'status':flight[4] } )


#-------End of API building-------#

# Simple output example
json_output = json.dumps(flighttable)
print(json_output)
