# Import packages---------------------------------------------------------------------------------------------
## Data Acess and Manipulation
import pandas as pd

## Utilities
### importing necessary functions from dotenv library and loading variables from .env file
import os
import logging
from functools import partial
#from google.colab import userdata
from multiprocessing import cpu_count
from dotenv import load_dotenv 
load_dotenv()
# Notebook Configurations
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

"""Capacited Vehicles Routing Problem (CVRP)."""

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from src.utils.data_loaders import save_dict
# Functions---------------------------------------------------------------------------------------------

import requests
import json
import time

def reverse_coordinates(input):
  output = []
  for each in input:
    each.reverse()
    output.append(each)
  return output

def return_coords(coords,ls):
    r_ls = [coords[each] for each in ls]
    r_ls = list(map(list,r_ls))
    r_ls = reverse_coordinates(input=r_ls)
    return r_ls

def return_ids(ids,ls):
    r_ls = [ids[each] for each in ls]
    return r_ls

def call_api(coordinates):

  body = {"coordinates": coordinates}

  headers = {
      'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
      'Authorization': '5b3ce3597851110001cf624822b79fbe37204f6a83490d4a1566d9a5',
      'Content-Type': 'application/json; charset=utf-8'
  }
  call = requests.post('https://api.openrouteservice.org/v2/directions/driving-car', json=body, headers=headers)

  # print(call.status_code, call.reason)
  if call.status_code == 200:
    response = json.loads(call.text)
    geometry = response['routes'][0]['geometry']
    distance = round(response['routes'][0]['summary']['distance']/1000,1)
    duration = round(response['routes'][0]['summary']['duration']/60,1)
  else:
    print("API call failed for this list of coordinates coordinates: ", coordinates)
    print(call.text)
    geometry = None
    distance = 1
    duration = 1

  return geometry, distance, duration

def enhance_optimized_route(op, coords, ids):
  output = {}
  for k, v in op.items():
    output[k] = {}
    for k2, v2 in v.items():
      if k2 == 'route_plan':
        time.sleep(2)
        if len(return_coords(coords ,op[k]['route_plan'])) > 1:
          api_response = call_api(coordinates=return_coords(coords, op[k]['route_plan']))
          output[k]['route_geometry'] = api_response[0]
          output[k]['route_distance'] = api_response[1]
          output[k]['route_duration'] = api_response[2]
        else:
          output[k]['route_geometry'] = 1
          output[k]['route_distance'] = 1
          output[k]['route_duration'] = 1

      output[k]['route_plan'] = op[k]['route_plan']
      output[k]['cumulative_route_load'] = op[k]['cumulative_route_load']
      #output[k]['route_distance'] = 0
      output[k]['route_coords'] = return_coords(coords, op[k]['route_plan'])
      output[k]['route_ids'] = return_ids(ids, op[k]['route_plan'])

  #Save the Output
  save_location = r'assets\data\appData\route_output.json'  # Specify your file location
  save_dict(save_location, output)

  return output

