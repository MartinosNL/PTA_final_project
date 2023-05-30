import pathlib
import sys
from collections import Counter
from nltk import ne_chunk
import spacy


def gpe_disambig(string):
    '''This will handle the separation between COU and CIT.'''
    return "dummy"


def fit_ner(string):
    '''This will handle turning the chunk labels into the desired labels.'''
    if string == "PERSON":
        return "PER"
    elif string == "ORGANIZATION":
        return "ORG"
    elif string == "GPE" or string == "GSP":
        return gpe_disambig(string)
    else:
        return None
    # TODO: No idea how to find animals, sports, nature and entertainment.
    # Will do research into this but will likely have to be done with a separate
    # tagging system through sysnet.


def tag_entities(filepath):
    # Open file and put contents in string.
    str_file_contents = ""
    with open(filepath, 'r') as file_input:
        for line in file_input:
            str_file_contents += line

    # Create NER tags.
    list_pos = []
    for line in str_file_contents.split("\n"):
        current_split = line.split(" ")
        if len(current_split) >= 4:
            tuple_current = (current_split[3], current_split[4])
            list_pos.append(tuple_current)
    ne_tags = ne_chunk(list_pos)

    # Clean up NER tags.
    list_tags = []
    for ne in ne_tags:
        if hasattr(ne, 'label'):
            # We do this to handle multi-word entities.
            for i in range(len(ne)):
                list_tags.append(ne.label())
        else:
            list_tags.append(None)

    # Add tag to lines in string where applicable.
    list_tagged = []
    accum_line = 0
    for line in str_file_contents.split("\n"):
        if line != "":
            if list_tags[accum_line] != None:
                made_tag = fit_ner(list_tags[accum_line])
                if made_tag != None:
                    line += " "
                    line += made_tag
            # Sysnet functionality per word could be added here.
            list_tagged.append(line)
            accum_line += 1
    return "\n".join(list_tagged)


def create_filepaths(path_input):
    '''Returns a list of filepaths leading to "en.tok.off.pos" files.'''
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
        print(tag_entities(filepath))
    # TESTETSTESTESTST


main()
