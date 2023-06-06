# PSBS

The PuzzleScript Build System!

PSBS combines multiple files into one puzzlescript source file and uploads it to the web.

This is an early development release and changes may be made to the project structure and config file formats in the future.

## Features

 - Compile PuzzleScript games from many files using Jinja2 templates
 - Load existing PuzzleScript projects right from their gists
 - Load existing PuzzleScript projects from a source text file
 - Save PuzzleScript projects to gists
 - Launch your project from play.html or the PuzzleScript editor

## Installing

Simply run the following command from your terminal

`pip install 'psbs @ git+https://github.com/jcmiller11/PSBS'`

## Connecting to GitHub

By default PSBS will attempt to run `gh auth token` to recieve an authorization token from the GitHub command line tool.  If you would like to use a different token or prefer not to install the GitHub command line tool you can add an environmental variable to .profile, .bashrc, .zshenv or whatever file your shell uses for handling such things

`export PSBS_GH_TOKEN=insert your token here`

## Usage

Enter `psbs` into your terminal to get a list of commands

## Example

    psbs new myProject
    cd myProject
    psbs build