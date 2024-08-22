from random import sample

import json_util
import sample_from_vector_space


def create_question(cerf_filtered_words, definitions_dict, used_words, question_type="word"):
    # choose 4 random words that are in both cerf_filtered_words and definitions_dict
    words = list(definitions_dict.keys())
    words = [word for word in words if type(definitions_dict[word]) is not list and word in cerf_filtered_words and word not in used_words]
    four_words = sample(words, 4)
    used_words.extend(four_words)
    chosen_word = four_words[0]
    if question_type == "word":
        word_question = {"question": f"What is the meaning of the word \"{chosen_word}\"?",
                         "options": [definitions_dict[word] for word in four_words],
                         "correct_option": definitions_dict[chosen_word],
                         "question_word": chosen_word}
        return word_question
    if question_type == "definition":
        definition_question = {"question": f"Which word has the meaning \"{definitions_dict[chosen_word]}\"?",
                               "options": four_words,
                               "correct_option": chosen_word,
                               "question_word": chosen_word}
        return definition_question


def create_questions_csv(cerf_filtered_words, definitions_dict, question_type="word", num_questions=10):
    questions = []
    used_words = []
    for i in range(num_questions):
        question = create_question(cerf_filtered_words, definitions_dict, used_words, question_type)
        questions.append(question)
    with open("data/questions_file.csv", "w") as file:
        # type, content, alignment, name
        # text, "In this experiment, you will Answer my questions. <p>if you fail to asnwer them <b>You will die, I will kill you.</b></p>", center, Instructions
        # text, "Who marries Monica in the TV show ""friends""?", center, MarryMonicaFriends
        # text, "Who doesn't get married in the show ""friends""?", center, NotMarriedFriends
        file.write("type,content,alignment,name\n")
        for question in questions:
            file.write(f"text,{question['question']},center,Q{question['question_word']}\n")
        file.write('text,"In this experiment, you will Answer my questions. <p>if you fail to answer them <b>We will record you mouse.</b></p>",center,Instructions\n')
        file.write('text,"Click the button below and wait for an important and deep question to appear. <p>Once it appears, click on the appropriate Answer.</p>",center,MouseInstructions')

    with open("data/answers_file.csv", "w") as file:
        # type, sampling_rate, reference_point, proportional, feedback, name, button_content, choices, target, locations, duration_timer, layout
        # mouse_position, 50, center, true, true, Mousetracking,, , , , ,
        # mouse_reset,, , , true, MouseReset, Click
        # Here,, , , ,
        file.write("type,feedback,choices,target,locations,duration_timer,layout,name,button_content,sampling_rate,"
         "reference_point,proportional\n")
        for question in questions:
            # file.write(
            #     f"choice,,,true,{question['question']},,{question['options']},{[question['correct_option']]},Fixed,,\n")
            row = f"choice,TRUE,\"{question['options']}\",\"{[question['correct_option']]}\",random,TRUE,\"[2,2]\",A{question['question_word']},,,,,\n"
            row = row.replace('\'', "\"\"")
            file.write(row)
        file.write("mouse_reset,true,,,,,,MouseReset,Click Here,,,\n")
        file.write("mouse_position,true,,,,,,Mousetracking,,50,center,true\n")


def main():
    definitions_dict = json_util.load_json_to_object('definitions_dict.json')
    for word, definition in definitions_dict.items():
        if type(definition) is list:
            continue
        start_length = len(definition)
        definitions_dict[word] = definition.replace("\'", "")
        definitions_dict[word] = definition.replace("\"", "")
        if start_length != len(definitions_dict[word]):
            print(word, definition)
            print(definitions_dict[word])
            print()
    cerf_filtered_words = json_util.load_json_to_object('cerf_filtered_words.json')
    used_words = []
    question = create_question(cerf_filtered_words, definitions_dict, used_words)
    create_questions_csv(cerf_filtered_words, definitions_dict, "word", 15)
    # print()
    # print()
    print(question['question'])
    for i, option in enumerate(question['options']):
        print(f"{i + 1}. {option}")

    # for bucket_size in [1000]:
    #     counter = 0
    #     histogram = []
    #     word_levels = []
    #     for word, data in cerf_filtered_words.items():
    #         if counter % bucket_size == 0:
    #             histogram.append(0)
    #             print(f"bucket {counter // bucket_size}")
    #             if word_levels:
    #                 word_levels = sorted(word_levels)
    #                 q1 = word_levels[len(word_levels) // 4]
    #                 q2 = word_levels[len(word_levels) // 2]
    #                 q3 = word_levels[3 * len(word_levels) // 4]
    #                 print(f" word levels: {q1}-{q3}")
    #             word_levels = []
    #         counter += 1
    #         if word in definitions_dict:
    #             histogram[-1] += 1
    #             # if data['word_level'] not in word_levels:
    #             word_levels.append(data['word_level'])
    #             # if histogram[-1] < 10:
    #             #     print(data['word_level'])
    #     # print(histogram)


if __name__ == '__main__':
    main()
