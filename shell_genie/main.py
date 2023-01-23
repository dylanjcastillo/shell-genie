import json
import os
import subprocess
from pathlib import Path

import openai
import typer
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

app = typer.Typer()

APP_NAME = ".shell_genie"


@app.command()
def init():
    try:
        uname = subprocess.check_output(["uname", "-a"]).decode("utf-8")
        if "Darwin" in uname:
            oper_sys = "MacOS"
        elif "Linux" in uname:
            oper_sys = "Linux"
        else:
            raise Exception("uname -a didn't return a recognizable OS.")
    except Exception as e:
        typer.echo(e)
        try:
            subprocess.check_output(["powershell", "Get-ComputerInfo"])
            oper_sys = "Windows"
        except Exception:
            typer.prompt("I couldn't figure out your OS. What OS are you on?")

    if oper_sys == "Linux":
        try:
            shell_distro_str = subprocess.check_output(
                ["grep -E '^(NAME)=' /etc/os-release"]
            )
            shell_version_str = subprocess.check_output(
                ["grep -E '^(NAME)=' /etc/os-release"]
            )
            os_version = (
                shell_distro_str.split("=")[1].strip()
                + " "
                + shell_version_str.split("=")[1].strip()
            )
        except Exception:
            typer.prompt(
                "I couldn't figure out your Linux distro and version. What's your Linux distro and version?"
            )

    if oper_sys == "MacOS":
        try:
            os_version_str = subprocess.check_output(["sw_vers"]).decode("utf-8")
            os_version = os_version_str.split()[3].strip()
        except Exception as e:
            typer.echo(e)
            typer.prompt(
                "I couldn't figure out your MacOS version. What's your MacOS version?"
            )

    if oper_sys == "Linux" or oper_sys == "MacOS":
        try:
            shell_str = os.environ.get("SHELL")
            if "bash" in shell_str:
                shell = "bash"
            elif "zsh" in shell_str:
                shell = "zsh"
            elif "fish" in shell_str:
                shell = "fish"
            else:
                raise Exception
        except Exception as e:
            typer.echo(e)
            typer.prompt("I couldn't figure out your shell. What shell are you using?")

    config = {
        "os": oper_sys,
        "os_version": os_version,
        "shell": shell,
        "current_dir": "pwd",
        "list_files": ["ls", "-a"],
    }

    if oper_sys == "Windows":
        if shell == "powershell":
            config["current_dir"] = "Get-Location"
            config["list_files"] = "Get-ChildItem"
        else:
            config["current_dir"] = "%cd%"
            config["list_files"] = "dir"

    app_dir = typer.get_app_dir(APP_NAME)
    config_path: Path = Path(app_dir) / "config.json"

    typer.echo("Configuration settings: " + str(config))

    config_path.parent.mkdir(parents=True, exist_ok=True)

    if config_path.exists():
        overwrite = typer.confirm("Config file already exists. Overwrite?")
        if not overwrite:
            typer.echo("Exiting...")
            return

    with open(config_path, "w") as f:
        json.dump(config, f)

    typer.echo("Config file saved at " + str(config_path))


@app.command()
def ask(
    wish: str = typer.Argument(..., help="What do you want to do?"),
    explain: bool = False,
):
    explain_text = ""
    format_text = "Format: JSON with one key: 'command'. Make sure to escape the necessary characters."

    if explain:
        explain_text = "In addition, provide a detailed description of how the provided command works."
        format_text = "Return a JSON with two keys'command' and 'description'. Make sure to escape the necessary characters."

    app_dir = typer.get_app_dir(APP_NAME)
    config_path: Path = Path(app_dir) / "config.json"
    with open(config_path, "r") as f:
        config = json.load(f)

    current_dir = subprocess.check_output(config["current_dir"]).decode("utf-8").strip()
    files_in_dir = ", ".join(
        subprocess.check_output(config["list_files"]).decode("utf-8").split("\n")
    )

    prompt = f"""You're a command line tool that generates commands for the user.
    Shell: {config["shell"]}
    OS: {config["os"]}, {config["os_version"]}
    Current directory: {current_dir}
    Files in current directory: {files_in_dir}
    Format: {format_text}
    Instructions: Write a command line command that does the following: {wish}. {explain_text}
    """

    typer.echo("Prompt: " + prompt)

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=256,
        temperature=0,
    )
    json_response = response.choices[0].text.strip()

    json_dict = json.loads(json_response)

    typer.echo("Generated command: " + json_dict["command"])

    if explain:
        typer.echo("Description: " + json_dict["description"])

    execute = typer.confirm("Execute command?")
    if execute:
        os.system(json_dict["command"])


if __name__ == "__main__":
    app()
