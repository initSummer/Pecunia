# © Dream Hunter Studio 2024.
# All rights reserved.
#
# This software, including all its code, documentation, images, and related materials, is the exclusive property of the
# program author. Unauthorized copying, modification, distribution, or commercial use of any part of this software is
# strictly prohibited without prior written consent from the program author. The software is provided "as is," without
# any express or implied warranties, including but not limited to implied warranties of merchantability or fitness for a
# particular purpose. The program author assumes no liability for any direct or indirect damages arising from the use or
# inability to use the software.
#
# Description : Project Builder
#
# Reversion   :
#   Rev.        Date        Designer    Description
#   1.0         2025-04-19  summer      Initial version
#

from datetime import datetime
import os
import re
import shutil
import subprocess
import time
from turtledemo.penrose import start

from src.util import *

prog_name = f"{PROJECT_NAME}_cli"

def change_info():
    info_file_path = "src/util/util_consts.py"

    build_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(info_file_path, 'r', encoding="utf-8") as file:
        file_data = file.read()

    file_data = re.sub(f'PROJECT_BUILD_TIME = ".*"', f'PROJECT_BUILD_TIME = "{build_time}"', file_data)

    with open(info_file_path, 'w', encoding="utf-8") as file:
        file.write(file_data)


def pack():
    nuitka_executable = shutil.which("nuitka")
    if nuitka_executable is None:
        print("Error, Cannot Find nuitka, Pack Failed")
        return
    print(f"Found nuitka: {nuitka_executable}")
    print(f"Nuitka version: ")
    subprocess.run([nuitka_executable, "--version"], check=True)
    nuitka_command = [
        nuitka_executable,
        "--jobs=16",
        "--standalone",
        "--onefile",
        "--lto=yes",
        "--follow-imports",
        # "--windows-console-mode=enable",
        f'--windows-icon-from-ico={os.path.join("resource", "images", "icon_0.ico")}',
        "--enable-plugin=tk-inter",
        f"src/{prog_name}.py"
    ]
    subprocess.run(nuitka_command, check=True)

    print("Pack Done, Cleaning")
    for path in [f"{prog_name}.build", f"{prog_name}.dist", f"{prog_name}.onefile-build",
                 "nuitka-crash-report.xml"]:
        if os.path.exists(path):
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)


def main():
    start_time = time.time()

    change_info()
    pack()

    end_time = time.time()
    print(f"Pack done, runtime: {end_time - start_time:4}s")


if __name__ == "__main__":
    main()
