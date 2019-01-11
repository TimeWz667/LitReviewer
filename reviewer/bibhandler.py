import bibtexparser as bp
from titlecase import titlecase

__author__ = 'TimeWz667'
__all__ = ['load_bib', 'output_bib', 'get_bib_string']


def load_bib(path, abbreviations=None):
    if abbreviations:
        def callback(word, **kwargs):
            if word.upper() in abbreviations:
                return word.upper()

        def tit(word):
            return titlecase(word, callback=callback)
    else:
        tit = titlecase

    with open(path, 'rt', encoding='utf-8') as file:
        db = bp.load(file)
        for ent in db.entries:
            ent.update({k: v[1:-1] for k, v in ent.items() if v.startswith('{') and k != 'author'})

            ent['title'] = tit(ent['title'])

            if 'journal' in ent:
                ent['journal'] = tit(ent['journal'])
            if 'booktitle' in ent:
                ent['booktitle'] = tit(ent['booktitle'])

        return db


def get_bib(entries, keep_abstract=False):
    bn = bp.bibdatabase.BibDatabase()
    for ent in entries:
        ent = dict(ent)
        if not keep_abstract and 'abstract' in ent:
            del ent['abstract']
        bn.entries.append(ent)
    return bn


def output_bib(entries, path, keep_abstract=False):
    bn = get_bib(entries, keep_abstract=keep_abstract)

    with open(path, 'w') as file:
        bp.dump(bn, file)


def get_bib_string(entries, keep_abstract=False):
    bn = get_bib(entries, keep_abstract=keep_abstract)
    writer = bp.bwriter.BibTexWriter()
    return writer.write(bn)
