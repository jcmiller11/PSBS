from argparse import ArgumentParser

from .project import PSBSProject
from .token import get_token, set_token


def main():
    parser = CLIParser()
    args = parser.parse_args()

    if args.command in ["build", "export", "run"]:
        project = PSBSProject()
        project.build(verify=args.verify)
        if args.command in ["export", "run"]:
            project.export()
        if args.command == "run":
            project.run(editor=args.editor)
    elif args.command == "new":
        PSBSProject.create(
            args.name,
            gist_id=args.gist_id,
            file=args.file,
            new_gist=args.new_gist,
        )
    elif args.command == "token":
        if args.token:
            set_token(args.token)
        else:
            print(get_token(verbose=True))
    elif args.command == "help":
        if args.topic:
            parser.commands[args.topic].print_help()
        else:
            parser.print_help()
    elif args.command is None:
        parser.print_help()


class CLIParser:
    def __init__(self):
        self.parser = ArgumentParser(
            description="PSBS: PuzzleScript Build System", add_help=False
        )
        self.commands = self.add_commands()

    def add_commands(self):
        subparser = self.parser.add_subparsers(
            title="Commands", dest="command"
        )
        commands = {}
        commands_dict = {
            "build": "Build project in current working directory",
            "export": "Build project then export to game",
            "run": "Build project, export, then run in web browser",
            "new": "Create a new project",
            "token": "Check or set GitHub auth token",
            "help": "Display help dialog",
        }
        for command, help_text in commands_dict.items():
            commands[command] = subparser.add_parser(
                command, help=help_text, description=help_text, add_help=False
            )

        commands["run"].add_argument(
            "--editor",
            "-e",
            help="Run project in PuzzleScript editor",
            action="store_true",
        )

        commands["new"].add_argument("name", type=str)
        commands["new"].add_argument(
            "--new-gist",
            "-n",
            dest="new_gist",
            help="Create a new gist for the project",
            action="store_true",
        )
        new_project_flags = commands["new"].add_mutually_exclusive_group()
        new_project_flags.add_argument(
            "--from-gist",
            "-g",
            dest="gist_id",
            help="Build project from existing source at supplied gist",
            type=str,
        )
        new_project_flags.add_argument(
            "--from-file",
            "-f",
            dest="file",
            help="Build project from existing source in supplied file",
            type=str,
        )

        commands["token"].add_argument(
            "token",
            nargs="?",
            help="Your github auth token",
            type=str,
        )

        commands["help"].add_argument(
            "topic",
            nargs="?",
            choices=list(commands.keys()),
            help="Select command you would like help with",
            type=str,
        )

        for verifiable_command in [
            commands["build"],
            commands["run"],
            commands["export"],
        ]:
            verifiable_command.add_argument(
                "--verify",
                "-v",
                help="Verify compilation and display PuzzleScript console output",
                action="store_true",
            )
        return commands

    def parse_args(self):
        return self.parser.parse_args()

    def print_help(self):
        self.parser.print_help()
