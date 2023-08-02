from coordlm.tools.sentences import sentence_split_exporting

EXPORT_PATH = "/media/adglo/Others/nlp/dlm/data/txt/trankit_split_sentences.txt"
DATA_PATH = "/media/adglo/Others/nlp/dlm/data/samples/coca-samples/text_test_sample.txt"

sentence_split_exporting(DATA_PATH, EXPORT_PATH, "txt")