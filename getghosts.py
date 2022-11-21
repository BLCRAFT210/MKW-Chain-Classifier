#make sure this doesn't try downloading runs that don't have ghosts

import requests
import json

URL = 'https://tt.chadsoft.co.uk'

#r = requests.get(URL+'/leaderboard/08/1AE1A7D894960B38E09E7494373378D87305A163/00.json')
#data = json.loads(r.text)
f = open('leaderboard.json')
data = json.load(f)
for entry in data['ghosts'][:10]:
    if entry['vehicleId'] == 32 and entry['driverId'] == 22: #ensure that the run is set with Funky Kong on the Spear
        ghostUrl = 'https://tt.chadsoft.co.uk'+entry['_links']['item']['href'][:-4]+'rkg'
        print(ghostUrl)