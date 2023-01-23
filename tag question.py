import spacy

# Load the en_core_web_sm model
nlp = spacy.load("en_core_web_sm")

# Define the sentence
sentence = "Rahim who is a youtuber wants to get a job"

# Parse the sentence
doc = nlp(sentence)

# Extract the principal clause by iterating over the subtree of the root token
principal_clause = []
for token in doc:
    if token.dep_ == "ROOT":
        for t in token.subtree:
            principal_clause.append(t.text)
        break

# Join the words of the principal clause to form a sentence
principal_clause = " ".join(principal_clause)

# Print the principal clause
print(principal_clause)
