from pipes import Template
import click
import os
import shutil
from string import Template
from pathlib import  Path, PurePath
from sys import platform
from subprocess import call

ONE_DIR_UP = ".."
TEMPLATE_PATH = "project_template_minimal"
TEMPLATE_SRC_NAME = "main.c"
TEMPLATE_CMAKE_IMPORT_NAME = "pico_sdk_import.cmake"
TEMPLATE_CMAKE_NAME = "CMakeLists.txt"
LINUX_MKDIR = "mkdir {}"
LINUX_CMAKE_COMMAND_GEN = "cmake {} -B {}"
LINUX_MAKE_COMMAND_COMPILE = "cmake --build {}"
LINUX_FLASH_COMMAND = "sudo {} load -v -x {} -t uf2"
SDK_DIR = "pico-sdk"

def is_input_path_valid(path : str) -> bool:
    _path = Path(path)
    if _path.is_dir():
        return True
    else:
        print("path is not valid")
        return False

def create_project_folder(path: str, project_name : str) -> str:
    _path = Path().cwd().joinpath(path, project_name)
    
    if _path.is_dir():
        _user_prompt = input("project exists. Type YES to remove existing project and create a new one: ")
        
        if _user_prompt == "YES":
            shutil.rmtree(_path)
        else:
            return None

    os.mkdir(_path)
    return _path

def copy_template_file(dst_path: str, filename : str):
    _src_path = Path().cwd().joinpath(ONE_DIR_UP, TEMPLATE_PATH, filename)
    shutil.copy2(_src_path, dst_path)
    pass

def generate_cmake_file(dst_path: str,
                        project_name: str,
                        usb_stdio_enable : bool,
                        uart_stdio_enable : bool) -> bool:

    _src_path = Path().cwd().joinpath(ONE_DIR_UP, TEMPLATE_PATH, TEMPLATE_CMAKE_NAME)
    cmake_template = ""
    _usb_stdio_enable = 0
    _uart_stdio_enable = 0
    
    with open(_src_path, mode='r') as cmake_file:
        cmake_template = cmake_file.read()

    
    if cmake_template is not None:
        
        if usb_stdio_enable:
            _usb_stdio_enable = 1
    
        if uart_stdio_enable:
            _uart_stdio_enable = 1
        
        generated_cmake = Template(cmake_template).substitute(
            project_name = project_name,
            enable_usb_stdio = _usb_stdio_enable,
            enable_uart_stdio = _uart_stdio_enable)
        
        
        new_cmake_path = Path().cwd().joinpath(dst_path, TEMPLATE_CMAKE_NAME)
        
        with open(new_cmake_path, mode="w") as new_cmake_file:
            new_cmake_file.write(generated_cmake)
            return True
    else:
        return False

def create_new_project(dst : str,
                       project_name: str,
                       usb_stdio_enable : bool,
                       uart_stdio_enable : bool) -> bool:
    ret_val = False
    
    if is_input_path_valid(dst):
        _path = create_project_folder(dst, project_name)
        
        if is_input_path_valid(_path):
            copy_template_file(_path, TEMPLATE_SRC_NAME)
            copy_template_file(_path, TEMPLATE_CMAKE_IMPORT_NAME)
            if generate_cmake_file(_path,
                                   project_name,
                                   usb_stdio_enable,
                                   uart_stdio_enable):
                ret_val = True;
    return ret_val

def compile_project(project_path) -> bool:
    #remove the build folder if it exists
    _path_build = Path().cwd().joinpath(project_path, "build")
    _path_cmake = Path(project_path)
    _path_sdk = Path().cwd().joinpath(ONE_DIR_UP, SDK_DIR)
    
    print(_path_sdk)
    if _path_build.is_dir():
        shutil.rmtree(_path_build)
    
    os.environ["PICO_SDK_PATH"] = str(_path_sdk)
    
    if call(LINUX_MKDIR.format(_path_build), shell=True) != 0:
        return False
    
    if call(LINUX_CMAKE_COMMAND_GEN.format(_path_cmake, _path_build), shell= True) != 0:
        return False
    
    if call(LINUX_MAKE_COMMAND_COMPILE.format(_path_build), shell= True) != 0:
        return False
    
    return True
    
def flash_firmware(project_path : str) -> bool:
    _path_build = Path().cwd().joinpath(project_path, "build")
    _path_picotool = Path().cwd().joinpath(ONE_DIR_UP, "flash_tool", "picotool")
    
    _path_firmware = list(_path_build.glob("*.uf2"))
    
    if len(_path_firmware) == 1:
        #one firmware exists, so it must be ok
        call(LINUX_FLASH_COMMAND.format(_path_picotool, _path_firmware[0]),
             shell=True)
    else:
        pass

@click.group()
def build_cli():
    click.echo()
    click.echo()
    click.echo("**********************************************")
    click.echo("* Welcome to Raspberry Pi Pico toolchains")
    click.echo("**********************************************")
    
@click.command()
@click.option('--path', required=True, help="path to project folder")
@click.option('--project', required=True, help="name of the project")
@click.option('--std_usb',
              default=False,
              help="enable std output to usb comport")
@click.option('--std_uart',
              default=False,
              help="enable std output to uart")

def create(project, path, std_usb, std_uart):    
    click.echo("creating new project...")
    if std_usb:
        click.echo("enable std output to usb comport")
    if std_uart:
        click.echo("enable std output to uart")
    
    
    if create_new_project(path, project, std_usb, std_uart):
        click.echo("create project success")
    else:
        click.echo("create project fail")

@click.command()
@click.option('-p', '--path', required=True, help="path to project folder")
def build(path):
    click.echo("project path: {}".format(path))
    click.echo("building the project...")
    compile_project(path)
    
@click.command()
@click.option('-p', '--path', required=True, help="path to project folder")
def flash(path):
    click.echo("flashing the firmware...")
    flash_firmware(path);

build_cli.add_command(create)
build_cli.add_command(build)
build_cli.add_command(flash)

if __name__ == '__main__':
    if platform == "linux" or platform == "linux2":
        build_cli()
    else:
        click.echo("this tool supports currently only Linux")