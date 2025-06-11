import sys
import platform
from pathlib import Path
from typing import Optional, TextIO
from jsgenerator import generate_examples
from tsdgenerator.utils import run_shell, create_dir, image_exists

scripts_path = Path(__file__).parent.parent / "scripts"

def build_dts(work_path: Path) -> None:
    """Builds the TypeScript declaration files (DTS) by cloning necessary repositories.

    This function checks if the required images exist, and if not, it clones the
    repositories for 'master-mind-wp3' and 'tsd-generator', then builds them.
    
    Args:
        work_path: The path where the work will be done.
    """
    print("BUILDING DTS")
    repositories_path = work_path / "repositories"
    create_dir(repositories_path, remove=False)
    
    project_name = "master-mind-wp3"
    if not image_exists(project_name):
        repo_url = "https://github.com/Proglang-TypeScript/run-time-information-gathering.git"
        clone_path = repositories_path / project_name
        run_shell(f"git clone --depth 1 {repo_url} {clone_path}")
        run_shell(f"{clone_path}/build/build.sh", check=False)
        print("...IGNORING TEST ERRORS")

    project_name = "tsd-generator"
    if not image_exists(project_name):
        repo_url = "https://github.com/Proglang-TypeScript/ts-declaration-file-generator.git"
        clone_path = repositories_path / project_name
        run_shell(f"git clone --depth 1 {repo_url} {clone_path}")
        run_shell(f"{clone_path}/build/build.sh")

def generate_types(package_name: str, extract: bool = True, generate: bool = True, fix: bool = True, work_path: str | Path = "__tsdgenerator__", model_name: str = "gpt-4o-mini", log_file: Optional[TextIO] = sys.stdout, allow_injections: bool = False) -> None:
    """Generates TypeScript declaration files for a given package.

    This function builds the DTS, installs the package, generates examples,
    and creates declaration files based on runtime information.

    Args:
        package_name: The name of the package for which to generate types.
        extract: Flag to indicate whether to extract examples.
        generate: Flag to indicate whether to generate examples.
        fix: Flag to indicate whether to fix issues in the extracted or generated examples.
        work_path: The path where the work will be done.
        model_name: The name of the model to use for generation.
        log_file: The file to log output messages.
        allow_injections: Flag to allow injections during generation.
    """
    work_path = Path(work_path)
    build_dts(work_path)
    
    print("RUNNING DTS")
    template_path = work_path / "template"
    project_path = work_path / "project"

    create_dir(template_path)
    run_shell(f"npm install {package_name}", cwd=template_path)
    
    jsgenerator_path = work_path / "__jsgenerator__"
    generate_examples(package_name, extract=extract, generate=generate, fix=fix, work_path=jsgenerator_path, model_name=model_name, log_file=log_file, allow_injections=allow_injections, no_const=True)

    examples_path = jsgenerator_path / "examples" / package_name
    declarations_path = work_path / "declarations" / package_name
    create_dir(declarations_path)
    for example_path in examples_path.iterdir():
        create_dir(project_path, template_path)
        file_path = project_path / "index.js"
        file_path.write_text(example_path.read_text())

        script_path = scripts_path / ("getRunTimeInformation.linux.sh" if platform.system() == "Linux" else "getRunTimeInformation.sh")
        run_time_path = work_path / "run_time_info_ouput" / "run_time_info.json"
        create_dir(run_time_path.parent)
        run_shell(f"{script_path} {file_path} {run_time_path} 120")

        tsd_path = work_path / "tsd_output"
        create_dir(tsd_path)
        script_path = scripts_path / "generateDeclarationFile.sh"
        run_shell(f"{script_path} {run_time_path} {package_name} {tsd_path}")

        file_path = declarations_path / example_path.name.replace(".js", ".d.ts")
        output_path = tsd_path / package_name / "index.d.ts"
        file_path.write_text(output_path.read_text())