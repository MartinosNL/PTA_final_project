import pathlib
import sys
from collections import Counter


def tag_entities(filepath):
    # Open file and put contents in string.
    str_file_contents = ""
    with open(filepath, 'r') as file_input:
        for line in file_input:
            str_file_contents += line
    # Add tag to lines in string where applicable.
    list_tagged = []
    for line in str_file_contents.split("\n"):
        if line != "":
            line += " "
            line += "dummy" # Replace this dummy with the entity tag.
            list_tagged.append(line)
    return "\n".join(list_tagged)

def create_filepaths(path_input):
    '''Returns all filepaths leading to "en.tok.off.pos" files.'''
    list_append = []
    list_return = []
    for item in path_input.iterdir():
        path_subdir = ""
        if item.is_file() == False:
            path_subdir = pathlib.Path(item)
            list_add = create_filepaths(path_subdir)
            if list_add != []:
                list_append += list_add
        else:
            list_append.append(item)
    for item in list_append:
        if str(item)[-3:] == "pos":
            list_return.append(str(item))
    return list_return


def main():
    path_base = pathlib.Path(sys.argv[1])
    list_paths = create_filepaths(path_base)
    for filepath in list_paths:
        tag_entities(filepath)


main()
