import subprocess
import os
# subprocess.run(r"C:\Program Files (x86)\Steam\steamapps\common\Terraria\Terraria.exe") this works without cwd
#and auto opens up steam 

#####
#Steam games only seem to work if I don't pass in a cwd, only tested on terraria so far but prolly same for all

####
#Epic games only seem to work when the launcher is open

####
#If its a game not attatched to a launcher then it is probably best to pass in the cwd
def run_game(exe_path:str,launcher:str):
    if launcher == "Steam":
        subprocess.run(exe_path)
    elif launcher == "Epic Games":
        ...
    elif launcher == "unknown":
        subprocess.run(exe_path,cwd=exe_path.rpartition(os.sep)[0])