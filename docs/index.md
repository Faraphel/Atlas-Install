# Welcome to MKWF-Install docs !

## Introduction
MKWF-Install is an installer written in [Python](https://www.python.org) 
with the objective to make Mario Kart Wii Mod way easier to create, customize and
install, while staying as Nintendo copyright free as possible.

## Advantage 
### Patching
To create a mod in Mario Kart Wii, you would normally need to edit many repetitive
files and convert them between many classic and Nintendo filetypes.

This installer allow you to __describe how should a file be patched and transformed
before being copied to the game__. For example, you can put a PNG image inside your
mod, and set the installer to add write text on the image, paste another image on it,
encode it into a TPL file (Nintendo equivalent type for image files), instead of 
having to convert it manually everytime you modify the image.

The same thing apply for BMG files (files representing the game's text) that allow
for decoding, modifying the entry based on a regexp or on the message id and encoding.

cups icons are automatically generated too and combined to be easier to modify and
ready without having to edit a very tall PNG file.

### Custom Tracks
This mod allow you to add a track by simply adding an entry in a json file, and copying
the track file into a directory. No more need for patching manually all the texts, modifying
all the cups to insert a track, and everything that come with it. 

### Configuration
MKWF-Install allow you to configure even more one of the mods by letting you change
their configuration. You can override the "Random: new tracks" options, filter or 
highlight the tracks only if they fit certains criteria, sort them, ...


## Disadvantage
MKWF-Install is not as fast as the alternatives since Python is far from being the 
fastest language, and because of all the customization, it needs to process many
thing when doing an installation (Patching all the files, autogenerate files, 
convert the tracks to the game format).

Despite this, it stays pretty fast, and it will primarily depend on the mod that is
being installed (for example, Mario Kart Wii Faraphel will be slow because this mod
try to be as Nintendo copyright free as possible, and so need to do many conversion,
resulting in many time spent waiting for tracks conversion)