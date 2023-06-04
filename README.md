# PSBS

The PuzzleScript Build System!

PSBS combines multiple files into one puzzlescript source file and uploads it to the web.

This is an early development release and changes may be made to the project structure and config file formats in the future.

## Installing

Simply run the following command from your terminal

`pip install 'psbs @ git+https://github.com/jcmiller11/PSBS'`

## Connecting to GitHub

By default PSBS will attempt to run `gh auth token` to recieve an authorization token from the GitHub command line tool.  If you would like to use a different token or prefer not to install the GitHub command line tool you can add an environmental variable to .profile, .bashrc, .zshenv or whatever file your shell uses for handling such things

`export PSBS_GH_TOKEN=insert your token here`

## Usage

Enter `psbs` into your terminal to get a list of commands