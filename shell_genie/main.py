import json
import os
import subprocess
from pathlib import Path

import pyperclip
import typer
from rich import print
from rich.prompt import Confirm, Prompt

from .utils import get_backend, get_os_info

APP_NAME = ".shell_genie"
app = typer.Typer()


@app.command()
def init():

    backend = Prompt.ask("Select backend:", choices=["openai-gpt3", "free-genie"])
    additional_params = {}

    if backend == "openai-gpt3":
        additional_params["openai_api_key"] = Prompt.ask("Enter a OpenAI API key")

    if backend == "free-genie":
        print(
            "[yellow]Note that this server will store the requested command, OS, and shell version to improve the model. Also, I cannot guarantee that the server will be up and running 24/7.[/yellow]"
        )
        if not Confirm.ask("Do you want to continue?"):
            return
        additional_params["training-feedback"] = Confirm.ask(
            "Do you want to provide feedback about the generated commands to improve the models?"
        )
    os_family, os_fullname = get_os_info()

    if os_family:
        if not Confirm.ask(f"Is your OS {os_fullname}?"):
            os_fullname = Prompt.ask("What is your OS and version? (e.g. MacOS 13.1)")
    else:
        os_fullname = Prompt.ask("What is your OS and version? (e.g. MacOS 13.1)")

    if os_family == "Windows":
        shell = Prompt.ask(
            "What shell are you using?",
            choices=["cmd", "powershell"],
        )

    if os_family in ("Linux", "MacOS"):
        shell_str = os.environ.get("SHELL") or ""
        if "bash" in shell_str:
            shell = "bash"
        elif "zsh" in shell_str:
            shell = "zsh"
        elif "fish" in shell_str:
            shell = "fish"
        else:
            typer.prompt("What shell are you using?")

    config = {
        "backend": backend,
        "os": os_family,
        "os_fullname": os_fullname,
        "shell": shell,
    } | additional_params

    app_dir = typer.get_app_dir(APP_NAME)
    config_path: Path = Path(app_dir) / "config.json"

    print("The following configuration will be saved:")
    print(config)

    config_path.parent.mkdir(parents=True, exist_ok=True)

    if config_path.exists():
        overwrite = Confirm.ask(
            "A config file already exists. Do you want to overwrite it?"
        )
        if not overwrite:
            print("Did not overwrite config file.")
            return

    with open(config_path, "w") as f:
        json.dump(config, f)

    print(f"[bold green]Config file saved at {config_path}[/bold green]")


@app.command()
def ask(
    wish: str = typer.Argument(..., help="What do you want to do?"),
    explain: bool = False,
):
    app_dir = typer.get_app_dir(APP_NAME)
    config_path = Path(app_dir) / "config.json"

    with open(config_path, "r") as f:
        config = json.load(f)

    genie = get_backend(**config)
    try:
        command, description = genie.ask(wish, explain)
    except Exception as e:
        print(f"[red]Error: {e}[/red]")
        return

    print(f"[bold]Command:[/bold] [yellow]{command}[/yellow]")

    if description:
        print(f"[bold]Description:[/bold] {description}")

    if config["os"] == "Windows" and config["shell"] == "powershell":
        pyperclip.copy(command)
        print("[green]Command copied to clipboard.[/green]")
    else:
        execute = Confirm.ask("Do you want to run the command?")
        if execute:
            subprocess.run(command, shell=True)
            feedback = False
            try:
                if config["training-feedback"]:
                    feedback = Confirm.ask("Did the command work?")
            except KeyError:
                pass
            genie.post_execute(
                wish=wish,
                explain=explain,
                command=command,
                description=description,
                feedback=feedback,
            )


if __name__ == "__main__":
    app()
