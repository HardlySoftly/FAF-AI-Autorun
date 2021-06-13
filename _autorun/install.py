import logging
from zipfile import ZipFile

from _autorun.util import confirm, get_faforever_dir, zip_add_dir

log = logging.getLogger(__name__)


def install(args):
    faf_dir = get_faforever_dir()
    gamedata = faf_dir / "gamedata"
    bin = faf_dir / "bin"
    zip_name = "autorun.zip"
    init_name = "init_autorun.lua"

    if not args.yes and is_installed(faf_dir, zip_name, init_name):
        if not confirm(
            "Autorun appears to be installed, do you want to overwrite "
            "the existing installation?"
        ):
            log.debug("Cancelling...")
            return

    # 1. Create the zip
    dest = gamedata / zip_name
    log.info("Creating zip file %s", dest)
    with ZipFile(dest, "w") as f:
        zip_add_dir(f, "lua")
        zip_add_dir(f, "schook")

    # 2. Add our init file that will load the zip
    dest = bin / init_name
    log.info("Copying init file %s", dest)
    with open(bin / "init_faf.lua") as f_in:
        with open(bin / "init_autorun.lua", "w") as f_out:
            f_out.writelines(modify_init(f_in, zip_name))


def is_installed(
    faf_dir=None,
    zip_name="autorun.zip",
    init_name="init_autorun.lua"
):
    if not faf_dir:
        faf_dir = get_faforever_dir()

    gamedata = faf_dir / "gamedata"
    bin = faf_dir / "bin"

    return (
        gamedata / zip_name in gamedata.iterdir() and
        bin / init_name in bin.iterdir()
    )


def modify_init(init_file, zip_name):
    """
    Copy the contents of an existing init file modifying it to make it load our
    zip file.

    :param init_file: Iterator over the lines of the file
    :param zip_name: Name of the file we want to load

    :return: A generator that yeilds the modified contents
    """
    # Use a simple state machine to keep track of where we are in the file
    state = "top"
    for line in init_file:
        line = line.rstrip()
        if state == "top":
            # First search for the whitelist section
            if line.startswith("whitelist"):
                state = "whitelist"
                # Allow the brace to be on the same line
                if "{" in line:
                    state = "whitelist_brace"
        elif state == "whitelist":
            # Find the opening brace
            if "{" in line:
                state = "whitelist_brace"
        elif state == "whitelist_brace":
            # Add our line to the end
            yield f'    "{zip_name}",\n'
            state = "functions"
        elif state == "functions":
            # Find the mount sounds section
            if line.startswith("mount_mod_sounds"):
                # Insert our mount before mount_mod_sounds
                yield (
                    "mount_dir_with_whitelist("
                    # Using a raw string so the backslashes are not escaped
                    r"InitFileDir .. '\\..\\gamedata\\', '*.zip', '/')"
                    "\n"
                )
                state = "done"

        yield line + "\n"


def uninstall(args):
    faf_dir = get_faforever_dir()

    files = (
        faf_dir / "gamedata" / "autorun.zip",
        faf_dir / "bin" / "init_autorun.lua"
    )

    removed_any = False
    for file in files:
        if file.is_file():
            if not args.yes and args.prompt and not confirm(f"Remove {file}?"):
                continue
            log.info("Removing %s", file)
            try:
                file.unlink()
                removed_any = True
            except OSError as e:
                log.warning("%s", e)

    if not removed_any:
        log.warning("Nothing to do...")
