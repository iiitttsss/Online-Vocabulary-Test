"""
Install the Google AI Python SDK

$ pip install google-generativeai

See the getting started guide for more information:
https://ai.google.dev/gemini-api/docs/get-started/python
"""
import time

import google
import google.generativeai as genai
from google.generativeai.types import generation_types

import json_util

genai.configure(api_key='API KEY')


# Create the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    # safety_settings = Adjust safety settings
    # See https://ai.google.dev/gemini-api/docs/safety-settings
)


def get_definition(word):
    chat_session = model.start_chat()
    response = chat_session.send_message(
        f"what is the most common definition of the word \"{word}\" (give only one definition. do not explain anything around it. do not use the word {word} in what you print.)")

    return str(response.text).strip()


def main():
    cerf_filtered_words = json_util.load_json_to_object('cerf_filtered_words.json')
    definitions_dict = json_util.load_json_to_object('definitions_dict.json')
    save_counter = 0
    for i, (word, data) in enumerate(cerf_filtered_words.items()):
        if word in definitions_dict:
            continue
        # if i % 10 >= 8:
        #     continue
        save_counter += 1
        frequency = data['frequency']
        try:
            definition = get_definition(word)
        except google.api_core.exceptions.ResourceExhausted as e:
            print(f"Error getting definition for |{word}|")
            try_again_count = 0
            delay_time = 60
            while try_again_count < 5:
                print(f"Trying again in {delay_time} seconds")
                try:
                    time.sleep(delay_time)
                    definition = get_definition(word)
                    break
                except google.api_core.exceptions.ResourceExhausted as e:
                    try_again_count += 1
                except generation_types.StopCandidateException as e:
                    print(f"possible harmful content for |{word}|")
                    print(e)
                    definition = ["possible harmful content"]
                    break
        except generation_types.StopCandidateException as e:
            print(f"possible harmful content for |{word}|")
            print(e)
            definition = ["possible harmful content"]
            # continue

        definitions_dict[word] = definition
        print(f"{i}\t{word}: {definition}\t{frequency}")
        if save_counter > 15:
            save_counter = 0
            json_util.save_objects_json(definitions_dict, 'definitions_dict.json')

    json_util.save_objects_json(definitions_dict, 'definitions_dict.json')


def clean_definitions_dict():
    # Remove duplicate definitions
    definitions_dict = json_util.load_json_to_object('definitions_dict.json')
    definitions_appeared = {}
    for _, definition in definitions_dict.items():
        if type(definition) is list:
            continue
        if definition not in definitions_appeared:
            definitions_appeared[definition] = 0
        definitions_appeared[definition] += 1

    corrected_definitions_dict = {}
    for word, definition in definitions_dict.items():
        if type(definition) is list:
            corrected_definitions_dict[word] = definition
            continue
        if definition not in definitions_appeared:
            corrected_definitions_dict[word] = definition
            continue
        if definitions_appeared[definition] == 1:
            corrected_definitions_dict[word] = definition
            continue

    json_util.save_objects_json(corrected_definitions_dict, 'definitions_dict.json')

def export_words_union_tsv():
    definitions_dict = json_util.load_json_to_object('definitions_dict.json')
    cerf_filtered_words = json_util.load_json_to_object('cerf_filtered_words.json')

    with open('words_union.tsv', 'w') as file:
        file.write("word\tdefinition\tfrequency\tcerf_level\tembedding\n")
        for word, data in cerf_filtered_words.items():
            if word in definitions_dict:
                definition = definitions_dict[word]
                if type(definition) is list:
                    continue
                definition = definition.replace("\t", " ")
                frequency = data['frequency']
                cerf_level = data['word_level']
                embedding = data['embedding']
                file.write(f"{word}\t{definition}\t{frequency}\t{cerf_level}\t{embedding}\n")

if __name__ == '__main__':
    # print(get_definition("sweet"))
    # main()
    # clean_definitions_dict()
    export_words_union_tsv()



