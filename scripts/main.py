import re
import pandas as pd
from trankit import Pipeline, trankit2conllu

import time
import resource


class CSVInfo:
    '''
    A class representing a .csv document with all the coordination info.
    '''

    def __init__(self, template):
        self.template = template
        self.csv = pd.DataFrame(columns=template.columns)

    def add_info_row(self, info):
        self.csv.loc[len(self.csv)] = info

    def export(self, path):
        self.csv.to_csv(path, index=False)


def load_data(corpus):
    with open(corpus, "r") as file:
        document = file.readlines()
    return document


def parse_sentences(pipeline, data):
    sentences = pipeline.posdep(data)
    return sentences


def clean(dict_parsed):
    '''
    Removes all sentences that contain copyright-avoiding string "@ @ @ ..." and header tags.
    Returns a dictionary with correct sentences and list of removed sentences' ids.
    '''

    clean_dict = {"sentences": []}
    clean_dict["text"] = dict_parsed["text"]
    removed_sentences_ids = []
    for sentence in dict_parsed["sentences"]:
        if re.search(r'@(\s@){8}\s@', sentence["text"]) or re.search(r'<p>', sentence["text"]):
            removed_sentences_ids.append(sentence["id"])

        if sentence["id"] not in removed_sentences_ids:
            clean_dict["sentences"].append(sentence)

    return clean_dict, removed_sentences_ids


def search_for_id(dict_parsed):
    '''
    Returns a matched string with line id from the corpus.
    '''
    match = re.match(r"@@\d{7}", dict_parsed["text"])
    return match.group(0)


def select_conj(dict_parsed):
    '''
    Selects all the sentences with at least one conjunction and adds
    key with a list of dictionaries, containing conjunction words and information
    about them. Also, adds information about dependencies and token children.

    Returns a dictionary and a list of selected sentences' ids.
    '''

    selected_dict = {}
    selected_dict["text"] = dict_parsed["text"]
    selected_dict["sentences"] = []

    selected_ids = []

    for sentence in dict_parsed["sentences"]:
        sentence["dependencies"] = []
        sentence["words_cconj"] = []
        conj_counter = 0
        for token in sentence["tokens"]:
            token["children"] = []
            sentence["dependencies"].append(
                (token["head"], token["id"], token["deprel"]))

            # Information about word's children
            for t in sentence["tokens"]:
                if t["head"] == token["id"]:
                    token["children"].append(t["id"])

            if token["deprel"] == "conj" and sentence["id"] not in selected_ids:
                conj_counter += 1
                sentence["words_cconj"].append({"no": conj_counter,
                                                "word": token["text"],
                                                "tag": token["xpos"],
                                                "pos": token["upos"],
                                                "ms": " "})
                if sentence["id"] not in selected_ids:
                    selected_ids.append(sentence["id"])
            
            

        if sentence["id"] in selected_ids:
            selected_dict["sentences"].append(sentence)

    return selected_dict, selected_ids


def conj_info_extraction(dict_parsed):  
    for sentence in dict_parsed["sentences"]:
        conj_counter = 1
        sentence["coordination_info"] = []

        for token in sentence["tokens"]:
            if token["deprel"] == "conj":
                left_token_conj = sentence["tokens"][token["head"] - 1]
                left_token_conj_id = left_token_conj["id"]
                right_token_conj = token
                right_token_conj_id = token["id"]

                if left_token_conj["head"] != 0:
                    governor = sentence["tokens"][left_token_conj["head"] - 1]
                else:
                    governor = left_token_conj

                if governor["id"] < left_token_conj["id"]:
                    # governor is on the left
                    governor_dir = "L"
                elif governor["id"] > left_token_conj["id"]:
                    # governor is on the right
                    governor_dir = "R"
                else:
                    # there is no governor
                    governor_dir = "0"

                if governor_dir == "0":
                    text, xpos, upos, ms = " ", " ", " ", " "
                else:
                    text = governor["text"]
                    xpos = governor["xpos"]
                    upos = governor["upos"]
                    try:
                        ms = governor["feats"]
                    except KeyError:
                        ms = " "

                try:
                    left_feats = left_token_conj["feats"]
                    right_feats = token["feats"]
                except KeyError:
                    left_feats = " "
                    right_feats = " "
               
                sentence["coordination_info"].append({"no.conjunct": conj_counter,
                                                      "left_head": left_token_conj,
                                                      "right_head": right_token_conj,
                                                      "text": {"left": left_token_conj["text"],
                                                               "right": right_token_conj["text"]},
                                                      "left_deplabel": left_token_conj["deprel"],
                                                      "right_deplabel": right_token_conj["deprel"],
                                                      "left_tag": left_token_conj["xpos"],
                                                      "right_tag": right_token_conj["xpos"],
                                                      "left_upos": left_token_conj["upos"],
                                                      "right_upos": right_token_conj["upos"],
                                                      "left_ms": left_feats,
                                                      "right_ms": right_feats,
                                                      "governor": text,
                                                      "governor_dir": governor_dir,
                                                      "governor_tag": xpos,
                                                      "governor_pos": upos,
                                                      "governor_ms": ms
                                                      })

            conj_counter += 1


def search_for_dependencies(sentence):
    '''
    Przerobiony kod od Magdy
    '''

    for con in sentence["coordination_info"]:
        left_list = []
        right_list = []

        for t in con["left_head"]["children"]:
            if sentence["tokens"][t - 1]["id"] != con["right_head"]["id"] and sentence["tokens"][t - 1]["deprel"] != "cc" and sentence["tokens"][t - 1]["deprel"] != "punct":
                left_list.append(t)
        for t in con["right_head"]["children"]:
            if sentence["tokens"][t - 1]["deprel"] != "punct" and sentence["tokens"][t - 1]["deprel"] != "cc":
                right_list.append(t)

        for child in left_list:
            for t in sentence["tokens"][child - 1]["children"]:
                left_list.append(t)
        for child in right_list:
            for t in sentence["tokens"][child - 1]["children"]:
                right_list.append(t)
        
        left_list.append(con["left_head"]["id"])
        right_list.append(con["right_head"]["id"])

        left = ""
        right = ""
        Lwords = 0
        Ltokens = 0
        Rwords = 0
        Rtokens = 0

        left_list.sort()
        right_list.sort()

        for id in left_list:
            Ltokens += 1
            if sentence["tokens"][id - 1]["deprel"] != "punct":
                Lwords += 1
            left += sentence["tokens"][id - 1]["text"]
            if id < max(left_list):
                left += " "
                
        for id in right_list:
            Rtokens += 1
            if sentence["tokens"][id - 1]["deprel"] != "punct":
                Rwords += 1
            right += sentence["tokens"][id - 1]["text"]
            if id < max(right_list):
                right += " "

        con["right_text"] = right
        con["left_text"] = left
        con["Rwords"] = Rwords
        con["Lwords"] = Lwords
        con["Rtokens"] = Rtokens
        con["Ltokens"] = Ltokens


def count_syllables():
    pass


def create_csv_template(columns_info_path):
    template = pd.read_csv(columns_info_path)
    return template


def toconllu(parsed_data, filename):
    conllu_doc = trankit2conllu(parsed_data)
    with open(filename, "w") as file:
        file.write(conllu_doc)


def addline(conj, word, sentence, file_path, genre, sent_id):
    line = {"governor.position": conj["governor_dir"],
            "governor.word": conj["governor"],
            "governor.tag": conj["governor_tag"],
            "governor.pos": conj["governor_pos"],
            "governor.ms": conj["governor_ms"],
            "conjunction.word": word["word"],
            "conjunction.tag": word["tag"],
            "conjunction.pos": word["pos"],
            "conjunction.ms": word["ms"],
            "no.conjuncts": len(sentence["coordination_info"]) + 1,
            "L.conjunct": conj["left_text"],
            "L.dep.label": conj["left_deplabel"],
            "L.head.word": conj["text"]["left"],
            "L.head.tag": conj["left_tag"],
            "L.head.pos": conj["left_upos"],
            "L.head.ms": conj["left_ms"],
            "L.words": conj["Lwords"],
            "L.tokens": conj["Ltokens"],
            "L.syllables": "Lsyllables",
            "L.chars": len(conj["left_text"]),
            "R.conjunct": conj["right_text"],
            "R.dep.label": conj["right_deplabel"],
            "R.head.word": conj["text"]["right"],
            "R.head.tag": conj["right_tag"],
            "R.head.pos": conj["right_upos"],
            "R.head.ms": conj["right_ms"],
            "R.words": conj["Rwords"],
            "R.tokens": conj["Rtokens"],
            "R.syllables": "Rsyllables",
            "R.chars": len(conj["right_text"]),
            "sentence": sentence["text"],
            "sent.id": sent_id + "-" + str(sentence["id"] - 1),
            "genre": genre,
            "converted.from.file": file_path
}


    '''
    line = [conj["governor_dir"], conj["governor"], conj["governor_tag"],
            conj["governor_pos"], conj["governor_ms"], word["word"],
            word["tag"], word["pos"], word["ms"],
            len(sentence["coordination_info"]) +
            1, conj["left_text"], conj["left_deplabel"],
            conj["text"]["left"], conj["left_tag"], conj["left_upos"],
            conj["left_ms"], conj["Lwords"], conj["Ltokens"],
            "Lsyllables", len(conj["left_text"]), conj["right_text"],
            conj["right_deplabel"], conj["text"]["right"], conj["right_tag"],
            conj["right_upos"], conj["right_ms"], conj["Rwords"],
            conj["Rtokens"], "Rsyllables", len(conj["right_text"]),
            sentence["text"], sent_id+"-" +
            str(sentence["id"]), genre,
            file_path
            ]
    '''
    return line


def main():
    time_start = time.perf_counter()

    eng_pipeline = Pipeline("english", gpu=False, cache_dir="./media/adglo/Others/nlp/cache")

    file_path = "/media/adglo/Others/nlp/dlm/coca-samples/text_fic_2000.txt"
    genre = file_path.split("_")[1].split(".")[0]
    text = load_data(file_path)

    template = create_csv_template("/media/adglo/Others/nlp/dlm/csv/UD_Polish-LFG.csv")
    info_csv = CSVInfo(template)

    # Looping through lines in .txt file
    for i in range(1, 3):
        dict_of_sentences = parse_sentences(eng_pipeline, text[i])

        clean_depparsed, removed_ids = clean(dict_of_sentences)
        conj_depparsed, selected_ids = select_conj(clean_depparsed)

        sent_id = search_for_id(clean_depparsed)

        conj_info_extraction(conj_depparsed)


        # Adding info
        for sentence in conj_depparsed["sentences"]:
            search_for_dependencies(sentence)
            if len(sentence["coordination_info"]) == 1:
                conj = sentence["coordination_info"][0]
                word = sentence["words_cconj"][0]

                info_csv.add_info_row(addline(conj, word, sentence, file_path, genre, sent_id))

            elif len(sentence["coordination_info"]) > 1:
                conj_first = sentence["coordination_info"][0]
                conj_last = sentence["coordination_info"][len(sentence["coordination_info"]) - 1]

                word_first = sentence["words_cconj"][0]
                word_last = sentence["words_cconj"][len(sentence["words_cconj"]) - 1]

                info_csv.add_info_row(addline(conj_first, word_first, sentence, file_path, genre, sent_id))
                info_csv.add_info_row(addline(conj_last, word_last, sentence, file_path, genre, sent_id))

            '''
            if len(conj) != 0:
                info_csv.add_info_row(addline(conj, word, sentence, file_path, genre, sent_id))

            
                line = [conj["governor_dir"], conj["governor"], conj["governor_tag"],
                        conj["governor_pos"], conj["governor_ms"], word["word"],
                        word["tag"], word["pos"], word["ms"],
                        len(sentence["coordination_info"]) +
                        1, conj["left_text"], conj["left_deplabel"],
                        conj["text"]["left"], conj["left_tag"], conj["left_upos"],
                        conj["left_ms"], conj["Lwords"], conj["Ltokens"],
                        "Lsyllables", len(conj["left_text"]), conj["right_text"],
                        conj["right_deplabel"], conj["text"]["right"], conj["right_tag"],
                        conj["right_upos"], conj["right_ms"], conj["Rwords"],
                        conj["Rtokens"], "Rsyllables", len(conj["right_text"]),
                        sentence["text"], sent_id+"-" +
                        str(sentence["id"]), genre,
                        file_path
                        ]

            else:
                print(conj)
                print("---------")
                print(sentence["text"])
            '''
        #print("rm ids:", removed_ids)
        #print("line id:", search_for_id(clean_depparsed))
        # print(clean_depparsed["text"])
        #print("--------")
        # print(conj_depparsed)
        #print("selected conj ids:", selected_ids, "\n--------\n")
        if conj_depparsed is not None:
            toconllu(conj_depparsed, f"/media/adglo/Others/nlp/dlm/conll-docs/conllu_conj{i}_{genre}.conll")
        # toconllu(clean_depparsed, f"conllu{i}.txt")
        #print(conj_depparsed["sentences"][7]["dependencies"])
        #print(conj_depparsed["sentences"][7]["coordination_info"])
        #print("-------")
        

        time_elapsed = (time.perf_counter() - time_start)
        memMb = resource.getrusage(
            resource.RUSAGE_SELF).ru_maxrss/1024.0/1024.0
        print("%5.1f secs %5.1f MByte" % (time_elapsed, memMb))

    info_csv.export("/media/adglo/Others/nlp/dlm/csv/info_csv_test3.csv")


main()
