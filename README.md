# AltStore Source for Vendetta
![Icons](https://skillicons.dev/icons?i=py,githubactions,github)

---

## How this works
This repository checks every 4 hours for new builds of Vendetta at https://discord.k6.tf/ios.  
If one exists, the AltStore source in the `pages` branch will be updated to the latest version.

## Installation
Tap below to open AltStore and add this source. Not working? Add `https://vendetta.burrito.software/apps.json` to AltStore.

[![Add to AltStore](https://taidums.are-really.cool/9nj3vv5.png | width=250)](https://vendetta.burrito.software)

## Manual Setup
This code can be run without GitHub actions.  
Tested on Windows 11 and `ubuntu-latest` Actions runner.

1. Make sure you have Python installed.
2. Install/upgrade dependencies:
  ```
  pip install -U -r requirements.txt
  ```
3. Duplicate `.env-example` to `.env`.
  ```
  cp .env-example .env
  ```
3. Run `generate.py`.
  ```
  python3 generate.py
  ```
4. The AltStore source file will be located, by default, in `out/apps.json`. A file to compare and track new versions will be, by default, in `cache/lastGenerated.json`. You can adjust these parameters in the `.env` file.