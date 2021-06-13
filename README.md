# FAF-AI-Autorun

## Pre-requisites
- Python 3 installed (pip too would be helpful)
- FAF installed, and any AI mods you want to use loaded (run a game with them
  all active to be sure).
- Git installed

## Prep
You will need to be comfortable running commands in a console like cmd or
Powershell.
    - Open a command prompt (start -> search for 'cmd' or 'Powershell')
    - Browse to the location of this repo (`cd` is the change directory command,
    `dir` lists stuff in the current directory)

1. Clone this repo using git. You can use either git bash or the git gui to do
this. Make a note of what folder you cloned it to.

2. Navigate to the directory where you cloned this repo in cmd/Powershell by
typing `cd C:\Path\To\FAF-AI-Autorun`
3. Install autorun by typing `python autorun.py install`

This will perform the steps described in the 'Install manually' section. You can
uninstall any time by deleting the `autorun.zip` and `init_autorun.lua` files or by running `python autorun.py uninstall`.

## Usage
1. If you want windows to be minimized automatically, install the requirements
    - run `python -m pip install -r requirements.txt`
2. Edit the `experiments.py` file to set up the experiments you want to run.
3. Run `python autorun.py batch` with desired options
    - run `python autorun.py batch --help` for a list of options
    - run `python autorun.py batch -o` to prevent windows from being minimized
    - run `python autorun.py batch -vv` for debug level output
    - run `python autorun.py batch -s` to write results to a json file instead
    of printing them to the console.

## Install manually
1. Prep the mod files for inclusion into the game
    - Select the 'lua' and 'schook' folders
    - Right click -> Send to... -> Compressed (zipped) folder
    - Call the zip 'autorun' (full file name of autorun.zip)
    - Copy autorun.zip into the FAF gamedata folder (usually c:\programdata\faforever\gamedata
2. Create a custom init file that includes the autorun.zip mod when running the game
    - Make a copy of init_faf.lua and call it init_autorun.lua
    - Add 'autorun.zip' to the whitelist
    - Add the following line right before the two mount_mod_sounds lines:
        - mount_dir_with_whitelist(InitFileDir .. '\\\\..\\\\gamedata\\\\', '*.zip', '/')
