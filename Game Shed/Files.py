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

    GAME_EXACT = {
        "game.exe",
        "main.exe",
        "client.exe",
        "app.exe",
        "application.exe",
        "bin.exe",
        "player.exe",
        "playgame.exe",
        "gameclient.exe"
    }

    IGNORE_REGEX = re.compile(
        r"^(.*[\\/])?"
        r"("
        r"unins(t(all(er)?)?|\d{3})|"
        r"unwise|"
        r".*setup|"
        r"vc_?redist.*|"
        r"dotnetfx.*|"
        r"physx.*|"
        r".*crashpad.*"
        r")\.exe$",
    )

    def __init__(self) -> None:
        self.pref_path = pygame.system.get_pref_path("nnw-2","Game Shed")
        self.os = system()
        self.settings = self.load_settings()
        self.game_collections = self.load_game_collections()
        self.executables = self.load_individual_executables()
        self.game_folders = self.load_game_folders()

    def is_main_exe(self,root:str,exe:str) -> bool:
        #compare the root folder name to the passed in exe 
        game_folder = os.path.basename(root)
        exe_name_only = exe[:-4]
        
        if exe_name_only.lower() == game_folder.lower():
            return True
        #try and see if an abbreviation
        abbreviated_folder = "".join([letter.lower() for letter in game_folder if letter.isupper()])
        if exe_name_only.lower() == abbreviated_folder:
            return True
       
        seper_exe_name = re.sub(r"(?<=[a-z])(?=[A-Z])", " " , exe_name_only)
        full_seper_exe_name = re.findall(r"[a-z]+|[0-9]+",seper_exe_name.lower())

        similar_names = True
        for s in full_seper_exe_name:
            if s in game_folder.lower():
                continue
            similar_names = False
            break
        
        if similar_names:
            return True

        return False

    def save(self,settings=False,collections=False,game_folders=False,exes=False) -> None:
        save_deciders = (settings,collections,game_folders,exes)
        
        save_options = (
            (os.path.join(self.pref_path,"settings.json"),self.settings),
            (os.path.join(self.pref_path,"collections.json"),self.game_collections),
            (os.path.join(self.pref_path,"folders.json"),self.game_folders),
            (os.path.join(self.pref_path,"executables.json"),self.executables)
        )

        for i in range(4):
            if save_deciders[i]:
                with open(save_options[i][0], "w") as f:
                    json.dump(save_options[i][1],f,indent=4)
    
    def load(self,path:str):
        with open(path, "r") as f:
            return json.load(f)

    def load_settings(self) -> dict[str , tuple]:
        settings_path = os.path.join(self.pref_path,"settings.json")
        if os.path.exists(settings_path):
            return self.load(settings_path)

        return {
            "line_colour" : (255,255,255),
            "icon_colour" : (255,255,255),
            "background_colour" : (0,0,0)
        }

    def load_game_collections(self) -> dict[str,dict[str,str|list[str]|None]]:
        folders_path = os.path.join(self.pref_path,"collections.json")
        if os.path.exists(folders_path):
            with open(folders_path, "r") as folders_f:
                #before returning I should first check that all of the folders exist.
                #the user could of deleted some folders
                return json.load(folders_f)

#         if self.os == "Windows":
#             if os.path.exists(r"C:\Program Files (x86)\Steam\steamapps\common"):
#                 colletion_list.append(r"C:\Program Files (x86)\Steam\steamapps\common")
#         elif self.os == "Linux":
#             if os.path.exists(os.path.expanduser("~/.local/share/Steam/steamapps/common")):
#                 colletion_list.append(os.path.expanduser("~/.local/share/Steam/steamapps/common"))
#             elif os.path.exists(os.path.expanduser("~/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common")):
#                 colletion_list.append(os.path.expanduser("~/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common"))
        
        self.game_collections = {"All" : {"path":None,"exes":[]}}
        if self.os == "Windows":
            if os.path.exists(r"C:\Program Files (x86)\Steam\steamapps\common"):
                self.game_collections["Steam"] = {"path":r"C:\Program Files (x86)\Steam\steamapps\common","exes":[]}
            
        return self.game_collections

    def load_game_folders(self) -> dict[str,list[str]]:
        folders_path = os.path.join(self.pref_path,"folders.json")
        if os.path.exists(folders_path):
            with open(folders_path, "r") as folders_f:
                return json.load(folders_f)

        self.game_folders = {}
        
        #don't need to use a deep copy in this case
        for collection_name,collection_values in self.game_collections.items():
            if collection_values["path"]  == None:
                continue
            
            for folder in os.scandir(collection_values["path"]):
                if os.path.isdir(folder.path):
                    all_exe_in_folder = glob.glob(f"**{os.sep}*.exe",root_dir=folder.path,recursive=True)
                    if len(all_exe_in_folder) == 0:
                        continue
                    exe,exe_type = self.find_wanted_exe(all_exe_in_folder,folder.path)
                    full_exe_path = folder.path + os.sep + exe
                    self.game_folders[folder.path] = [full_exe_path]
                    #The collections available on first run should be launchers so this is ok
                    self.executables[full_exe_path] = {"collections":["All",collection_name],"launcher":collection_name,"type":exe_type,"folder":folder.path}
                    self.game_collections["All"]["exes"].append(full_exe_path)
                    self.game_collections[collection_name]["exes"].append(full_exe_path)
        return self.game_folders

    def f_w_e_logic(self,list:list[str],root:str) -> list[str]: #find wanted exe logic
        new_useful_list = []
        game_count = 0
        for exe in list:
            #add more stuff within this for loop, no need to loop over again
            filename_lower = os.path.basename(exe).lower()
            if filename_lower in self.IGNORE_EXACT or self.IGNORE_REGEX.match(filename_lower):
                ... #don't add it to the new list, it isn't wanted
            elif filename_lower in self.GAME_EXACT or self.is_main_exe(root,os.path.basename(exe)): #check if Game.exe or game name .exe
                new_useful_list.append([exe,"game"])
                game_count += 1
            else:
                new_useful_list.append([exe,"unknown"])
            
        match len(new_useful_list):
            case 1:
                return new_useful_list[0] #its probably what is wanted
            case _:
                biggest_size = 0
                ind_to_use = 0
                if game_count == 0:
                    for i, exe in enumerate(new_useful_list):
                        if os.path.getsize(root+os.sep+exe[0]) > biggest_size:
                            biggest_size = os.path.getsize(root+os.sep+exe[0])
                            ind_to_use = i
                    return new_useful_list[ind_to_use]
                if game_count == 1:
                    for exe in new_useful_list:
                        if exe[1] == "game":
                            return exe
                for i,exe in enumerate(new_useful_list):
                    if exe[1] == "game" and os.path.getsize(root+os.sep+exe[0]) > biggest_size:
                        biggest_size = os.path.getsize(root+os.sep+exe[0])
                        ind_to_use = i
                new_useful_list[ind_to_use][1] = "unknown"
                return new_useful_list[ind_to_use]
    
    def find_wanted_exe(self,exe_list:list[str],root:str) -> list[str]:
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
            return self.f_w_e_logic(close_exe_list,root)
        return self.f_w_e_logic(exe_list,root)

    def load_individual_executables(self) -> dict:
        exe_path = os.path.join(self.pref_path,"executables.json")
        if os.path.exists(exe_path):
            with open(exe_path) as exe_f:
                return json.load(exe_f)
        return {}
    
    def update_collections(self,collection_name,added_data=None,removed_data=None,what_to_change="exes",update_collection_name=False):
        self.game_collections:dict[str,dict]
        
        if added_data == None and removed_data == None:
            return
        if what_to_change == "collections":
            if update_collection_name:
                self.game_collections[collection_name] = self.game_collections.pop(removed_data)
                for exe in self.game_collections[collection_name]["exes"]:
                    self.executables[exe]["collections"].remove(removed_data)
                    self.executables[exe]["collections"].append(collection_name)
                return
            if added_data:
                self.game_collections[collection_name] =  {"path":None,"exes":[]} 
                #if i want to add a collection with a path then do update_collections(what_to_change="collections") followed by update_collections(what_to_change="path")
                #not both in the same function call
            elif removed_data:
                self.game_collections.pop(collection_name)
            return

        if what_to_change == "path":
            self.game_collections[collection_name][what_to_change] = added_data
            #more stuff needs to be added here ltr
            #if changing to none then shouldn't need to do anything
            #if changing from None or to a different path then should prompt the user
            #if they want to keep the exes already in the collection or clear them
            #it should then add exes to the collection based on the given path
            return
        if added_data != None:
            self.game_collections[collection_name][what_to_change].append(added_data)
            self.executables[added_data]["collections"].append(collection_name)
        if removed_data != None:
            self.game_collections[collection_name][what_to_change].remove(removed_data)
            self.executables[removed_data]["collections"].remove(collection_name)

    def update_folders(self,folder,added_data=None,removed_data=None,what_to_change="exes",updating_folder=False):
        self.game_folders:dict[str,list[str]]
        if added_data == None and removed_data == None:
            return
        if what_to_change == "folders":
            if updating_folder:
                self.game_folders[folder] = self.game_folders.pop(removed_data)
                for exe in self.game_folders[folder]:
                    self.executables[exe]["folder"] = folder
                return
            if added_data:
                self.game_folders[folder] = []
            elif removed_data:
                self.game_folders.pop(folder)
            return
        if added_data != None:
            self.game_folders[folder].append(added_data)
            self.executables[added_data]["folder"] = folder
        if removed_data != None:
            self.game_folders[folder].remove(removed_data)
            self.executables[removed_data]["folder"] = ""

    def update_exes(self,exe,added_data=None,removed_data=None,what_to_change="exes",update_exe_path=False):
        self.executables:dict[str,dict[str,list[str]|str]]
        if added_data == None and removed_data == None:
            return
        if what_to_change == "exes":
            if update_exe_path:
                self.executables[exe] = self.executables.pop(removed_data)
                self.game_folders[self.executables[exe]["folder"]].remove(removed_data)
                self.game_folders[self.executables[exe]["folder"]].append(exe)
                for collection in self.executables[exe]["collections"]:
                    self.game_collections[collection]["exes"].remove(removed_data)
                    self.game_collections[collection]["exes"].append(exe)
                return
            if added_data:
                self.executables[exe] = {"collections":[],"launcher":"unknown","type":"unknown","folder":""}
            if removed_data:
                self.executables.pop(removed_data)
            return
        if what_to_change == "collections":
            self.executables[exe]["collections"].remove(removed_data)
            self.executables[exe]["collections"].append(added_data)
            self.game_collections[removed_data]["exes"].remove(exe)
            self.game_collections[added_data]["exes"].append(exe)
            return
        if what_to_change == "launcher":
            self.executables[exe]["launcher"] = added_data
            return
        if what_to_change == "type": #unknown/game
            self.executables[exe]["type"] = added_data
            return
        if what_to_change == "folder":
            if added_data != "":
                self.game_folders[self.executables[exe]["folder"]].remove(exe)
                self.game_folders[added_data].append(exe)
            else:
                self.game_folders[self.executables[exe]["folder"]].remove(exe)
            self.executables[exe]["folder"] = added_data
          

##### I am thinking of creating 2 different Files.py one for linux and this for windows
#In the main file check the os at the start and depending on the os the import will be a diff file

#eventually i might want to let the user move the location of an exe and have it work still by retaining the working directory given to the exe
test = Save_Load()

test.save(collections=True,game_folders=True,exes=True)