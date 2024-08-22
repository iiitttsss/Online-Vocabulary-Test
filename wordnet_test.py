# import nltk
# import ssl
#
# try:
#     _create_unverified_https_context = ssl._create_unverified_context
# except AttributeError:
#     pass
# else:
#     ssl._create_default_https_context = _create_unverified_https_context
#
# nltk.download('wordnet')
import re
from nltk.corpus import wordnet as wn
from sentence_transformers import SentenceTransformer

import json_util
from similarity_score import calculate_similarity_score

from tqdm import tqdm
import Levenshtein



# Function to get definitions
def get_definitions(word):
    definitions = []
    for synset in wn.synsets(word):
        definitions.append(synset.definition())
    return definitions


# Function to get all words in WordNet
def get_all_words():
    words = set()
    for synset in wn.all_synsets():
        for lemma in synset.lemmas():
            words.add(lemma.name())
    return words


def get_all_words_with_frequencies():
    word_freq = {}
    for synset in wn.all_synsets():
        for lemma in synset.lemmas():
            word_freq[lemma.name()] = word_freq.get(lemma.name(), 0) + lemma.count()
    return word_freq


def test1():
    # Example usage
    word = "sweet"
    definitions = get_definitions(word)
    print(f"Definitions of the word '{word}':")
    for idx, definition in enumerate(definitions, 1):
        print(f"{idx}. {definition}")
    # all_words = get_all_words()
    # all_words = [w for w in all_words if '_' not in w]

    # Get all words with their frequencies
    # all_words_with_frequencies = get_all_words_with_frequencies()
    #
    # # Sort words by frequency
    # sorted_words_with_frequencies = sorted(all_words_with_frequencies.items(), key=lambda item: item[1], reverse=True)
    #
    # # Print the total number of words and the top 10 most common words
    # print(f"Total number of words in WordNet: {len(all_words_with_frequencies)}")
    # print("Top 10 most common words:")
    # for word, freq in sorted_words_with_frequencies[:10]:
    #     print(f"{word}: {freq}")

def get_first_definitions():
    all_words = get_all_words()
    all_words = [w for w in all_words if '_' not in w]
    definitions_dict = {}
    for word in tqdm(all_words):
        definitions_dict[word] = [synset.definition() for synset in wn.synsets(word)]
        # for synset in wn.synsets(word):
        #     definitions[word] = synset.definition()
        #     break
    json_util.save_objects_json(definitions_dict, 'definitions.json')


def is_word_in_text(word, text, max_edit_distance=1):
    """
    Checks if a word appears in a text (as a part of another word or whole) or if there is a word with a very small edit distance to it.

    :param word: The word to check for in the text.
    :param text: The text to search within.
    :param max_edit_distance: The maximum edit distance to consider for matching.
    :return: True if the word is found or if a word with a small edit distance is found; False otherwise.
    """
    # Tokenize the text into words
    words_in_text = re.findall(r'\b\w+\b', text)

    # Check if the word appears in the text or as part of another word
    for w in words_in_text:
        if word in w:
            return True
        if Levenshtein.distance(word, w) <= max_edit_distance:
            return True

    return False

def get_definitions_by_similarity_score():
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # combined_dict = json_util.load_json_to_object('combined_dict_10.json')
    # all_words = combined_dict.keys()
    all_words = get_all_words()
    all_words = [w for w in all_words if '_' not in w]
    definitions_dict = {}
    for word in tqdm(all_words):
        definitions = [synset.definition() for synset in wn.synsets(word)]
        if len(definitions) == 0:
            continue
        elif len(definitions) == 1:
            pass
        else:
            definitions = [(definition, calculate_similarity_score(word, definition, model=model)) for definition in definitions if not is_word_in_text(word, definition)]
            definitions = sorted(definitions, key=lambda x: x[1], reverse=True)
            definitions = [definition[0] for definition in definitions]

        definitions_dict[word] = definitions

    json_util.save_objects_json(definitions_dict, 'definitions_with_similarity_score.json')

def combine_into_single_definition():
    definitions_with_similarity_score = json_util.load_json_to_object('definitions_with_similarity_score.json')
    definitions_by_default_order = json_util.load_json_to_object('definitions.json')

    definitions_dict_final = {}

    for word, definitions_by_score_list in tqdm(definitions_with_similarity_score.items()):
        if len(definitions_by_score_list) == 0:
            continue
        definitions_by_order_list = definitions_by_default_order[word]
        values = {}
        for i, definition in enumerate(definitions_by_score_list):
            values[definition] = i
        # for i, definition in enumerate(definitions_by_order_list):
        #     values[definition] += i
        definitions_final = sorted(values.items(), key=lambda x: x[1])
        definitions_final = [definition for definition, v in definitions_final]
        definitions_dict_final[word] = definitions_final[0]

    json_util.save_objects_json(definitions_dict_final, 'definitions_dict_final.json')



if __name__ == '__main__':
    # get_first_definitions()
    get_definitions_by_similarity_score()
    # combine_into_single_definition()
