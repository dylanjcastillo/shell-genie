import openai
import requests


class BaseGenie:
    def __init__(self):
        pass

    def ask(self, wish: str, explain: bool = False):
        raise NotImplementedError

    def post_execute(
        self, wish: str, explain: bool, command: str, description: str, feedback: bool
    ):
        pass


class OpenAIGenie(BaseGenie):
    def __init__(self, api_key: str, os_fullname: str, shell: str):
        self.os_fullname = os_fullname
        self.shell = shell
        openai.api_key = api_key

    def _build_prompt(self, wish: str, explain: bool = False):
        explain_text = ""
        format_text = "Command: <insert_command_here>"

        if explain:
            explain_text = (
                "Also, provide a detailed description of how the command works."
            )
            format_text += "\nDescription: <insert_description_here>\nThe description should be in the same language the user is using."
        format_text += "\nDon't enclose the command with extra quotes or backticks."

        prompt_list = [
            f"Instructions: Write a CLI command that does the following: {wish}. Make sure the command is correct and works on {self.os_fullname} using {self.shell}. {explain_text}",
            "Format:",
            format_text,
            "Make sure you use the format exactly as it is shown above.",
        ]
        prompt = "\n\n".join(prompt_list)
        return prompt

    def ask(self, wish: str, explain: bool = False):
        prompt = self._build_prompt(wish, explain)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You're a command line tool that generates CLI commands for the user.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=300 if explain else 180,
            temperature=0,
        )
        responses_processed = (
            response["choices"][0]["message"]["content"].strip().split("\n")
        )
        responses_processed = [
            x.strip() for x in responses_processed if len(x.strip()) > 0
        ]
        command = responses_processed[0].replace("Command:", "").strip()

        if command[0] == command[-1] and command[0] in ["'", '"', "`"]:
            command = command[1:-1]

        description = None
        if explain:
            description = responses_processed[1].split("Description: ")[1]

        return command, description


class FreeTrialGenie(BaseGenie):
    def __init__(self, os_fullname: str, shell: str):
        self.url = "https://shell-genie.dylancastillo.co"
        self.os_fullname = os_fullname
        self.shell = shell

    def ask(self, wish: str, explain: bool):
        response = requests.post(
            url=self.url + "/ask",
            json={
                "wish": wish,
                "explain": explain,
                "os_fullname": self.os_fullname,
                "shell": self.shell,
            },
        )

        if response.status_code != 200:
            raise ValueError("Error in response.")

        command = response.json()["command"]
        description = response.json()["description"]
        return command, description

    def post_execute(
        self, wish: str, explain: bool, command: str, description: str, feedback: bool
    ):
        requests.post(
            url=self.url + "/post_execute",
            json={
                "wish": wish,
                "explain": explain,
                "os_fullname": self.os_fullname,
                "shell": self.shell,
                "command": command,
                "description": description,
                "correct": feedback,
            },
        )
        return
