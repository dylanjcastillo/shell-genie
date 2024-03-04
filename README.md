**I am no longer maintaining this repository. Please consider using a tool such as [shellGPT](https://github.com/TheR1D/shell_gpt)**

# 🧞‍♂️ Shell Genie

_Your wishes are my commands._

Shell Genie is a command-line tool that lets you interact with the terminal in plain English. You ask the genie what you want to do and it will give you the command you need.

## Installation

The recommended way to install Shell Genie is using [pipx](https://pypa.github.io/pipx/):

1. Install Python 3.10 or higher.
2. Install [pipx](https://github.com/pypa/pipx#install-pipx).
3. Install Shell Genie: `pipx install shell-genie`

Alternatively, you can install it using pip:

1. Install Python 3.10 or higher.
2. Create a virtual environment in your preferred location: `python -m venv .venv`
3. Activate the virtual environment: `source .venv/bin/activate`
4. Install Shell Genie: `pip install shell-genie`

## How to use

1. First, you need to initialize the tool by running the following command:

   ```shell
   shell-genie init
   ```

   This will prompt you to select a backend (either `openai-gpt3.5-turbo` or `free-genie`) and provide any additional information that is required (e.g. your own [OpenAI API](https://openai.com/api/) key for `openai-gpt3.5-turbo`).

   The `free-genie` backend is free to use. I'm hosting it, and as you can imagine I'm not a big corporation with unlimited money, so there's no guarantee that it will be available at all times. My goal is to generate a dataset of commands to fine-tune a model later on (this is mentioned during the initialization process).

2. Once you have initialized the tool, you can start asking the genie what you want to do. For example, you may ask it to find all the `json` files in the current directory that are larger than 1MB:

   ```shell
   shell-genie ask "find all json files in the current directory that are larger than 1MB"
   ```

   You'll see an output similar to this:

   ```shell
   Command: find . -name "*.json" -size +1M
   Do you want to run this command? [y/n]:
   ```

   If you have questions about how the command works, you can ask the genie to explain it:

   ```shell
   shell-genie ask "find all json files in the current directory that are larger than 1MB" --explain
   ```

   And you'll see an output similar to this:

   ```shell
   Command: find . -name "*.json" -size +1M
   Description: This command will search the current directory for all... (shortened for brevity)
   Do you want to run the command? [y/n]:
   ```

   You can ask for commands in English or other languages, and the genie will try to provide you with a explanation in the same language.

3. Run the command if you want to. If you're using `free-genie`, and you want to help improve the tool, you can provide feedback after you've run the command.

   You can use `shell-genie ask --no-execute` to inhibit the "Run this command" question, like this:

   ```shell
   shell-genie ask --no-execute "list open files for process"
   ```
   And you'll see an output similar to this:

   ```shell
   Command: lsof -p <process_id>
   ```

### Using an alias

If you find that writing `shell-genie ask` is too verbose, you can create an alias for the tool:

```shell
echo "alias please='shell-genie ask'" >> ~/.bashrc
source ~/.bashrc
```

And now you can ask the genie using `please`:

```shell
please "find all json files in the current directory that are larger than 1MB"
```

## Examples

Here are two short videos showing how to use the tool:

- [Ask genie for a command](https://youtu.be/QM-fwgnGzDc)
- [Ask genie to explain a command](https://youtu.be/Qi3w3abI4oE)

## Limitations

As you can imagine, not all the commands provided by the genie work as expected. If you request them, you might receive commands that could wreck your OS (e.g., rm -rf /). So, don't run commands if you don't understand their functions. If you choose to execute them despite not understanding them, do so at your own risk.

## License

This project is licensed under the terms of the MIT license.
