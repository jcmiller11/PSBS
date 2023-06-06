#!/usr/bin/env python3

from argparse import ArgumentParser

from .project import PSBSProject


def main():
    parser = ArgumentParser(add_help=False)
    parser._positionals.title = "Commands"
    subparser = parser.add_subparsers(dest="command")
    commands = {
        'build': subparser.add_parser(
            "build",
            help="Build project in current working directory",
            add_help=False),
        'upload': subparser.add_parser(
            "upload",
            help="Build project then upload to gist",
            add_help=False),
        'run': subparser.add_parser(
            "run",
            help="Build project, upload, then run in web browser",
            add_help=False),
        'new': subparser.add_parser(
            "new",
            help="Create a new project",
            add_help=False),
        'help': subparser.add_parser(
            "help",
            help="Display help dialog",
            add_help=False)}

    commands['new'].add_argument("name", type=str)
    new_project_flags = commands['new'].add_mutually_exclusive_group()
    new_project_flags.add_argument('--from-gist', '-g', dest="gist_id", type=str)
    new_project_flags.add_argument('--from-file', '-f', dest="file", type=str)

    args = parser.parse_args()

    if args.command == "build":
        project = PSBSProject()
        project.build()
    elif args.command == "upload":
        project = PSBSProject()
        project.build()
        project.upload()
    elif args.command == "run":
        project = PSBSProject()
        project.build()
        project.upload()
        project.run()
    elif args.command == "new":
        if args.gist_id is not None:
            PSBSProject.create(args.name, gist_id=args.gist_id)
        elif args.file is not None:
            PSBSProject.create(args.name, file=args.file)
        else:
            PSBSProject.create(args.name)
    elif args.command == "help":
        parser.print_help()
    elif args.command is None:
        parser.print_help()
