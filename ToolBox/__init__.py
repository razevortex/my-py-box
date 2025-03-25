from pathlib import Path
import subprocess as sp
import os
import sys
script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
print(script_directory)
print(__file__)
print(Path.cwd())
print(os.getcwd())
temp = sp.STARTUPINFO()
temp.dwFlags |= sp.STARTF_USESHOWWINDOW
print(sp.run('powershell.exe', startupinfo=temp))