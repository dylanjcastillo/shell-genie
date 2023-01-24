import json
import os
import re
import subprocess
from pathlib import Path

import openai
import typer
from dotenv import load_dotenv
from rich.prompt import Prompt

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
            computer_info = subprocess.check_output(
                ["powershell", "Get-ComputerInfo"]
            ).decode("utf-8")
            oper_sys = "Windows"
        except Exception:
            oper_sys = typer.prompt(
                "I couldn't figure out your OS. What OS are you on?"
            )

    if oper_sys == "Windows":
        try:
            match = re.search(r"WindowsProductName\s*:\s*(.+)", computer_info)
            if match:
                os_version = match.group(1).replace("Windows", "").strip()
        except Exception:
            os_version = typer.prompt(
                "I couldn't figure out your Windows version. What's your Windows version?"
            )

        shell = Prompt.ask(
            "What shell are you using?",
            choices=["cmd", "powershell", "git bash", "WSL"],
        )

    if oper_sys == "Linux":
        try:
            shell_distro_str = (
                subprocess.check_output(["cat", "/etc/os-release"])
                .decode("utf-8")
                .split("\n")
            )
            distro = (
                [line for line in shell_distro_str if line.startswith("NAME")][0]
                .split("=")[1]
                .replace('"', "")
                .strip()
            )
            version = (
                [line for line in shell_distro_str if line.startswith("VERSION")][0]
                .split("=")[1]
                .replace('"', "")
                .strip()
            )
            os_version = distro + " " + version
        except Exception as e:
            typer.echo(e)
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
    }

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
    format_text = "Command: <insert_command_here>"

    if explain:
        explain_text = "In addition, provide a detailed description of how the provided command works."
        format_text = (
            "Command: <insert_command_here>\n Description: <insert_description_here>"
        )

    app_dir = typer.get_app_dir(APP_NAME)
    config_path: Path = Path(app_dir) / "config.json"
    with open(config_path, "r") as f:
        config = json.load(f)

    prompt = f"""You're a command line tool that generates commands for the user.
    Shell: {config["shell"]}
    Format: {format_text}
    Instructions: Write a command line command that does the following: {wish}. It must work for {config["os"]}, {config["os_version"]}. {explain_text}
    """

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=200,
        temperature=0,
    )
    responses_processed = response.choices[0].text.strip().split("\n")
    command = responses_processed[0].replace("Command:", "").strip()
    typer.echo("Command: " + command)

    if explain:
        description = responses_processed[1].split("Description: ")[1]
        typer.echo("Description: " + description)

    execute = typer.confirm("Execute command?")
    if execute:
        os.system(command)


if __name__ == "__main__":
    app()
