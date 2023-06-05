#!/usr/bin/env python3

from sys import argv

from .project import PSBSProject, new

def show_commands():
    print("\033[1mCOMMANDS\033[0m")
    print("build:\tBuild project")
    print("upload:\tBuild project then upload to gist")
    print("run:\tBuild project, upload to gist, then launch in browser")
    print("new:\tCreate a new project")

def main():
    #TODO: refactor with argparse or similar
    if len(argv)>1:
        first_arg = argv[1].lower()
        if first_arg == "build":
            project = PSBSProject()
            project.build()
        elif first_arg == "upload":
            project = PSBSProject()
            project.build()
            project.upload()
        elif first_arg == "run":
            project = PSBSProject()
            project.build()
            project.upload()
            project.run()
        elif first_arg == "new":
            if len(argv)<3:
                print("Please provide a name for the new project")
            else:
                new(argv[2])
        else:
            print("I didn't understand that\n")
            show_commands()
    else:
        print("PSBS - PuzzleScript Build System\n")
        show_commands()
