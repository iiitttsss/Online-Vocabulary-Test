import numpy as np


def read_vectors_from_file(filename):
    d = {}
    with open(filename, 'rt') as infile:
        for line in infile:
            word, *rest = line.split()
            d[word] = np.array(list(map(float, rest)))
    return d


def cosine_similarity(x: np.ndarray, y: np.ndarray) -> float:
    return np.dot(x, y) / (np.linalg.norm(x) * np.linalg.norm(y))


def euclidean_distance(x: np.ndarray, y: np.ndarray) -> float:
    return np.linalg.norm(x - y)

def get_all_words_from_file(filename):
    words = set()  # Use a set to avoid duplicate words
    with open(filename, 'rt') as infile:
        for line in infile:
            word, _ = line.split(maxsplit=1)
            words.add(word)
    return list(words)


def compute_distances(word: str, vectors: dict, distance_func) -> list:
    """
    Computes the distances between the given word and all other words using the specified distance function.

    :param word: The target word to compare distances to.
    :param vectors: A dictionary where keys are words and values are their vector representations.
    :param distance_func: A function that computes the distance between two vectors.
    :return: A sorted list of tuples where each tuple contains a word and its distance from the given word.
    """
    if word not in vectors:
        raise ValueError(f"Word '{word}' not found in the vectors dictionary.")

    word_vector = vectors[word]
    distances = []

    for other_word, other_vector in vectors.items():
        if other_word != word:
            distance = distance_func(word_vector, other_vector)
            distances.append((other_word, distance))

    # Sort by distance
    distances.sort(key=lambda x: x[1])
    return distances

def main():
    e = read_vectors_from_file("glove.6B/glove.6B.50d.txt")
    print(e['apples'])
    distances = compute_distances('apples', e, euclidean_distance)
    print(distances)


if __name__ == '__main__':
    main()
