"""
Breath color's, logo and other fun stuff!
"""

import subprocess

def logo():
    """
    Outputs Breath logo
    """
    subprocess.run(['toilet', '-f', 'mono12', '-F', 'crop', 'Breath'])
    subprocess.run(['toilet', '-f', 'term', '-F', 'border', 'Made by MilkyDeveloper'])

