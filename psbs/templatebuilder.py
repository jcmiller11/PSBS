def make_header(section_name):
    output = "="*(len(section_name)+1)
    output += f"\n{section_name.upper()}\n"
    output += "="*(len(section_name)+1)
    output += "\n\n"
    return output


def make_template(src_tree):
    output = ""
    for section in src_tree:
        if section != "prelude":
            output += make_header(section)
        if not src_tree[section]:
            src_tree[section] = [""]
        for index in range(len(src_tree[section])):
            index += 1
            if len(src_tree[section]) == 1:
                index = ""
            src_filename = f"{section}{index}.pss"
            output += f"{{% include \"{src_filename}\" %}}\n"
        output += "\n"
    return output.strip()
