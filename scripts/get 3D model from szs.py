import bpy
import subprocess
import os
import glob
import shutil

TRACK_DIR: str = r"C:\Users\RC606\PycharmProjects\MKWF-Install\file\Track"
DEST_DIR: str = r"D:/gltf/"

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

os.chdir(TRACK_DIR)
os.makedirs(DEST_DIR, exist_ok=True)

clear_scene()

for file in glob.iglob("./*.szs"):
    try:
        
        print(sha1 := file.split("/")[-1].split("\\")[-1].split(".")[0])
        if os.path.exists(f"{DEST_DIR}/{sha1}.glb"): continue

        subprocess.run(["wszst", "extract", file], creationflags=subprocess.CREATE_NO_WINDOW)
        if not os.path.exists(f"./{sha1}.d/course_model.brres"): continue
        subprocess.run(["abmatt", "convert", f"./{sha1}.d/course_model.brres", "to", f"./{sha1}.d/course_model.obj"], creationflags=subprocess.CREATE_NO_WINDOW)
        if not os.path.exists(f"./{sha1}.d/course_model.obj"): continue
        
        bpy.ops.import_scene.obj(filepath=f"./{sha1}.d/course_model.obj")
        bpy.ops.export_scene.gltf(filepath=f"{DEST_DIR}/{sha1}.glb")
    
    except Exception as e: 
        with open("./error.log", "a") as file: file.write(str(e))
        
    finally:
        try:
            clear_scene()
            shutil.rmtree(f"./{sha1}.d/")
        except: pass

