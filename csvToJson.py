import pandas as pd
import json

def find_non_utf8_lines(file_path):
    with open(file_path, 'rb') as file:
        for line_number, line in enumerate(file, start=1):
            try:
                line.decode('utf-8')
            except UnicodeDecodeError as e:
                print(f"Line {line_number} has non-UTF-8 characters.")
                print(f"Error: {e}")
                break


def read_csv_files(stimuli_path, responses_path):
    """
    Reads the CSV files and returns the DataFrames.

    Parameters:
    - stimuli_path: Path to the stimulus-definitions CSV.
    - responses_path: Path to the response-definitions CSV.

    Returns:
    - stimuli_df: DataFrame containing the stimulus definitions.
    - responses_df: DataFrame containing the response definitions.
    """
    find_non_utf8_lines(stimuli_path)
    stimuli_df = pd.read_csv(stimuli_path)
    responses_df = pd.read_csv(responses_path)
    return stimuli_df, responses_df


def create_instr_section(stimuli_df):
    """
    Creates the 'Instr' section of the JSON structure.

    Parameters:
    - stimuli_df: DataFrame containing the stimulus definitions.

    Returns:
    - instr_section: Dictionary representing the 'Instr' section.
    """
    instr_stimuli = stimuli_df[stimuli_df['name'] == 'Instructions']['name'].tolist()
    return {
        "type": "instruction",
        "stimuli": instr_stimuli,
        "duration": 3
    }


def create_trials_section(stimuli_df, responses_df):
    """
    Creates the 'Trials' section of the JSON structure.

    Parameters:
    - stimuli_df: DataFrame containing the stimulus definitions.
    - responses_df: DataFrame containing the response definitions.

    Returns:
    - trials_section: Dictionary representing the 'Trials' section.
    """
    trial_stimuli = stimuli_df['name'].tolist()
    trial_responses = responses_df['name'].apply(lambda x: [x]).tolist()

    # Remove unwanted stimuli and responses
    trial_stimuli = [stimul for stimul in trial_stimuli if stimul not in ["Instructions", "MouseInstructions"]]
    trial_responses = [response for response in trial_responses if response[0] not in ["Mousetracking", "MouseReset"]]

    trial_responses_yes = trial_responses[0][0]
    trial_responses_no = trial_responses[1][0]

    word_types = stimuli_df['word_type'].tolist()
    trial_responses_final = [trial_responses_yes if word_type==1 else trial_responses_no for word_type in word_types]

    print(len(trial_stimuli))
    print(len(trial_responses))
    return {
        "type": "AFC",
        "stimulus_pattern": {"order": "pseudorandom",
                             "attribute": "diff_category",
                             "preshuffle": True,
                             "min_N": 3, "max_N": 4,
                             "limit": 3
                             },
        "stimuli": trial_stimuli,
        "delay": 0.1,
        "responses": trial_responses_final
    }


def create_reset_temp_section(len_responses):
    """
    Creates the 'ResetTemp' section of the JSON structure.

    Parameters:
    - trial_stimuli: List of trial stimuli names.

    Returns:
    - reset_temp_section: Dictionary representing the 'ResetTemp' section.
    """
    reset_stimuli = [{"which": ["MouseInstructions"], "location": [5]}] * 60
    return {
        "type": "mouse_reset",
        "stimuli": reset_stimuli,
        "responses": ["MouseReset"]
    }


def construct_json_structure(stimuli_df, responses_df):
    """
    Constructs the complete JSON structure from the provided DataFrames.

    Parameters:
    - stimuli_df: DataFrame containing the stimulus definitions.
    - responses_df: DataFrame containing the response definitions.

    Returns:
    - json_structure: Dictionary representing the complete JSON structure.
    """
    instr_section = create_instr_section(stimuli_df)
    trials_section = create_trials_section(stimuli_df, responses_df)
    reset_temp_section = create_reset_temp_section(len(trials_section['responses']) - 2)

    return {
        "Instr": instr_section,
        "Trials": trials_section,
        "ResetTemp": reset_temp_section
    }


def main(stimuli_path, responses_path):
    """
    Main function to read CSVs and construct the JSON structure.

    Parameters:
    - stimuli_path: Path to the stimulus-definitions CSV.
    - responses_path: Path to the response-definitions CSV.

    Returns:
    - json_output: JSON string representing the complete structure.
    """
    stimuli_df, responses_df = read_csv_files(stimuli_path, responses_path)
    json_structure = construct_json_structure(stimuli_df, responses_df)
    return json.dumps(json_structure, indent=2)


if __name__ == "__main__":
    # Paths to the CSV files
    stimuli_csv_path = 'stimulus-definitions_lextale.csv'
    responses_csv_path = 'response-definitions_lextale.csv'

    # Generate and print the JSON output
    print(main(stimuli_csv_path, responses_csv_path))
