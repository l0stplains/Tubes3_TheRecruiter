import argparse
import importlib
import sys
from pathlib import Path

def discover_drivers():
    drivers_path = Path(__file__).parent / "drivers"
    if not drivers_path.exists():
        sys.exit(f"Error: drivers folder not found at {drivers_path!r}")
    modules = []
    for file in sorted(drivers_path.glob("*.py")):
        name = file.stem
        if name == "__init__":
            continue
        modules.append(name)
    if not modules:
        sys.exit("Error: no drivers found in drivers/")
    return modules

def parse_args(available_drivers):
    parser = argparse.ArgumentParser(
        prog="therecruiter",
        description="Mau nyari pekerja paling cocok sama kriteriamu (nyari pasangan yang cocok soon)."
    )
    parser.add_argument(
        "-d", "--driver",
        choices=available_drivers,
        default=available_drivers[0], # it should be __main__
        help="Which driver to run (default: %(default)s)"
    )
    return parser.parse_args()

def main():
    drivers = discover_drivers()
    args = parse_args(drivers)
    driver = args.driver

    pkg = __package__ or "src"  
    module_name = f"{pkg}.drivers.{driver}"

    print("Running on Python", sys.version) # version debug

    try:
        driver = importlib.import_module(module_name)
    except ImportError as e:
        sys.exit(f"Error: could not load driver '{driver}': {e}")

    if not hasattr(driver, "run"):
        sys.exit(f"Error: driver module '{module_name}' has no run() function")
    driver.run()

if __name__ == "__main__":
    main()

