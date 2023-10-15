import re
import xml.etree.ElementTree as ET

def getEntitlements(binary_file_path):

  # Create a regular expression pattern to match plist data
  plist_pattern = re.compile(rb'<plist[\s\S]*?</plist>', re.DOTALL)

  # Initialize an empty list to store keys
  keys = []

  # Read the binary file
  with open(binary_file_path, 'rb') as file:
      binary_data = file.read()

  # Search for plist data within the binary data
  plist_matches = plist_pattern.findall(binary_data)

  # Iterate through the matches and extract keys
  for i, match in enumerate(plist_matches):
      plist_data = match.decode('utf-8')  # Assuming the plist is in UTF-8 encoding

      # Check if the XML-encoded plist data contains a key element
      if "<key>" in plist_data:
          try:
              root = ET.fromstring(plist_data)
              for key_element in root.findall(".//key"):
                  key = key_element.text
                  if key not in ["application-identifier", "com.apple.developer.team-identifier"]:
                      keys.append(key)
          except ET.ParseError:
              # Skip malformed XML data
              continue
  
  return keys
