from argparse import ArgumentParser

from .project import PSBSProject
from .token import get_token, set_token


def _main():
    _CLIParser().parse_args()


class _CLIParser:
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
        commands["build"].set_defaults(func=self.build_project)
        commands["export"].set_defaults(func=self.export_project)
        commands["run"].set_defaults(func=self.run_project)
        commands["new"].set_defaults(func=self.new_project)
        commands["token"].set_defaults(func=self.token)
        commands["help"].set_defaults(func=self.print_help)
        self.parser.set_defaults(func=self.print_help, topic=None)

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
        args = self.parser.parse_args()
        args.func(args)

    def build_project(self, args):
        project = PSBSProject()
        project.build(verify=args.verify)
        return project

    def export_project(self, args):
        project = self.build_project(args)
        project.export()
        return project

    def run_project(self, args):
        project = self.export_project(args)
        project.run()

    def new_project(self, args):
        PSBSProject.create(
            args.name,
            gist_id=args.gist_id,
            file=args.file,
            new_gist=args.new_gist,
        )

    def token(self, args):
        if args.token:
            set_token(args.token)
        else:
            print(get_token(verbose=True))

    def print_help(self, args):
        if args.topic:
            self.commands[args.topic].print_help()
        else:
            self.parser.print_help()
