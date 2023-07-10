from trankit import Pipeline
from tqdm import tqdm
import time
import resource

from coordlm.utils.data import CSVInfo
from coordlm.utils import other
from coordlm.utils import cleaning
from coordlm.tools import extract

CORPUS_PATH = "coca-samples/text_test_sample.txt"
TEMPLATE_PATH = "csv/UD_Polish-LFG.csv"
CSV_PATH = "csv/info_csv_from_test_sample.csv"


def parse_sentences(pipeline, data):
    sentences = pipeline.posdep(data)
    return sentences


def main():

    time_start = time.perf_counter()

    eng_pipeline = Pipeline("english", gpu=False, cache_dir="cache")

    genre = CORPUS_PATH.split("_")[1].split(".")[0]
    text = other.load_data(CORPUS_PATH)

    template = other.create_csv_template(TEMPLATE_PATH)
    info_csv = CSVInfo(template)

    # Looping through lines in .txt file
    for i in tqdm(range(0, len(text))):
        text[i] = cleaning.clean_text(text[i])

        dict_of_sentences = parse_sentences(eng_pipeline, text[i])
        clean_depparsed, removed_ids = cleaning.clean_parsed(dict_of_sentences)
        conj_depparsed, selected_ids = extract.select_conj(clean_depparsed)

        sent_id = extract.search_for_id(clean_depparsed)

        extract.conj_info_extraction(conj_depparsed)

        # Adding info
        for sentence in conj_depparsed["sentences"]:
            extract.search_for_dependencies(sentence)
            try:
                word_first = sentence["words_cconj"][0]
            except IndexError:
                word_first = {"no": "",
                              "word": "",
                              "tag": "",
                              "pos": "",
                              "ms": ""}
            if len(sentence["coordination_info"]) == 1:
                conj = sentence["coordination_info"][0]

                info_csv.add_info_row(extract.addline(conj, word_first, sentence, CORPUS_PATH, genre, sent_id))

            elif len(sentence["coordination_info"]) > 1:
                conj_first = sentence["coordination_info"][0]
                conj_last = sentence["coordination_info"][len(sentence["coordination_info"]) - 1]

                word_last = sentence["words_cconj"][len(sentence["words_cconj"]) - 1]

                info_csv.add_info_row(extract.addline(conj_first, word_first, sentence, CORPUS_PATH, genre, sent_id))
                info_csv.add_info_row(extract.addline(conj_last, word_last, sentence, CORPUS_PATH, genre, sent_id))

        #if conj_depparsed is not None:
        #    toconllu(conj_depparsed, f"conll-docs/conllu_conj{i}_{genre}.conll")


    time_elapsed = (time.perf_counter() - time_start)
    memMb = resource.getrusage(
        resource.RUSAGE_SELF).ru_maxrss/1024.0/1024.0
    print("%5.1f secs %5.1f MByte" % (time_elapsed, memMb))

    info_csv.export(CSV_PATH)

main()




'''
poprawić na tych samych tabelkach:
interpunkcja w conjunctach
enhanced UD sprawdzić
dzielone podrzędniki, jeśli jest po prawej stronie
koordynacja a i b i dalej jest podpięte pod a to pomijamy
Disappionted, Sara set the mail aside, took off her fatigue jacket
JEDNO SŁOWO: ROZBIJA NA COMPOUND (zwróć uwagę)
liczyć dodatkowe tokeny ale słowo jest jedno
INTERPUNKCJA

jeśli jest do wszystkiego to pomijamy
jeśli przecinek po lewej to ignorujemy
przecinek i dywiz
relacja: jeśli którykolwiek ma tą samą relację, to po lewej jest do pierwszego członu
jak na lewo relacja, to gdy żaden inny nie ma takiej samej relacji to jest wspólna

sprawdzić podział na zdania!
oszacować ile można sparsować


podział zdań
jeden wiersz jedno zdanie
'''