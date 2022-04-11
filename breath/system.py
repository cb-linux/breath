import subprocess
import platform
import sys

def logo():
    subprocess.run(['toilet', '-f', 'mono12', '-F', 'crop', 'Breath'])
    subprocess.run(['toilet', '-f', 'term', '-F', 'border', 'Made by MilkyDeveloper'])

