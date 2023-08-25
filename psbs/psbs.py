"""
PSBS CLI Module

This base module provides a command-line interface (CLI) for the PuzzleScript
Build System (PSBS). It allows users to perform various actions related to
building, exporting, and running PuzzleScript projects, as well as managing
authentication tokens.

You probably shouldn't be importing this one if you're using PSBS as an API.

Classes:
    _CLIParser: A class that handles parsing command-line arguments and
    executing associated functions.

Functions:
    _main: Entry point for the PSBS CLI application.
"""

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
        self.commands = self.__add_commands()

    def __add_commands(self):
        """
        Private method.
        Add subcommands to the command-line parser and set their associated
        functions.

        Returns:
            dict: A dictionary containing the subcommands and their associated
            argument parsers.
        """
        # Create a subparser for handling subcommands
        subparser = self.parser.add_subparsers(title="Commands", dest="command")
        # Initialize a dictionary to store subcommands and their associated parsers.
        commands = {}

        # Define the descriptions for each subcommand.
        commands_dict = {
            "build": "Build project in current working directory",
            "export": "Build project then export to game",
            "run": "Build project, export, then run in web browser",
            "new": "Create a new project",
            "token": "Check or set GitHub auth token",
            "help": "Display help dialog",
        }

        # Iterate through each subcommand to create parsers.
        for command, help_text in commands_dict.items():
            # Add a parser for the subcommand with its help description.
            commands[command] = subparser.add_parser(
                command, help=help_text, description=help_text, add_help=False
            )

        # Set default functions for each subcommand.
        commands["build"].set_defaults(func=self.build_project)
        commands["export"].set_defaults(func=self.export_project)
        commands["run"].set_defaults(func=self.run_project)
        commands["new"].set_defaults(func=self.new_project)
        commands["token"].set_defaults(func=self.token)
        commands["help"].set_defaults(func=self.print_help)

        # Set the default function for no given command.
        self.parser.set_defaults(func=self.print_help, topic=None)

        # Add arguments specific to the "run" subcommand.
        commands["run"].add_argument(
            "--editor",
            "-e",
            help="Run project in PuzzleScript editor",
            action="store_true",
        )

        # Add arguments specific to the "new" subcommand.
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

        # Add arguments specific to the "token" subcommand.
        commands["token"].add_argument(
            "token",
            nargs="?",
            help="Your GitHub auth token",
            type=str,
        )

        # Add arguments specific to the "help" subcommand.
        commands["help"].add_argument(
            "topic",
            nargs="?",
            choices=list(commands.keys()),
            help="Select command you would like help with",
            type=str,
        )

        # Add the "--verify" option to relevant subcommands.
        for verifiable_command in [
            commands["build"],
            commands["run"],
            commands["export"],
        ]:
            verifiable_command.add_argument(
                "--verify",
                "-v",
                help="Verify compilation and show PuzzleScript console output",
                action="store_true",
            )

        # Return the dictionary containing subcommands and their parsers.
        return commands

    def parse_args(self):
        """
        Parse command-line arguments and execute the associated function.

        This method uses the ArgumentParser object defined for the class to
        parse command-line arguments. It then calls the associated function
        corresponding to the parsed command. The parsed arguments are passed
        as a parameter to the associated function.

        Returns:
            None
        """
        args = self.parser.parse_args()
        args.func(args)

    def build_project(self, args):
        """
        Build the project and return the project object.

        Args:
            args: Parsed command-line arguments.

        Returns:
            PSBSProject: The project object after building.
        """
        project = PSBSProject()
        project.build(verify=args.verify)
        return project

    def export_project(self, args):
        """
        Build the project and export it, returning the project object.

        Args:
            args: Parsed command-line arguments.

        Returns:
            PSBSProject: The project object after building and exporting.
        """
        project = self.build_project(args)
        project.export()
        return project

    def run_project(self, args):
        """
        Build, export, and run the project in a web browser.

        Args:
            args: Parsed command-line arguments.

        Returns:
            None
        """
        project = self.export_project(args)
        project.run()

    def new_project(self, args):
        """
        Create a new project using provided arguments.

        Args:
            args: Parsed command-line arguments.

        Returns:
            None
        """
        PSBSProject.create(
            args.name,
            gist_id=args.gist_id,
            file=args.file,
            new_gist=args.new_gist,
        )

    def token(self, args):
        """
        Check or set GitHub auth token.

        Args:
            args: Parsed command-line arguments.

        Returns:
            None
        """
        if args.token:
            set_token(args.token)
        else:
            print(get_token(verbose=True))

    def print_help(self, args):
        """
        Display help information based on provided arguments.

        Args:
            args: Parsed command-line arguments.

        Returns:
            None
        """
        if args.topic:
            self.commands[args.topic].print_help()
        else:
            self.parser.print_help()
