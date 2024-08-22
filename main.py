import random

import json_util
from glove_test import read_vectors_from_file
from wordnet_test import get_all_words_with_frequencies
from tqdm import tqdm


def create_combined_dict():
    definitions = json_util.load_json_to_object('definitions_with_similarity_score.json')
    embeddings = read_vectors_from_file("glove.6B/glove.6B.50d.txt")
    frequencies = get_all_words_with_frequencies()

    combined_dict = {}

    for word, definition in tqdm(definitions.items()):
        if word in embeddings:
            embedding = embeddings[word]
            freq = frequencies[word]
            if freq < 5:
                continue
            combined_dict[word] = {'definition': definition,
                                   'embedding': list(embedding),
                                   'freq': freq}

    print(f"number of words: {len(combined_dict)}")
    json_util.save_objects_json(combined_dict, 'combined_dict_10.json')


def create_question(word, combined_dict):
    print(word)
    print(combined_dict[word]['definition'])
    for word, data in random.sample(list(combined_dict.items()), k=300):
        print(f"{data['definition']} - {word}")


def main():
    combined_dict = json_util.load_json_to_object('combined_dict_10.json')
    create_question('sweet', combined_dict)


if __name__ == '__main__':
    # create_combined_dict()
    main()
