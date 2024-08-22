from sentence_transformers import SentenceTransformer, util


def calculate_similarity_score(word, definition, model=None):
    if model is None:
        # Load the pre-trained model
        model = SentenceTransformer('all-MiniLM-L6-v2')
    # Create the sentences to encode
    sentences = [word, definition]

    # Encode the sentences
    embeddings = model.encode(sentences, convert_to_tensor=True)

    # Compute cosine similarity
    similarity_score = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()
    return similarity_score


def main():
    # Define the word and its definition
    word = "bank"
    definition = "the land alongside or sloping down to a river or lake."
    similarity_score = calculate_similarity_score(word, definition)
    print(f"Similarity score between '{word}' and the definition is: {similarity_score:.4f}")


if __name__ == '__main__':
    main()
