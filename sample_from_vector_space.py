import csv
import random

from tqdm import tqdm

import json_util
import numpy as np
import ast
import matplotlib.pyplot as plt


def create_distances_dictionary(cerf_filtered_words):
    distances_dictionary = {}
    for word1, data1 in tqdm(cerf_filtered_words.items()):
        embedding1 = np.array(data1['embedding'])
        for word2, data2 in cerf_filtered_words.items():
            if f'{word1}_{word2}' in distances_dictionary:
                # print(f"skipping {word1} {word2}")
                continue
            embedding2 = np.array(data2['embedding'])
            distance = np.linalg.norm(embedding2 - embedding1)
            distances_dictionary[f'{word1}_{word2}'] = distance
            distances_dictionary[f'{word2}_{word1}'] = distance
    return distances_dictionary


def create_distances_matrix(sorted_words_set):
    distances_matrix = np.zeros((len(sorted_words_set), len(sorted_words_set)))
    for i, (word1, definition1, _, _, embedding1) in enumerate(tqdm(sorted_words_set)):
        embedding1 = np.array(ast.literal_eval(embedding1))
        for j, (word2, definition2, _, _, embedding2) in enumerate(sorted_words_set):
            embedding2 = np.array(ast.literal_eval(embedding2))
            distance = np.linalg.norm(embedding2 - embedding1)
            distances_matrix[i, j] = distance
    return distances_matrix


def save_distances_matrix(distances_matrix):
    np.save('data/distances_matrix_2.npy', distances_matrix)


def query_distance_matrix(cerf_filtered_words, distances_matrix, word1, word2):
    # IndexError: only integers, slices (`:`), ellipsis (`...`), numpy.newaxis (`None`) and integer or boolean arrays are valid indices
    return distances_matrix[
        list(cerf_filtered_words.keys()).index(word1), list(cerf_filtered_words.keys()).index(word2)]


def choose_greedy_words(cerf_filtered_words, distances_matrix, filtered_words):
    """
    Choose three words from the filtered set that are as far apart from each other as possible using a greedy algorithm.

    Parameters:
    distances_dictionary (dict): A dictionary where keys are tuples of word pairs and values are distances.
    filtered_words (list): A list of words that are within the ideal distance range from the center word.

    Returns:
    tuple: A tuple containing the three chosen words.
    """
    # Initialize the best combination of words and the maximum distance sum
    best_combination = None
    max_distance_sum = -1

    # Iterate over all possible combinations of three words
    seen = set()
    for i in range(len(filtered_words)):
        for j in range(i + 1, len(filtered_words)):
            for k in range(j + 1, len(filtered_words)):
                w1, w2, w3 = filtered_words[i], filtered_words[j], filtered_words[k]
                if (w1, w2, w3) in seen:
                    continue
                seen.add((w1, w2, w3))
                seen.add((w1, w3, w2))
                seen.add((w2, w1, w3))
                seen.add((w2, w3, w1))
                seen.add((w3, w1, w2))
                seen.add((w3, w2, w1))
                # Calculate the sum of pairwise distances
                distance_sum = (query_distance_matrix(cerf_filtered_words, distances_matrix, w1, w2) +
                                query_distance_matrix(cerf_filtered_words, distances_matrix, w1, w3) +
                                query_distance_matrix(cerf_filtered_words, distances_matrix, w2, w3))
                # Update the best combination if the current sum is greater
                if distance_sum > max_distance_sum:
                    max_distance_sum = distance_sum
                    best_combination = (w1, w2, w3)

    return best_combination


def filter_distances_dictionary_by_center(cerf_filtered_words, distances_matrix, center_word, distance, error):
    filtered_words = []
    # center_embedding = cerf_filtered_words[center_word]['embedding']
    for word, data in cerf_filtered_words.items():
        if query_distance_matrix(cerf_filtered_words, distances_matrix, center_word, word) > distance + error:
            continue
        if query_distance_matrix(cerf_filtered_words, distances_matrix, center_word, word) < distance:
            continue
        if word == center_word:
            continue
        filtered_words.append(word)
        # print(word, query_distance_matrix(cerf_filtered_words, distances_matrix, center_word, word))

    return filtered_words


def load_csv_to_list():
    with open("data/words - words.csv") as fp:
        reader = csv.reader(fp, delimiter=",", quotechar='"')
        # next(reader, None)  # skip the headers
        data_read = [row for row in reader]
        return data_read[1:]


def sample(words_set, used_words, distances_matrix):
    central_word = None
    while central_word is None or central_word[0] in used_words:
        central_word = random.choice(words_set)

    for distance_vector, word in zip(distances_matrix, words_set):
        if word == central_word:
            break

    sorted_by_distance = sorted(list(zip(words_set, distance_vector)), key=lambda x: x[1])

    question_words = [central_word]
    for possible_distractor, distance_to_center in sorted_by_distance:
        if distance_to_center == 0:
            continue
        if possible_distractor[0] in used_words:
            continue
        if len(question_words) == 4:
            break
        question_words.append(possible_distractor)

    return question_words

    # for error in [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7]:
    #     filtered_words = filter_distances_dictionary_by_center(cerf_filtered_words, distances_matrix, 'helicopter', 4, error)
    #     if len(filtered_words) > 10:
    #         break
    # print(filtered_words)
    # filtered_words = filter_distances_dictionary_by_center(cerf_filtered_words, distances_matrix, 'helicopter', 4, 0.15)
    # sample_words = choose_greedy_words(cerf_filtered_words, distances_matrix, filtered_words)


# words_set, used_words, distances_matrix
def create_question(four_words, question_type='word'):
    # choose 4 random words that are in both cerf_filtered_words and definitions_dict
    chosen_word = four_words[0]
    if question_type == 'word':
        word_question = {"question": f"What is the meaning of the word \"{chosen_word[0]}\"?",
                         "options": [word[1] for word in four_words],
                         "correct_option": chosen_word[1],
                         "question_word": chosen_word[0]}
        return word_question
    elif question_type == 'definition':
        definition_question = {"question": f"What is the word for the definition \"{chosen_word[1]}\"?",
                                 "options": [word[0] for word in four_words],
                                 "correct_option": chosen_word[0],
                                 "question_word": chosen_word[0]}
        return definition_question


def print_question(four_words, question_type, question_number):
    if question_type == 'word':
        print(f"{question_number}. What is the meaning of the word \"{four_words[0][0]}\"?")
        for i, word in enumerate(random.sample(four_words, len(four_words))):
            print(f"{chr(i + 97)}) {word[1]}")
        print()
    elif question_type == 'definition':
        print(f"{question_number}. What is the word for the definition \"{four_words[0][1]}\"?")
        for i, word in enumerate(random.sample(four_words, len(four_words))):
            print(f"{chr(i + 97)}) {word[0]}")
        print()

    print()
    print()
    print()
    print(four_words[0][:2])
    print()


def create_questions_csv(sorted_words_set, distances_matrix, num_questions_per_section, section_size=1000):
    used_words = []
    question_number = 0
    questions = []
    questions_types = []
    for i in range(7):
        section_sorted_words_set = sorted_words_set[i * section_size: (i + 1) * section_size]
        for _ in range(num_questions_per_section):
            question_number += 1
            four_words = sample(section_sorted_words_set, used_words, distances_matrix)
            used_words.extend(four_words)

            if question_number % 2 == i % 2:
                print_question(four_words, 'word', question_number)
                question = create_question(four_words, 'word')
                questions_types.append('word')
            else:
                print_question(four_words, 'definition', question_number)
                question = create_question(four_words, 'definition')
                questions_types.append('definition')

            questions.append(question)
    with open(f"data/questions_file.csv", "w") as questions_file:
        questions_file.write("type,content,alignment,name\n")
        for question, question_type in zip(questions, questions_types):
            questions_file.write(f"text,{question['question']},center,Q_{question_type}_{question['question_word']}\n")
        # questions_file.write(
        #     'text,"In this experiment, you will Answer my questions. <p>if you fail to answer them <b>We will record you mouse.</b></p>",center,Instructions\n')
        # questions_file.write(
        #     'text,"Click the button below and wait for an important and deep question to appear. <p>Once it appears, click on the appropriate Answer.</p>",center,MouseInstructions')

    with open(f"data/answers_file.csv", "w") as answers_file:
        answers_file.write(
            "type,feedback,choices,target,locations,duration_timer,layout,name,button_content,sampling_rate,"
            "reference_point,proportional\n")
        for question, question_type in zip(questions, questions_types):
            # file.write(
            #     f"choice,,,true,{question['question']},,{question['options']},{[question['correct_option']]},Fixed,,\n")
            row = f"choice,TRUE,\"{question['options']}\",\"{[question['correct_option']]}\",random,TRUE,\"[2,2]\",A_{question_type}_{question['question_word']},,,,,\n"
            row = row.replace('\'', "\"\"")
            answers_file.write(row)
    # answers_file.write("mouse_reset,true,,,,,,MouseReset,Click Here,,,\n")
    # answers_file.write("mouse_position,true,,,,,,Mousetracking,,50,center,true\n")


def main():
    # cerf_filtered_words = json_util.load_json_to_object('cerf_filtered_words.json')
    # # cerf_filtered_words_subset = {word: cerf_filtered_words[word] for word in list(cerf_filtered_words.keys())[:100]}
    # distances_dictionary = create_distances_dictionary(cerf_filtered_words)
    # json_util.save_objects_json(distances_dictionary, 'data/distances_dictionary.json')
    sorted_words_set = load_csv_to_list()

    # save_distances_matrix(create_distances_matrix(sorted_words_set))

    # load csv to dictionary
    distances_matrix = np.load('data/distances_matrix_2.npy')
    # question_words = sample(sorted_words_set, used_words, distances_matrix)
    # for word in question_words:
    #     print(word[0], "-", word[1])

    create_questions_csv(sorted_words_set, distances_matrix, 3 * 6)


if __name__ == '__main__':
    main()
