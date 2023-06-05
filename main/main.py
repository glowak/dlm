from trankit import Pipeline
import time
import resource

from classes import CSVInfo
from utilities import *
from cleaning import *
from extract import *


def parse_sentences(pipeline, data):
    sentences = pipeline.posdep(data)
    return sentences


def main():
    CORPUS_PATH = "/media/adglo/Others/nlp/dlm/coca-samples/text_fic_2000.txt"
    TEMPLATE_PATH = "/media/adglo/Others/nlp/dlm/csv/UD_Polish-LFG.csv"
    CSV_PATH = "/media/adglo/Others/nlp/dlm/csv/info_csv_test3.csv"

    time_start = time.perf_counter()

    eng_pipeline = Pipeline("english", gpu=False)

    genre = CORPUS_PATH.split("_")[1].split(".")[0]
    text = load_data(CORPUS_PATH)

    template = create_csv_template(TEMPLATE_PATH)
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

                info_csv.add_info_row(addline(conj, word, sentence, CORPUS_PATH, genre, sent_id))

            elif len(sentence["coordination_info"]) > 1:
                conj_first = sentence["coordination_info"][0]
                conj_last = sentence["coordination_info"][len(sentence["coordination_info"]) - 1]

                word_first = sentence["words_cconj"][0]
                word_last = sentence["words_cconj"][len(sentence["words_cconj"]) - 1]

                info_csv.add_info_row(addline(conj_first, word_first, sentence, CORPUS_PATH, genre, sent_id))
                info_csv.add_info_row(addline(conj_last, word_last, sentence, CORPUS_PATH, genre, sent_id))

        if conj_depparsed is not None:
            toconllu(conj_depparsed, f"/media/adglo/Others/nlp/dlm/conll-docs/conllu_conj{i}_{genre}.conll")


        time_elapsed = (time.perf_counter() - time_start)
        memMb = resource.getrusage(
            resource.RUSAGE_SELF).ru_maxrss/1024.0/1024.0
        print("%5.1f secs %5.1f MByte" % (time_elapsed, memMb))

    info_csv.export(CSV_PATH)


main()