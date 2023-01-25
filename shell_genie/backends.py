import openai


class BaseGenie:
    def __init__(self):
        pass

    def ask(self, wish: str, explain: bool = False):
        raise NotImplementedError

    def post_execute(self, command: str, description: str):
        raise NotImplementedError


class OpenAIGenie(BaseGenie):
    def __init__(self, api_key: str, os_fullname: str, shell: str):
        self.os_fullname = os_fullname
        self.shell = shell
        openai.api_key = api_key

    def _build_prompt(self, wish: str, explain: bool = False, config: dict = None):
        explain_text = ""
        format_text = "Command: <insert_command_here>"

        if explain:
            explain_text = "In addition, provide a detailed description of how the provided command works."
            format_text = "Command: <insert_command_here>\n Description: <insert_description_here>"

        prompt = f"""You're a command line tool that generates CLI commands for the user.
        Format: {format_text}
        Instructions: Write a CLI command that does the following: {wish}. It must work on {self.os_fullname} using {self.shell}. {explain_text}
        """

        return prompt

    def ask(self, wish: str, explain: bool = False):

        prompt = self._build_prompt(wish, explain)

        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=300 if explain else 180,
            temperature=0,
        )
        responses_processed = response.choices[0].text.strip().split("\n")
        command = responses_processed[0].replace("Command:", "").strip()

        description = None
        if explain:
            description = responses_processed[1].split("Description: ")[1]
            print(f"[bold]Description:[/bold] {description}")

        return command, description

    def post_execute(self, command: str):
        pass


class FreeTrialGenie:
    def __init__(self, api_key):
        self.api_key = api_key
