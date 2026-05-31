import glob
import os
import pygame
import json
from platform import system
import re

class Save_Load():
    IGNORE_EXACT = {
        "unitycrashhandler64.exe", 
        "unitycrashhandler32.exe",
        "crashreportclient.exe", 
        "cefsharp.browsersubprocess.exe",
        "qtwebengineprocess.exe",
        "awesomiumprocess.exe",
        "dxsetup.exe",
        "oalinst.exe",
        "config.exe",
        "settings.exe",
        "sysconfig.exe"
    }

    IGNORE_REGEX = re.compile(
        r"^(.*[\\/])?"
        r"("
        r"unins(t(all(er)?)?|\d{3})|"
        r"unwise|"                   
        r".*setup|"                  
        r"vc_?redist.*|"             
        r"dotnetfx.*|"               
        r"physx.*"                   
        r")\.exe$",
    )

    def __init__(self) -> None:
        self.pref_path = pygame.system.get_pref_path("nnw-2","Game Shed")
        self.os = system()
        self.settings = self.load_settings()
        self.game_folder_collection = self.load_game_folder_collection()
        self.game_folders = self.load_game_folders()
        self.executables = self.load_individual_executables()

    def save(self,settings=False,folder_collection=False,game_folders=False):
        save_deciders = (settings,folder_collection,game_folders)
        
        save_options = (
            (os.path.join(self.pref_path,"settings.json"),self.settings),
            (os.path.join(self.pref_path,"folder_collections.json"),self.game_folder_collection),
            (os.path.join(self.pref_path,"folders.json"),self.game_folders)
        )

        for i in range(3):
            if save_deciders[i]:
                with open(save_options[i][0], "w") as f:
                    json.dump(save_options[i][1],f,indent=4)
    
    def load(self,path):
        with open(path, "r") as f:
            return json.load(f)

    def load_settings(self):
        settings_path = os.path.join(self.pref_path,"settings.json")
        if os.path.exists(settings_path):
            return self.load(settings_path)

        return {
            "line_colour" : (255,255,255),
            "icon_colour" : (255,255,255),
            "background_colour" : (0,0,0)
        }

    def load_game_folder_collection(self):
        folders_path = os.path.join(self.pref_path,"folder_collections.json")
        if os.path.exists(folders_path):
            with open(folders_path, "r") as folders_f:
                #before returning I should first check that all of the folders exist.
                #the user could of deleted some folders
                return json.load(folders_f)

        colletion_list = []

        if self.os == "Windows":
            if os.path.exists(r"C:\Program Files (x86)\Steam\steamapps\common"):
                colletion_list.append(r"C:\Program Files (x86)\Steam\steamapps\common")
        elif self.os == "Linux":
            if os.path.exists(os.path.expanduser("~/.local/share/Steam/steamapps/common")):
                colletion_list.append(os.path.expanduser("~/.local/share/Steam/steamapps/common"))
            elif os.path.exists(os.path.expanduser("~/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common")):
                colletion_list.append(os.path.expanduser("~/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common"))
        
        return colletion_list

    def load_game_folders(self):
        folders_path = os.path.join(self.pref_path,"folders.json")
        if os.path.exists(folders_path):
            with open(folders_path, "r") as folders_f:
                return json.load(folders_f)

        folders_list = []
        for collection in self.game_folder_collection:
            folders_list += [folder.path for folder in os.scandir(collection) if os.path.isdir(folder.path)]

        return folders_list

    def find_wanted_exe(self,exe_list,root):
        close_exe_list = [] #close to the root
        for f in exe_list:
            num_sep = f.count(os.sep)
            if num_sep == 0: #exe within the initial dir
                close_exe_list.append(f)
            elif num_sep == 1: #exe within sub dir connected to root
                within_root_dir = glob.glob("*",root_dir=root)
                #the only thing in root dir is 1 sub dir
                if len(within_root_dir) == 1 and os.path.isdir(root + os.sep + within_root_dir[0]):
                    close_exe_list.append(f)
        
        if len(close_exe_list) != 0:
            ind_for_removal = set()
            for i,exe in enumerate(close_exe_list):
                filename_lower = os.path.basename(exe).lower()
                if exe in self.IGNORE_EXACT or self.IGNORE_REGEX.match(filename_lower):
                    ind_for_removal.add(exe)
                #add more stuff within this for loop, no need to loop over again
                
            post_removal_list = [item for i,item in enumerate(close_exe_list) if i not in ind_for_removal]
            match len(post_removal_list):
                case 0:
                    ...
                case 1:
                    return post_removal_list #its probably what is wanted
                case _:
                    ...
                    # re.findall()
                    # if "launcher.exe"
        
        #close_exe_list was or became empty. Check to see if one of the strings in exe_list is named Game.exe
        #or if it is named launcher or if the name is either the same or an abbreviation of the root folder name
        # e.g. .../P3R/P3R/Binaries/Win64/P3R.exe (the 1st P3R the root)



    def load_individual_executables(self):
        exe_path = os.path.join(self.pref_path,"executables.json")
        if os.path.exists(exe_path):
            with open(exe_path) as exe_f:
                return json.load(exe_f)
        
        exe_list = []
        for folder in self.game_folders:
            all_exe_in_folder = glob.glob(f"**{os.sep}*.exe",root_dir=folder,recursive=True)
            if len(all_exe_in_folder) == 0:
                continue
            # print(all_exe_in_folder)

            
            #then find the exe to use out of the ones found from the glob.glob list
            #the exe will probably be named the same as the root folder or Game
            #if there is a launcher then probably use that exe
            #remove UnityCrashHandler64.exe
            #remove any uninstaller exe
            #start_protected_game.exe (easy anti cheat)
            #CrashReportClient.exe (unreal engine)
            #remove any with setup in name
            #honestly probably just remove all past the root dir if there is a exe in the root dir
            

            exe_list.append(folder + os.sep + all_exe_in_folder[0])

        return exe_list


##### I am thinking of creating 2 different Files.py one for linux and this for windows
#In the main file check the os at the start and depending on the os the import will be a diff file
