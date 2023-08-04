 # PSBS Command Line Interface

#### Commands:

[`psbs new`](command-line-interface#new) Creates a new project

[`psbs build`](command-line-interface#build) Builds the project in the current working directory

[`psbs export`](command-line-interface#export) Builds project then export to game

[`psbs run`](command-line-interface#run) Builds project, exports it, then runs it in your web browser

[`psbs token`](command-line-interface#token) Check or set the GitHub auth token

`psbs help` View help dialogue

## New

`psbs new [--new-gist,-n] [--from-gist,-g GIST_ID] [--from-file,-f FILE] name`

Creates a new project.

The -n flag will create a new gist for the project to upload to and run from.

If a gist id or text file are supplied the project source files will automatically be populated with the contents. If both a gist and a file are given the project will be built from the source in the text file but be configured to upload and run from the supplied gist id.

!> Creating a new gist or building from a gist require a [GitHub auth token](getting-started#connecting-to-github).

#### Options:
- --new-gist, -n
   - Create a new gist for the project
- --from-gist GIST_ID, -g GIST_ID
   - Build project from existing source at supplied gist
- --from-file FILE, -f FILE
   - Build project from existing source in supplied file

#### Examples:
Create a new project named myproject, and create a new gist on your GitHub account for it
```bash
psbs new -n myproject
```
Create a new project named myproject from a text file
```bash
psbs new -n -f puzzlescript.txt myproject
```
Create a new project named myproject from a text file, and create a new gist on your GitHub account for it
```bash
psbs new -f puzzlescript.txt myproject
```
Create a new project named myproject from a supplied gist on your GitHub account
```bash
psbs new -g e3435763f6b7bee395251a909dcd89c3 myproject
```
## Build

`psbs build`

Builds the project in the current working directory.

This is the heart of PSBS's functionality.  Takes the source files in your project's src/ directory and compiles them into a PuzzleScript game which can will be found in your project's bin/ directory.

## Export

`psbs export`

Builds project then exports it to a game.

Runs psbs build and then exports your project to a game.

If a gist id found in your project's config.yaml the game will be exported there, otherwise it will be exported to a local html file.

## Run

`psbs run [--editor,-e]`

Builds project, exports it, then runs it in your web browser.

Runs psbs build, exports the project to a game, then runs it in your web browser.  If a gist id is found in your project's config.yaml it will be exported there and your browser will be opened to PuzzleScript's play.html pointed at that gist.  If no gist id is found a local html file will be exported and opened in your web browser.

Alternatively, if running from a gist if the -e flag is given it will open to editor.html instead.

#### Options:
- --editor, -e
   - Run project in PuzzleScript editor

## Token

`psbs token [token]`

Gets and sets the GitHub auth token that PSBS will use for [connecting to Github](getting-started#connecting-to-github)

If a token is supplied PSBS will start using that token for all GitHub Gist related functions.

If no token is supplied this command will output information on what token, if any, is currently in use.
