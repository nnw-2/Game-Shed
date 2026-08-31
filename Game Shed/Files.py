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
        self.game_folders = self.load_game_folders()
        self.executables = self.load_individual_executables()

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

    def save(self,settings=False,folder_collection=False,game_folders=False) -> None:
        save_deciders = (settings,folder_collection,game_folders)
        
        save_options = (
            (os.path.join(self.pref_path,"settings.json"),self.settings),
            (os.path.join(self.pref_path,"folder_collections.json"),self.game_collections),
            (os.path.join(self.pref_path,"folders.json"),self.game_folders)
        )

        for i in range(3):
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
        folders_path = os.path.join(self.pref_path,"folder_collections.json")
        if os.path.exists(folders_path):
            with open(folders_path, "r") as folders_f:
                #before returning I should first check that all of the folders exist.
                #the user could of deleted some folders
                return json.load(folders_f)

#         colletion_list = []

#         if self.os == "Windows":
#             if os.path.exists(r"C:\Program Files (x86)\Steam\steamapps\common"):
#                 colletion_list.append(r"C:\Program Files (x86)\Steam\steamapps\common")
#         elif self.os == "Linux":
#             if os.path.exists(os.path.expanduser("~/.local/share/Steam/steamapps/common")):
#                 colletion_list.append(os.path.expanduser("~/.local/share/Steam/steamapps/common"))
#             elif os.path.exists(os.path.expanduser("~/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common")):
#                 colletion_list.append(os.path.expanduser("~/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common"))
        
# # {collection_name : [collection path , [exes] ] }
#         return colletion_list
        collections = {"All" : {"path":None,"exes":[]}}
        if self.os == "Windows":
            if os.path.exists(r"C:\Program Files (x86)\Steam\steamapps\common"):
                collections["Steam"] = {"path":r"C:\Program Files (x86)\Steam\steamapps\common","exes":[]}
        return collections

    def load_game_folders(self) -> list[list[str]]:
        folders_path = os.path.join(self.pref_path,"folders.json")
        if os.path.exists(folders_path):
            with open(folders_path, "r") as folders_f:
                return json.load(folders_f)

        folders_list = []
        # for collection in self.game_collections:
        #     if f"{os.sep}Steam{os.sep}" in collection:
        #         launcher = "Steam"
        #     elif f"{os.sep}Epic Games{os.sep}" in collection:
        #         launcher = "Epic"
        #     else:
        #         launcher = "unknown"
        #     folders_list += [[folder.path,launcher] for folder in os.scandir(collection) if os.path.isdir(folder.path)]
        for collection_name,collection_values in self.game_collections.items():
            if collection_values["path"] != None:
                if f"{os.sep}Steam{os.sep}" in collection_values["path"]:
                    launcher = "Steam"
                elif f"{os.sep}Epic Games{os.sep}" in collection_values["path"]:
                    launcher = "Epic"
                else:
                    launcher = "unknown"
                

        return folders_list

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
            case 0:
                ...
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

    def load_individual_executables(self) -> list[list[str]]:
        exe_path = os.path.join(self.pref_path,"executables.json")
        if os.path.exists(exe_path):
            with open(exe_path) as exe_f:
                return json.load(exe_f)
        
        exe_list = []
        for folder,launcher in self.game_folders:
            all_exe_in_folder = glob.glob(f"**{os.sep}*.exe",root_dir=folder,recursive=True)
            if len(all_exe_in_folder) == 0:
                continue
            
            wanted_exe = self.find_wanted_exe(all_exe_in_folder,folder)
            
            exe_list.append([folder + os.sep + wanted_exe[0],launcher,wanted_exe[1]])
            #this should be in the form: full file path, launcher associated with exe, whether the exe is of unknown type or a game

        return exe_list

    def update_collections(self,collection_name,added_data=None,removed_data=None,what_to_change="exes",update_collection_name=False):
        self.game_collections:dict[str,dict]
        
        if added_data == None and removed_data == None:
            return
        if what_to_change == "collections":
            # change the keys of the initial dict
            if update_collection_name:
                ... #if true then before removing add data to the new collection name

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

    def update_folders(self,added_exe,removed_exe):
        self.game_folders:dict[str,list[str]]


    def update_exes(self):
        self.executables


##### I am thinking of creating 2 different Files.py one for linux and this for windows
#In the main file check the os at the start and depending on the os the import will be a diff file

#To do here still. Add the saving (changing values of self.executables etc)


# {collection_name : [collection path , [exes] ] }
#there will be 2 types of colletions, one with collection path = None and the other with a path
# if None then that collection has not got associated folders to collect for their exes, it is just a
#collection in the sense that exes not found together will be grouped by the user here (user made collection only and the All collection)

# {exe : [ [associated collections] , launcher , unknown/game , image to display like icon file ? , folder]}

# {folder_path : [exes]} 
# folder identifier can just be the basename of the folder path
#potential issue with folder_id being the basename -> multiple folders sharing the same basename so use path as id
#but still store basename? ig


#make the finding files and folders different separate functions and in the loads just call a
#function to update values in the dict and pass in steam epic etc once confirming the file paths exist

#doing it through an update function would remove the problem of the exe losing information of which collection it should be attatched to 