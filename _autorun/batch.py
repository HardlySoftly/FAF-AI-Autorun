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


def run_batch(args):
    faf_dir = get_faforever_dir()
    log_dir = Path("logs")

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

    futures = []
    with ThreadPoolExecutor(max_workers=args.num_threads) as executor:
        for experiment in experiments:
            fut = executor.submit(
                run_experiment,
                faf_dir,
                ais=experiment.ais,
                map_name=experiment.map,
                max_time=args.max_game_time,
                log_dir=log_dir
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
        with open("results.json") as f:
            json.dump(results, f)
    else:
        for i, (experiment, result) in enumerate(zip(experiments, results)):
            i += 1
            ais = sorted(experiment.ais, key=lambda ai: ai.slot)
            print("Experiment", i, " vs ".join(ai.name for ai in ais))
            for army, results in sorted(result.items(), key=lambda x: x[0]):
                print("   ", army, results)
            print()


def run_experiment(
    faf_dir,
    ais,
    map_name,
    max_time,
    log_dir,
    init_name="init_autorun.lua"
):
    bin = faf_dir / "bin"

    log_id = "".join(random.choice(string.hexdigits) for _ in range(8))
    log_name = log_dir / "log_" + log_id
    log_file = log_name.with_suffix(".sclog")

    subprocess.run([
        bin / "ForgedAlliance.exe",
        "/nobugreport",
        "/nosound",
        "/exitongameover",
        "/init", bin / init_name,
        "/map", map_name,
        "/log", log_name,
        "/maxtime", str(max_time),
        "/aitest", ai_test_arg(ais)
    ])

    return get_results(log_file)


def ai_test_arg(ais):
    return ",".join(
        "{}:{}:{}".format(
            ai.slot,
            ai.name,
            factions[ai.faction.lower()]
        ) for ai in ais
    )


def get_results(log_file):
    game_results = defaultdict(set)
    with open(log_file) as f:
        for line in f:
            if "AutoRunEndResult|" in line:
                _, army_index, result = line.strip().split("|")
                game_results[army_index].add(result)

    return game_results
