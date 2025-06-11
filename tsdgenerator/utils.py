import shutil
import subprocess
from pathlib import Path
from typing import Any, Optional, List

def run_shell(command, shell=True, check=True, **kwargs) -> Any:
    """Runs a shell command and captures its output.

    Args:
        command (str): The command to run.
        shell (bool, optional): Whether to use the shell. Defaults to True.
        check (bool, optional): Whether to check for errors. Defaults to True.
    """
    print(f"RUNNING: {command}")
    return subprocess.run(command, shell=shell, check=check, **kwargs)

def create_dir(dir_path: Path, src_path: Optional[Path] = None, remove: bool = True) -> None:
    """Creates a directory, optionally copying from a source path.

    Args:
        dir_path (Path): The path to the directory to create.
        src_path (Optional[Path], optional): The source path to copy from. Defaults to None.
        remove (bool, optional): Whether to remove the existing directory. Defaults to True.
    """
    if remove:
        shutil.rmtree(dir_path, ignore_errors=True)
    if src_path is None:
        dir_path.mkdir(parents=True, exist_ok=True)
    else:
        shutil.copytree(src_path, dir_path, dirs_exist_ok=True)
    
def image_exists(image_name):
    result = run_shell(f"docker images -q {image_name}", capture_output=True, text=True)
    return result.stdout.strip() != ""  # If there's output, the image exists