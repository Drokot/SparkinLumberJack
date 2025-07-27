# Semi-Auto Lumberjacking Script for Ultima Online UOAlive TOS Compliant 
**Version**: 7/2025  
**Author**: Sparkin  
**Modified by**: Grok (xAI)  
**Special Thanks**: Kurien33 for many hours of testing and development help  

## Disclaimer
**Important**: Using this script or any scripts for unattended resource gathering in UOAlive is strictly prohibited by server rules and can result in account bans or other penalties, including account suspension or permanent banning. Unattended macroing violates UOAlive’s Terms of Service and policies. Always review and comply with UOAlive’s macroing rules before running this script. The author, contributors, and modifiers (including Sparkin, Kurien33, and Grok) are not responsible for any consequences, such as account bans, suspensions, or loss of resources, resulting from the use of this script. Use at your own risk and actively monitor the script to avoid violations of server rules.

This script automates lumberjacking in Ultima Online, allowing you to chop trees, convert logs to boards (optional), and store resources in Up To  (5) Five pack beetles. It includes a safety net for detecting nearby players or invulnerable entities and a feature to walk 10 tiles in a random direction when no trees are found. The script was originally a combined lumberjacking and mining script but was modified to focus solely on lumberjacking.

## Features
- Scans for trees within a 20-tile radius and moves to the nearest one to chop.
- Converts logs to boards (optional) and stores them in up to five pack beetles.
- Supports mounting/dismounting beetles with the `mountAfterMove` option.
- Walks 10 tiles in a random direction (up to 10 attempts) when no trees are found.
- Alerts for special woods (bloodwood, heartwood, frostwood) with on-screen messages.
- Includes a safety net to detect nearby players or invulnerable entities with text-to-speech alerts.
- Automatically equips an axe and handles tree depletion with a 20-minute cooldown.
- Optimized to distribute resources across beetles to maximize storage.

## Requirements
- **Client**: Ultima Online with a supported client (e.g., Razor, TAZUO, UOSteam).
- **Dependencies**: Python with `System.Speech` library (for text-to-speech alerts).
- **Environment**: Run in a forested area with trees within 20 tiles.
- **Pack Beetles**: Up to five tamed beetles within 2-3 tiles of the player.
- **Axe**: An axe in your backpack or equipped (matching `axeList` IDs).

## Installation
1. Save the script as `lumberjacking.py` (or similar) in your scripting environment (e.g., Razor or UOSteam script folder).
2. Ensure Python is installed with the `System.Speech` library for text-to-speech functionality (Windows only; disable `alert` if unavailable).
3. Verify your Ultima Online client is running and configured to work with your scripting tool.

## Configuration
Edit the `# Configuration` section of the script to match your setup:

- **packAnimals**: List of up to five beetle serials and types. Example:
  ```python
  packAnimals = [
      {'serial': 0x043D5FC2, 'type': 'beetle'},
      {'serial': 0x09B6F6B9, 'type': 'beetle'},
      {'serial': 0x09B6F26D, 'type': 'beetle'},
      {'serial': 0x09B6F3B1, 'type': 'beetle'},
      {'serial': 0x09B87679, 'type': 'beetle'},
  ]
