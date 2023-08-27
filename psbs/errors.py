"""
ERRORS MODULE

This module defines custom error classes for PSBS.

Example:
    try:
        # Code that may raise PSBSError or its subclasses
    except PSBSError as err:
        print(f"An error occurred: {err}")

"""


class PSBSError(Exception):
    """Generic error for when PSBS can not continue execution"""
