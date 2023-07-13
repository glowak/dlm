from trankit import Pipeline
from coordlm.utils.other import load_data
from coordlm.tools.extract import search_for_id
from coordlm.utils.data import CSVInfo


def sentence_split_exporting(data_path: str,
                             csv_path: str) -> None:
    p = Pipeline("english", gpu=True)
    
    
    document = load_data(data_path)
    
    csv = CSVInfo(cols=["sentence", "id_trankit", "id_global"])

    for i in range(len(document)):
        split = p.ssplit(document[i])
        
        for sentence in split["sentences"]:
            csv.add_row({"sentence": sentence["text"],
                         "id_trankit": sentence["id"],
                         "id_global": "{}-{}".format(search_for_id(split), str(sentence["id"] - 1))
                         })
    
    csv.export(csv_path)


def depparse_sentences(pipeline: Pipeline,
                       data: str) -> dict:
    sentences = pipeline.posdep(data)
    return sentences