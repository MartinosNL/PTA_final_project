import pathlib
import sys
from collections import Counter
from nltk import ne_chunk
from nltk.corpus import wordnet
import spacy
import en_core_web_sm
import wikipediaapi
import warnings
import locationtagger


def add_urls(tagged_file):
    '''using: https://github.com/martin-majlis/Wikipedia-API/'''

    added_urls = ""
    for line in tagged_file.split("\n"):
        current_split = line.split(" ")
        # check if word is tagged with an entity
        if len(current_split) == 6:
            # Takes the entity and checks if this entity has a wikipedia page
            wiki_wiki = wikipediaapi.Wikipedia('en')
            page_py = wiki_wiki.page(current_split[3])
            if page_py.exists() == True:
                # Takes the found wikipedia page, sets it to a URL and adds
                # this to the line
                url = page_py.fullurl
                line += " " + url
        added_urls += line + "\n"
    return added_urls
    # TODO: The wikipediafinder does not look at words crossing over lines (Burkina Faso) or looks at the tagged entity yet


def gpe_disambig(string):
    '''This function uses locationtagger to disambiguate between CIT and COU.'''
    place_entity = locationtagger.find_locations(text = string)
    if place_entity.countries != []:
        return "COU"
    if place_entity.cities != []:
        return "CIT"
    if place_entity.regions != []:
        return "COU"
    if string == "St.":
        return "CIT"
    elif string == "Los":
        return "CIT"
    elif string == "U.S.":
        return "COU"
    return None


def fit_ner(tag, word):
    '''This handles turning the ne_chunk labels into the desired labels.'''
    if tag == "PERSON":
        return "PER"
    elif tag == "ORGANIZATION":
        return "ORG"
    elif tag == "GPE" or tag == "GSP":
        return gpe_disambig(word)
    else:
        return None


def detect_other(string, tagged_by_spacy):
    '''This function is able to recognise animals and sports thanks to synsets.'''
    # Pre-process the input.
    if wordnet.synsets(string) == []:
        return None
    current_synsets = wordnet.synsets(string)[0]
    list_hypernyms = set([i for i in current_synsets.closure(lambda s:s.hypernyms())])

    # Create the synsets for our categories.
    synset_ani = wordnet.synset('animal.n.01')
    synset_spo = wordnet.synset("sport.n.01")

    # Check them.
    if synset_ani in list_hypernyms:
        return "ANI"
    if synset_spo in list_hypernyms:
        return "SPO"
    
    word_tag_list = [(X.text, X.label_) for X in tagged_by_spacy.ents]
    for word_tag in word_tag_list:
        if len(word_tag) == 2 and word_tag[1] == 'WORK_OF_ART': # or word_tag[1] == 'EVENT':
            return 'ENT'
        if len(word_tag) == 2 and word_tag[1] == 'LOC':
            return 'NAT'
            # print(word_tag, "TEST")
        # if len(word_tag) == 2 and word_tag[1] == 'WORK_OF_ART': # or word_tag[1] == 'EVENT':
        #     return 'ENT'
            # print(word_tag, 'TEST')
    return None


# def detect_ent_nat(tagged_by_spacy):
#     # nlp = en_core_web_sm.load()
#     # tagged_by_spacy = nlp(words)
#     # print([(X.text, X.label_) for X in tagged_by_spacy.ents])
#     word_tag_list = [(X.text, X.label_) for X in tagged_by_spacy.ents]
#     print(word_tag_list)
#     for word_tag in word_tag_list:
#         if len(word_tag) == 2 and word_tag[1] == 'LOC':
#             return 'NAT'
#             # print(word_tag, "TEST")
#         if len(word_tag) == 2 and word_tag[1] == 'WORK_OF_ART': # or word_tag[1] == 'EVENT':
#             return 'ENT'
#             # print(word_tag, 'TEST')
#     return None


def open_file(filepath):
    str_file_contents = ""
    with open(filepath, 'r') as file_input:
        for line in file_input:
            str_file_contents += line
    return str_file_contents

def create_ner_tags(str_file_contents):
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
            for i in range(len(ne)): # We do this to handle multi-word entities.
                list_tags.append(ne.label())
        else:
            list_tags.append(None)
    return list_tags

def get_words(str_file_contents):
    str_content = ''
    for line in str_file_contents.split("\n"):
        if line != "":
            str_content = str_content + ' ' + line.split(" ")[3]
    return str_content

def tagger(str_file_contents, list_tags, tagged_by_spacy):
     # Add tag to lines in string where applicable.
    list_tagged = []
    accum_line = 0
    for line in str_file_contents.split("\n"):
        if line != "":
            tag_other = detect_other(line.split(" ")[3], tagged_by_spacy)
            # print(line.split(" ")[3])
            # detect_ent_nat(line.split(" ")[3])
            if list_tags[accum_line] != None:
                made_tag = fit_ner(list_tags[accum_line], line.split(" ")[3])
                if list_tags[accum_line] != None:

                    if made_tag != None:
                        line += " "
                        line += made_tag
            elif tag_other != None:
                line += " "
                line += tag_other
            # Sysnet functionality per word could be added here.
            list_tagged.append(line)
            accum_line += 1
    return "\n".join(list_tagged)

# def tag_entities(filepath):
#     '''Adds entity tags to the file in the filepath provided.
#     Returns the contents of the file as a string.'''
#     # Open file and put contents in string.
#     str_file_contents = ""
#     with open(filepath, 'r') as file_input:
#         for line in file_input:
#             str_file_contents += line

#     # Create NER tags.
#     list_pos = []
#     for line in str_file_contents.split("\n"):
#         current_split = line.split(" ")
#         if len(current_split) >= 4:
#             tuple_current = (current_split[3], current_split[4])
#             list_pos.append(tuple_current)
#     ne_tags = ne_chunk(list_pos)
    
#     # Clean up NER tags.
#     list_tags = []
#     for ne in ne_tags:
#         if hasattr(ne, 'label'):
#             for i in range(len(ne)): # We do this to handle multi-word entities.
#                 list_tags.append(ne.label())
#         else:
#             list_tags.append(None)

#     # Add tag to lines in string where applicable.
#     list_tagged = []
#     accum_line = 0
#     for line in str_file_contents.split("\n"):
#         if line != "":
#             tag_other = detect_other(line.split(" ")[3])
#             # print(line.split(" ")[3])
#             # detect_ent_nat(line.split(" ")[3])
#             if list_tags[accum_line] != None:
#                 made_tag = fit_ner(list_tags[accum_line], line.split(" ")[3])
#                 if made_tag != None:
#                     line += " "
#                     line += made_tag
#             elif tag_other != None:
#                 line += " "
#                 line += tag_other
#             # Sysnet functionality per word could be added here.
#             list_tagged.append(line)
#             accum_line += 1
#     return "\n".join(list_tagged)
#     # TODO: Find a way to tag entertainment and nature, as neither synsets nor
#     # available NER can seemingly do so, at least from my testing.


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
    nlp = en_core_web_sm.load()
    # tagged_by_spacy = nlp(words)
    warnings.filterwarnings("ignore") # Wordnet loves to throw warnings.
    path_base = pathlib.Path(sys.argv[1])
    list_paths = create_filepaths(path_base)
    # for filepath in list_paths:
    #     tagged_entities = tag_entities(filepath)
    #     urled_entities = add_urls(tagged_entities)
    # # TODO: write docstrings for all functions :)
    for filepath in list_paths:
        str_file_contents = open_file(filepath)
        words = get_words(str_file_contents)
        tagged_by_spacy = nlp(words)
        # detect_ent_nat(tagged_by_spacy)
        list_tags = create_ner_tags(str_file_contents)
        print(tagger(str_file_contents, list_tags, tagged_by_spacy))


main()
