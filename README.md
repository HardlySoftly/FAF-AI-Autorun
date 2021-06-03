# FAF-AI-Autorun

## Pre-requisites
- Python 3 installed (pip too would be helpful)
- FAF installed, and any AI mods you want to use loaded (run a game with them all active to be sure).
- Note: 

## Prep
1. Clone this repo
2. Prep the mod files for inclusion into the game
    - Select the 'lua' and 'schook' folders
    - Right click -> Send to... -> Compressed (zipped) folder
    - Call the zip 'autorun' (full file name of autorun.zip)
    - Copy autorun.zip into the FAF gamedata folder (usually c:\programdata\faforever\gamedata
3. Create a custom init file that includes the autorun.zip mod when running the game
    - Make a copy of init_faf.lua and call it init_autorun.lua
    - Add 'autorun.zip' to the whitelist
    - Add the following line right before the two mount_mod_sounds lines:
        - mount_dir_with_whitelist(InitFileDir .. '\\..\\gamedata\\', '*.zip', '/')

## Usage
1. Edit the run_batch.py file to contain the experiments you want to run
    - You do this by editing the 'exps' variable, its at line 44
2. Customise various configs to taste
    - The 'N' variable sets how many games it will attempt to run simultaneously at any one time
    - The 'maxGameTime' variable sets how long in seconds the game should be before it gets canned and called as a draw
    - The 'obnoxious' variable sets the minimising behaviour (True => minimise open FA windows regularly, False => Don't). Set to False if you want to be able to watch stuff.
3. Execute run_batch.py
    - Open a command prompt (start -> search for 'cmd')
    - Browse to the location of this repo (cd is the change directory command, 'dir' lists stuff in the current directory)
    - If this is your first time, you'll need to install the python dependencies
        - python -m pip install -r requirements.txt
    - Run the following command:
        - python run_batch.py
4. On completion, results from the games will appear in the results.txt file.



