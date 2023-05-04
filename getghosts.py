# Pulls the top 1000 ghosts from CTGP and saves them to the ghosts folder. Ghosts are documented in leaderboard.json.
import requests
import json
import os

URL = 'https://tt.chadsoft.co.uk'
NGHOSTS = 1000

# download leaderboard
print('Retrieving leaderboard... (this may time a while)')
try:
    r = requests.get(
        URL+'/leaderboard/08/1AE1A7D894960B38E09E7494373378D87305A163/00.json')
except:
    print('Error retrieving leaderboard.')
    exit()
data = json.loads(r.text)

# make ghosts folder if it doesn't exist
try:
    os.mkdir('ghosts')
except:
    pass

# make leaderboard.json if it doesn't exist
if ('leaderboard.json' not in os.listdir()):
    with open('leaderboard.json', 'w') as f:
        json.dump({}, f)
    print('New leaderboard.json created.')

# load leaderboard.json
with open('leaderboard.json', 'r+') as f:
    leaderboard = json.load(f)
    print('leaderboard.json found, loading...')

    # download ghosts
    for n, entry in enumerate(data['ghosts'][:NGHOSTS]):
        if entry['hash'] in leaderboard:
            print('Skipping run '+str(n+1)+' with hash ' +
                  entry['hash']+': already downloaded')

        elif entry['vehicleId'] != 32 or entry['driverId'] != 22:
            print('Skipping run '+str(n+1)+' with hash ' +
                  entry['hash']+': not set with Funky Kong on the Spear')

        else:
            print('Downloading run '+str(n+1) +
                  ' with hash '+entry['hash']+'...')
            r = requests.get('https://tt.chadsoft.co.uk'+entry['href'])
            with open('ghosts/'+entry['hash']+'.rkg', 'wb') as ghostFile:
                ghostFile.write(r.content)

            entry['replayed'] = False
            leaderboard[entry['hash']] = entry
            f.seek(0)
            json.dump(leaderboard, f)
            f.truncate()
            print(entry['finishTimeSimple']+' by ' +
                  entry['player']+' downloaded successfully!')
