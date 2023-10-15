import json
import os
import zipfile
import plistlib
from entitlements import getEntitlements
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
import shutil

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
APP_KEY = os.getenv("APP_KEY")
BINARY_KEY = os.getenv("BINARY_KEY")
EXTRACT_TO = os.getenv("EXTRACT_TO")
OUTPUT_TO = os.getenv("OUTPUT_TO")
CACHE_TO = os.getenv("CACHE_TO")

# Create EXTRACT_TO folder
if not os.path.exists(EXTRACT_TO):
  os.makedirs(EXTRACT_TO)

# Create OUTPUT_TO folder
if not os.path.exists(OUTPUT_TO):
  os.makedirs(OUTPUT_TO)

# Create CACHE_TO folder
if not os.path.exists(CACHE_TO):
  os.makedirs(CACHE_TO)

response = requests.get(BASE_URL)
soup = BeautifulSoup(response.content, 'html.parser')

# Get the latest build version from the file list
trs = soup.find('body').find('main').find('table').find('tbody').find_all('tr')
latestPath = trs[-1].find('td', {'class': 'name'}).find('a').text

# If lastGenerated.json does not exist, or if key "buildVersion" is not the same as latestPath[:-1], then continue
if not os.path.exists(f'{CACHE_TO}/lastGenerated.json') or json.load(open(f'{CACHE_TO}/lastGenerated.json', 'r'))['buildVersion'] != latestPath[:-1]:
    print(f'Starting to generate source for build {latestPath[:-1]}...')
else:
  # If lastGenerated.json exists and key "buildVersion" is the same as latestPath[:-1], then exit
  print('No new builds found. Exiting.')
  exit()

# AltStore source construction
source = {}
source['name'] = 'Vendetta'
source['identifier'] = 'tf.k6.discord'
source['subtitle'] = 'A mod for Discord\'s mobile apps.'
source['iconURL'] = 'https://avatars.githubusercontent.com/u/112445065?s=200&v=4'
source['website'] = 'https://github.com/vendetta-mod/Vendetta'
source['tintColor'] = '#3ab8ba'
source['apps'] = []
source['news'] = []

vendettaApp = {
  "name": "Vendetta",
  "bundleIdentifier": "com.hammerandchisel.discord",
  "developerName": "Vendetta Contributors",
  "subtitle": "A mod for Discord's mobile apps.",
  "localizedDescription": "A platform-agnostic mod for Discord's mobile apps. These IPAs are sourced from https://discord.k6.tf/ios.",
  "iconURL": "https://taidums.are-really.cool/5knt7F7.png",
  "tintColor": "#3ab8ba"
}
vendettaApp['versions'] = []

# Download the file at BASE_URL/tdAPP_KEY, then extract the Info.plist and binary from the zip in the Payload folder
downloadURL = f"{BASE_URL}/{latestPath}{APP_KEY}"
response = requests.get(downloadURL)
with open(f'{EXTRACT_TO}/{APP_KEY}', 'wb') as f:
  f.write(response.content)
with zipfile.ZipFile(f'{EXTRACT_TO}/{APP_KEY}', 'r') as zip_ref:
  zip_ref.extract(f'Payload/{BINARY_KEY}.app/Info.plist', path=EXTRACT_TO)
  zip_ref.extract(f'Payload/{BINARY_KEY}.app/{BINARY_KEY}', path=EXTRACT_TO)

##
# Creating and adding the latest version
##

# Get the last modified date of the latest build
response = requests.get(f"{BASE_URL}/{latestPath}")
soup = BeautifulSoup(response.content, 'html.parser')
trs = soup.find('body').find('main').find('table').find('tbody').find_all('tr')
# In trs[-1], get the last td, then get the time tag inside of it, then cut off the space and everything past it
lastModified = trs[-1].find_all('td')[-1].find('time').text.split(' ')[0]

# Declare the plist to get useful info like CFBundleShortVersionString and CFBundleVersion
plist = plistlib.load(open(f'{EXTRACT_TO}/Payload/Discord.app/Info.plist', 'rb'))

version = {
  "version": plist['CFBundleShortVersionString'],
  "buildVersion": plist['CFBundleVersion'],
  "date": lastModified,
  "localizedDescription": f"{plist['CFBundleShortVersionString']} ({plist['CFBundleVersion']})",
  "downloadURL": downloadURL,
  "minOSVersion": plist['MinimumOSVersion']
}
vendettaApp['versions'].append(version)

##
# Adding appPermissions including entitlements and privacy
##

vendettaApp['appPermissions'] = {}
vendettaApp['appPermissions']['entitlements'] = []

for entitlement in getEntitlements(f'{EXTRACT_TO}/Payload/{BINARY_KEY}.app/{BINARY_KEY}'):
  entitlementObject = {
    "name": entitlement
  }
  vendettaApp['appPermissions']['entitlements'].append(entitlementObject)

vendettaApp['appPermissions']['privacy'] = []

for key, value in plist.items():
    # Check if the key starts with "NS" and ends with "UsageDescription"
    if key.startswith("NS") and key.endswith("UsageDescription"):
      # Get the name of the permission by removing the "NS" and "UsageDescription" parts
      permissionName = key[2:-16]
      privacyObject = {
        "name": permissionName,
        "description": value
      }
      vendettaApp['appPermissions']['privacy'].append(privacyObject)

# Add vendettaApp to the source
source['apps'].append(vendettaApp)

# Output source variable as json to a file named apps.json
with open(f'{OUTPUT_TO}/apps.json', 'w') as f:
  f.write(json.dumps(source, indent=2))
  print('Source generated.')

# Generate lastGenerated.json and save it to CACHE_TO/lastGenerated.json
lastGenerated = {
  "version": plist['CFBundleShortVersionString'],
  "buildVersion": plist['CFBundleVersion'],
}

with open(f'{CACHE_TO}/lastGenerated.json', 'w') as f:
  f.write(json.dumps(lastGenerated, indent=2))

# Delete the EXTRACT_TO folder and its contents
shutil.rmtree(EXTRACT_TO)