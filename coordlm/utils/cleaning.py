import re

def clean_text(text):
    text_sub = re.sub(r'<p>|<h>',"", text)
    return text_sub


def clean_parsed(dict_parsed):
    '''
    Removes all sentences that contain copyright-avoiding string "@ @ @ ..." and header tags.
    Returns a dictionary with correct sentences and list of removed sentences' ids.
    '''

    clean_dict = {"sentences": []}
    clean_dict["text"] = dict_parsed["text"]
    removed_sentences_ids = []
    for sentence in dict_parsed["sentences"]:
        if re.search(r'@(\s@){8}\s@', sentence["text"]):
            removed_sentences_ids.append(sentence["id"])

        if sentence["id"] not in removed_sentences_ids:
            clean_dict["sentences"].append(sentence)

    return clean_dict, removed_sentences_ids
