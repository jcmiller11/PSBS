import re


def redact(input_str):
    # find all comments
    comments = re.finditer(r"(?:\()([^)]*)(?:\))", input_str)
    for comment in comments:
        start = comment.span()[0]
        end = comment.span()[1]
        # replace any non-newline character with a space
        redacted = re.sub(r"[^\n]", " ", comment.group())
        input_str = input_str[:start] + redacted + input_str[end:]
    return input_str


def split_ps(input_str):
    input_redacted = redact(input_str)
    sections = {
        "prelude": [],
        "tags": [],
        "objects": [],
        "legend": [],
        "sounds": [],
        "collisionlayers": [],
        "rules": [],
        "winconditions": [],
        "levels": [],
    }
    section_headers = list(sections.keys())[1:]
    headers = re.finditer(
        r"^(" + "|".join(section_headers) + ") *$",
        input_redacted,
        flags=re.IGNORECASE | re.MULTILINE,
    )

    section = "prelude"
    start = 0
    for header in headers:
        content = input_str[start : header.span()[0]]
        content = re.sub(r"^(=*) *", "", content, flags=re.MULTILINE)
        sections[section].append(content.strip())
        section = header.group().strip().lower()
        start = header.span()[1]
    content = input_str[start:]
    content = re.sub(r"^(=*) *", "", content, flags=re.MULTILINE)
    sections[section].append(content.strip())
    if not sections["tags"]:
        del sections["tags"]

    return sections


def get_engine(input_str):
    start_str = "http"
    end_str = "editor.html"
    start = input_str.find(start_str)
    end = input_str.find(end_str)
    return input_str[start:end]
