import random

import json_util
from csv_to_json import csv_to_json, txt_to_list, csv_to_json_int_values
from glove_test import read_vectors_from_file
from wordnet_test import get_all_words_with_frequencies
from tqdm import tqdm


def create_combined_dict():
    frequencies = csv_to_json_int_values('unigram_freq.csv')
    cerf_words = csv_to_json('ENGLISH_CERF_WORDS.csv')
    stop_words = txt_to_list('stopwords-en.txt')
    embeddings = read_vectors_from_file("glove.6B/glove.6B.50d.txt")

    combined_dict = {}

    for word, word_freq in frequencies.items():
        if word not in embeddings:
            continue
        if word in stop_words:
            continue
        if len(word) <= 2:
            continue
        if word not in cerf_words:
            continue
        embedding = embeddings[word]

        combined_dict[word] = {'embedding': list(embedding),
                               'frequency': word_freq,
                               'word_level': cerf_words[word]}
        # print(f"{word}\t{word_freq}")

    print(f"number of words: {len(combined_dict)}")
    json_util.save_objects_json(combined_dict, 'cerf_filtered_words.json')


def main():
    cerf_filtered_words = json_util.load_json_to_object('cerf_filtered_words.json')
    count_word_by_level = {}
    for word, word_data in cerf_filtered_words.items():
        if word_data['word_level'] not in count_word_by_level:
            count_word_by_level[word_data['word_level']] = 0
        count_word_by_level[word_data['word_level']] += 1

    print(count_word_by_level)


if __name__ == '__main__':
    create_combined_dict()
    main()
