import sys
import os
import traceback
import shutil
from sys import platform

SKIP_IMPORT_DIR = ["test"]
CURRENT_DIR = os.getcwd()
APP_DIR = os.path.join(CURRENT_DIR, "app")
EXEC_DIR = CURRENT_DIR
if not os.path.exists(EXEC_DIR):
    os.mkdir(EXEC_DIR)
APP_NAME = "WarningSystem"


def get_current_dir_hidden_imports():
    current_dir = os.getcwd()
    hidden_import = ""

    for root, dirs, files in os.walk(current_dir):
        if root == current_dir:
            continue
        if root.split(os.path.sep)[-1] in SKIP_IMPORT_DIR:
            continue
        for f in files:
            if f[-3:] == ".py":
                file_dir = os.path.join(root, f)
                file_dir = file_dir.replace(current_dir, "")
                file_dir = file_dir.replace(os.path.sep, ".")
                hidden_import += "--hidden-import " + file_dir[1:-3] + " "

    return hidden_import


def remove_pyinstaller_temp_file(currentDir):
    if os.path.exists(os.path.join(currentDir, "build")):
        shutil.rmtree(os.path.join(currentDir, "build"))
    if os.path.exists(os.path.join(currentDir, "dist")):
        shutil.rmtree(os.path.join(currentDir, "dist"))
    if os.path.exists(os.path.join(currentDir, "exec.spec")):
        os.remove(os.path.join(currentDir, "exec.spec"))


def copytree(src, dst, symlinks=False, ignore=None):
    """

    """
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def build_main(project_dir):
    try:
        # clean previous folder
        if os.path.exists(os.path.join(EXEC_DIR, APP_NAME)):
            shutil.rmtree(os.path.join(EXEC_DIR, APP_NAME))

        os.chdir(project_dir)
        hidden_imports = get_current_dir_hidden_imports()
        extra_hidden_imports = [
            "uvicorn.protocols.websockets.auto",
            "uvicorn.lifespan",
            "uvicorn.lifespan.on",
            "databases",
            "databases.backends",
            "databases.backends.sqlite",
            "main"
        ]

        for lib in extra_hidden_imports:
            hidden_imports += "--hidden-import " + lib + " "

        sys_command = "python -m PyInstaller " + \
            "--hidden-import pkg_resources.py2_warn " + hidden_imports + " exec.py "
        os.system(sys_command)

        dist_dir = os.path.join(project_dir, "dist", "exec")

        if platform.startswith("win32"):
            exe_file_name = "exec.exe"
        else:
            exe_file_name = "exec"
        if not os.path.exists(os.path.join(dist_dir, exe_file_name)):
            print("Build executable file occur error.")
            print(os.path.join(dist_dir, exe_file_name))
            raise RuntimeError("Build executable file occur error.")

        # if not os.path.exists(os.path.join(dist_dir, "templates")):
        #     os.mkdir(os.path.join(dist_dir, "templates"))
        #     copytree(os.path.join(project_dir, "templates"),
        #              os.path.join(dist_dir, "templates"))

        shutil.move(dist_dir, EXEC_DIR)
        os.rename(os.path.join(EXEC_DIR, "exec"),
                  os.path.join(EXEC_DIR, APP_NAME))
        if platform.startswith("win32"):
            os.rename(os.path.join(EXEC_DIR, APP_NAME,"exec.exe"),
                    os.path.join(EXEC_DIR, APP_NAME,"WarningSystem.exe"))
        else:
            os.rename(os.path.join(EXEC_DIR, APP_NAME,"exec"),
                    os.path.join(EXEC_DIR, APP_NAME,"WarningSystem"))
        with open(os.path.join(EXEC_DIR,"WarningSystem","start_warning.bat"),"w")as f:
            f.write('if "%1"=="hide" goto CmdBegin\nstart mshta vbscript:createobject("wscript.shell").run("""%~0"" hide",0)(window.close)&&exit\n:CmdBegin\nset filepath=%~dp0.\n%filepath%\WarningSystem.exe')
    except:
        traceback.print_exc()
    finally:
        remove_pyinstaller_temp_file(project_dir)


if __name__ == "__main__":
    python_version = sys.version_info
    print(f"Build project with python: {python_version}")
    build_main(APP_DIR)
