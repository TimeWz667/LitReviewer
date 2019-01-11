from .bibhandler import *
from .status import in_status, Status
from .form import PaperForm

import json
__author__ = 'TimeWz667'
__all__ = ['paper_list_from_reviewer', 'paper_list_from_source']


class Paper:
    def __init__(self, i, tp, tit, abstract, authors, journal, year, bib):
        self.ID = i
        self.Type = tp
        self.Title = tit
        self.Abstract = abstract
        self.Authors = authors
        self.Journal = journal
        self.Year = year
        self.Bib = bib
        self.Attributes = dict()
        self.Tags = set()
        self.Status = 'None'
        self.DropReason = None

    def append_tags(self, tag):
        self.Tags.add(tag)

    def __setitem__(self, key, value):
        self.Attributes[key] = value

    def __getitem__(self, item):
        return self.Attributes[item]

    def __repr__(self):
        return 'Paper_{}, {}, {}, {}'.format(self.Authors, self.Year, self.Title, self.Journal)

    def data_json(self):
        js = {
            'ID': self.ID,
            'Type': self.Type,
            'Journal': self.Journal,
            'Year': self.Year,
            'Tags': ','.join(self.Tags),
            'Status': self.Status,
        }
        if 'Out' in self.Status:
            js['DropReason'] = self.DropReason

        js.update(self.Attributes)
        return js

    def to_json(self):
        return {
            'ID': self.ID,
            'Type': self.Type,
            'Journal': self.Journal,
            'Title': self.Title,
            'Authors': self.Authors,
            'Abstract': self.Abstract,
            'Year': self.Year,
            'Bib': self.Bib,
            'Tags': ','.join(self.Tags),
            'Status': self.Status,
            'DropReason': self.DropReason,
            'Attributes': self.Attributes
        }

    @staticmethod
    def from_json(js):
        paper = Paper.from_entry(js['Bib'])
        paper.Status = js['Status']
        paper.Tags = set(js['Tags'].split(','))
        paper.DropReason = js['DropReason']
        paper.Attributes.update(js['Attributes'])
        return paper

    @staticmethod
    def from_entry(ent):
        return Paper(
            i=ent['ID'],
            tp=ent['ENTRYTYPE'],
            tit=ent['title'],
            abstract=ent['abstract'] if 'abstract in ent' else '',
            authors=ent['author'],
            journal=ent['journal'] if 'journal' in ent else ent['booktitle'],
            year=int(ent['year']),
            bib=ent
        )


class PaperList:
    def __init__(self, name, papers, forms, exc=None):
        self.Name = name
        self.Papers = papers
        self.Papers.sort(key=lambda x: (x.Authors, x.Year))
        self.Forms = forms
        self.ExclusionTags = exc if exc else ['X Topic']

    def to_json(self):
        return {
            'Papers': [paper.to_json() for paper in self.Papers],
            'Forms': self.Forms.to_json(),
            'Exclusions': self.ExclusionTags
        }

    def id_list(self, status='None', tags=None, exclusive=False):
        if exclusive:
            papers = [paper for paper in self.Papers if paper.Status == status]
        else:
            papers = [paper for paper in self.Papers if in_status(paper.Status, status)]

        if tags:
            for tag in tags:
                papers = [paper for paper in papers if tag in paper.Tags]

        papers.sort(key=lambda x: (Status.index(x.Status), x.Authors, x.Year))
        return [paper.ID for paper in papers]

    def update_form(self, path):
        if path.endswith('.json'):
            with open(path, 'r') as f:
                js = json.load(f)
        else:
            raise TypeError('Not json')
        self.Forms = PaperForm.from_json(js)

    def __getitem__(self, item):
        try:
            return self.Papers[int(item)]
        except ValueError:
            for paper in self.Papers:
                if paper.ID == item:
                    return paper
        return self.Papers[0]

    def __len__(self):
        return len(self.Papers)

    def save_bib(self, path):
        bib = [paper.Bib for paper in self.Papers]
        output_bib(bib, path)

    def get_bib_string(self, abstract=False):
        bib = [paper.Bib for paper in self.Papers]
        return get_bib_string(bib, keep_abstract=abstract)

    def get_select_bib_string(self, selected, abstract=False):
        bib = [paper.Bib for paper in self.Papers if paper.ID in selected]
        return get_bib_string(bib, keep_abstract=abstract)

    def get_data(self):
        return [p.data_json() for p in self.Papers]

    def save(self, path):
        if not path.endswith('.reviewer'):
            path = '{}.reviewer'.format(path)

        with open(path, 'w') as f:
            json.dump(self.to_json(), f)


def paper_list_from_source(path_bib, path_form, abbr, name=None):
    bib = load_bib(path_bib, abbr)

    papers = list()
    for ent in bib.entries:
        try:
            papers.append(Paper.from_entry(ent))
        except KeyError:
            continue

    if path_form.endswith('.json'):
        with open(path_form, 'r') as f:
            js = json.load(f)
    else:
        raise TypeError('Not json')
    form = PaperForm.from_json(js)
    if not name:
        name = "{}_{}".format(
            path_bib.split('/')[-1].split('.')[0],
            path_form.split('/')[-1].split('.')[0]
        )
    return PaperList(name, papers, form)


def paper_list_from_reviewer(path):
    with open(path, 'r') as file:
        js = json.load(file)

    papers = [Paper.from_json(ent) for ent in js['Papers']]
    form = PaperForm.from_json(js['Forms'])
    if 'Exclusions' in js:
        exc = list(js['Exclusions'])
    else:
        exc = None

    name = path.split('/')[-1].split('.')[0]
    return PaperList(name, papers, form, exc)
