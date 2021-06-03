import threading, subprocess, os, random, time, json

import pygetwindow as gw

N = 8

root = "C:\\ProgramData\\FAForever\\"
cwd = os.getcwd()
logDir = cwd+"\\output\\"
resultPath = cwd+"\\results.txt"
print(cwd)
if not os.path.isdir(logDir):
    os.mkdir(logDir)
if not os.path.isdir(root):
    print("Unable to find FAForever folder!")
    exit()

factionDict = {
    "Random": 0,
    "UEF": 1,
    "Aeon": 2,
    "Cybran": 3,
    "Seraphim": 4,
}
# Minimise windows with "Forged Alliance" in title
obnoxious = True
# In seconds
maxGameTime = 45*60

"""
    Some AI keys for your convenience:
        "rush" - Rush AI
        "sorianrush" - Sorian AI Rush
        "RNGStandard" - RNG Standard AI
        "DalliConstAIKey" - Dalli AI
        "uvesorush" - Uveso Rush AI
        "swarmterror" - Swarm Terror AI
        
    To find the AI key of any given AI, look in the \\lua\\AI\\CustomAIs_v2 directory in the mod files.
"""

dup = 1

exps = [
    # Format: {"map": "<path to map scenario.lua>", "ais": [(<spawn index>, <AI key>, <faction string (see factionDict)>)] }
    {"map": "SCMP_007", "ais": [(1, "rush", "UEF"), (2, "sorianrush", "Random")]},
    {"map": "SCMP_007", "ais": [(2, "rush", "UEF"), (1, "sorianrush", "Random")]},
]

print(len(exps))

random.shuffle(exps)

def get_result(fp,res):
    try:
        with open(fp) as f:
            for line in f:
                if "AutoRunEndResult|" in line:
                    res["results"].append(line[:-1].split("|",1)[1])
                    if "victory" in line:
                        winner_index = int(line.split("|")[1])
                        res["winners"].append(winner_index)
    except Exception as e:
        print("Exception: {}".format(e))
    return res

def run_experiments(exps):
    slots = [None for _ in range(N)]
    done = False
    lock = threading.Lock()
    exp_num = 0
    with open(resultPath,"w") as f:
        # Clean the results file for this batch
        f.write("")
    while not done:
        done = True
        # Kickoff threads
        for i in range(N):
            if slots[i] == None or not slots[i].is_alive():
                if exp_num < len(exps):
                    slots[i] = threading.Thread(target=run_exp,args=(exps[exp_num],lock))
                    slots[i].start()
                    exp_num += 1
                    done = False
                break
            elif slots[i].is_alive():
                done = False
        # Minimise windows
        if obnoxious:
            for w in gw.getWindowsWithTitle("Forged Alliance"):
                if not w.isMinimized:
                    w.minimize()
        # And wait...
        time.sleep(10)

def run_exp(exp,lock):
    # Separate log files with a random ID
    id = "".join([random.choice("1234567890ABCDEF") for _ in range(8)])
    logfile = logDir+"log_"+id
    args = [
        root+"bin\\ForgedAlliance.exe",
        "/nobugreport", "/nosound", "/exitongameover",
        "/init", root+"bin\\init_autorun.lua",
        "/map", exp["map"],
        "/log", logfile,
        "/maxtime", str(maxGameTime),
        "/aitest", mk_test_string(exp["ais"])
    ]
    subprocess.call(args)
    exp["results"] = []
    exp["winners"] = []
    result = get_result(logfile+".sclog",exp)
    os.remove(logfile+".sclog")
    lock.acquire()
    with open(resultPath,"a") as f:
        f.write(json.dumps(result)+"\n")
    lock.release()

def mk_test_string(ais):
    res = ",".join(["{}:{}:{}".format(ai[0],ai[1],factionDict[ai[2]]) for ai in ais])
    return res

start = time.time()
run_experiments(exps)
print("Time taken: {}s".format(round(time.time()-start)))