# Getting Started

## Installing

If you already have Python 3.8 or greater and pip installed simply run the following command from your terminal

`pip install psbs`

If you don't have Python and pip installed: [Download Python](https://www.python.org/downloads/)

## Connecting to GitHub

PSBS will build your projects into PuzzleScript source without interacting with GitHub at all, however uploading and running your projects requires an authorization token.

By default PSBS will attempt to run `gh auth token` to recieve an authorization token from the GitHub command line tool.  If you would like to use a different token or prefer not to install the GitHub command line tool you can run the following command.

`psbs token `*`insert_your_token_here`*