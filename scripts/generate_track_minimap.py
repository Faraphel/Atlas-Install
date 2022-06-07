"""
Note : use this script from the ../scripts/ directory
"""
import glob
import subprocess
import os
import shutil

from source.wszst import szs
from scripts import obj_to_png


def get_track_minimap(directory: str, sha1: str):
    os.makedirs(tmp_dir := f"./scripts/tmp/{sha1}/", exist_ok=True)

    szs.extract(f"{directory}{sha1}.szs", tmp_dir + "track.szs")
    subprocess.run(["abmatt", "convert", tmp_dir + "track.szs.d/map_model.brres", "to", tmp_dir + "map_model.obj"])

    try: img = obj_to_png.render_top_view(obj_file=tmp_dir + "map_model.obj")
    except Exception as e:
        print(e)
        return None
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    return img


directory = "./file/Track/"

for track in glob.glob("*.szs", root_dir=directory):
    sha1 = track.replace(".szs", "")
    if (image := get_track_minimap(directory, sha1)) is not None:
        image.save(f"./scripts/minimap/{sha1}.png")
