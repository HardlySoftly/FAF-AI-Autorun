import json
import logging
import random
import string
import subprocess
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from _autorun.install import is_installed
from _autorun.util import confirm, get_faforever_dir
from experiments import experiments

try:
    import pygetwindow as gw
except ImportError:
    gw = None

log = logging.getLogger(__name__)


factions = {
    "random": 0,
    "uef": 1,
    "aeon": 2,
    "cybran": 3,
    "seraphim": 4,
}

import os, multiprocessing, psutil

class Affinity:
    def __init__(self):
        self.cpus = {
            i: False for i in range(1,psutil.cpu_count())
        }
        self.pids = {}
        self.lock = multiprocessing.Lock()
    def start(self,pid):
        with self.lock:
            i = random.choice([x for x in self.cpus if not self.cpus[x]])
            self.cpus[i] = True
            self.pids[pid] = i
            psutil.Process(pid).cpu_affinity([i])
    def end(self,pid):
        with self.lock:
            i = self.pids[pid]
            del self.pids[pid]
            self.cpus[i] = False

AFFINITY = Affinity()

def run_batch(args):
    start = time.time()
    faf_dir = get_faforever_dir()
    log_dir = Path.cwd() / "logs"

    if not args.obnoxious and gw is None:
        log.warning("Can't minimize windows because pygetwindow is not installed!")
        return

    if not args.yes and not is_installed(faf_dir):
        if not confirm(
            "Autorun does not appear to be installed, do you want to run the "
            "experiments anyway?"
        ):
            log.debug("Cancelling...")
            return

    if not log_dir.exists():
        log_dir.mkdir()

    if args.dry_run:
        print(len(experiments))
        print(ai_test_arg(experiments[0].ais))
        exit()

    futures = []
    with ThreadPoolExecutor(max_workers=args.num_threads if not args.use_affinity else min(psutil.cpu_count(),args.num_threads)) as executor:
        for experiment in experiments:
            fut = executor.submit(
                run_experiment,
                faf_dir,
                ais=experiment.ais,
                map_name=experiment.map,
                max_time=args.max_game_time,
                log_dir=log_dir,
                use_affinity=args.use_affinity
            )
            futures.append(fut)

            if not args.obnoxious:
                for w in gw.getWindowsWithTitle("Forged Alliance"):
                    if not w.isMinimized:
                        w.minimize()

            time.sleep(10)

    if args.delete_logs:
        for path in log_dir.iterdir():
            if path.is_file() and path.suffix == ".sclog":
                path.unlink()

    results = [fut.result(0) for fut in futures]
    if args.save_results:
        with open("results.json","a") as f:
            for res in results:
                f.write(json.dumps(res))
                f.write("\n")
    else:
        for result in results:
            print(json.dumps(result))
    print(time.time()-start)


def run_experiment(
    faf_dir,
    ais,
    map_name,
    max_time,
    log_dir,
    use_affinity,
    init_name="init_autorun.lua"
):
    bin = faf_dir / "bin"

    log_id = "".join(random.choice(string.hexdigits) for _ in range(8))
    log_name = log_dir / ("log_" + log_id)
    log_file = log_name.with_suffix(".sclog")

    args = [
        bin / "ForgedAlliance.exe",
        "/nobugreport",
        "/nosound",
        "/exitongameover",
        "/init", bin / init_name,
        "/map", map_name,
        "/log", log_name,
        "/maxtime", str(max_time),
        "/aitest", ai_test_arg(ais)
    ]
    log.debug("%s", args)
    proc = subprocess.Popen(args)
    pid = proc.pid
    if use_affinity:
        AFFINITY.start(pid)
    proc.wait()
    if use_affinity:
        AFFINITY.end(pid)
    return get_results(log_file, ais, map_name)


def ai_test_arg(ais):
    return ",".join(
        "{}:{}:{}:{}".format(
            ai.slot,
            ai.name,
            factions[ai.faction.lower()],
            ai.team
        ) for ai in ais
    )


def get_results(log_file,ais,map_name):
    game_results = defaultdict(list)
    winners = []
    with open(log_file) as f:
        for line in f:
            if "AutoRunEndResult|" in line:
                _, army_index, result = line.strip().split("|")
                army_index = int(army_index)
                game_results[army_index].append(result)
                if "victory" in result:
                    winners.append(army_index)

    return {"map": map_name, "ais": ais, "results": game_results, "winners": winners}
