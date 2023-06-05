import spacy
from spacy_syllables import SpacySyllables

nlp = spacy.load("en_core_web_sm")
nlp.add_pipe("syllables", after="tagger")

assert nlp.pipe_names == ["tok2vec", "tagger", "syllables", "parser",  "attribute_ruler", "lemmatizer", "ner"]

count = 0 
text = ""
with open("sentences.txt", "r") as file:
    for line in file:
        # Split the sentence into the text and syllable count
        sentence, syllable_count = line.rsplit("(", 1)
        syllable_count = syllable_count.replace(" syllables)", "")
        text += sentence
        count += int(syllable_count)

# Print the results
print(text)
print("Syllable count according to ChatGPT: ", count) 

doc = nlp(text)
data = [(token.text, token._.syllables, token._.syllables_count) for token in doc]

sum = 0
for el in data:
    if el[2] is not None:
        sum += el[2]

print("Syllable count according to spaCy: ", sum)
print("Proportion spaCy/GPT: ", sum/count)