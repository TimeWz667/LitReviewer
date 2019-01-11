from .status import *
from .paper import *
from .form import *
from .reader import Reviewer
from .summary import *
import os


__author__ = 'TimeWz667'


FOLDERS = {
    'Bib': 'data_bib/',
    'Form': 'data_form/',
    'Data': 'data/'
}


Reviewers = dict()
PaperLists = dict()


def list_bib():
    files = [f for f in os.listdir('./data_bib') if f.endswith('.bib')]
    files = [(f.split('.bib')[0], f) for f in files]
    return files


def list_form():
    files = [f for f in os.listdir('./data_form') if f.endswith('.json')]
    files = [(f.split('.json')[0], f) for f in files]
    return files


def list_project():
    files = [f for f in os.listdir('./data') if f.endswith('.reviewer')]
    files = [(f.split('.reviewer')[0], f) for f in files]
    return files


def new_project(name, file_bib, file_form, abbr):
    file_bib = file_bib if file_bib.endswith('.bib') else file_bib + '.bib'
    file_form = file_form if file_form.endswith('.json') else file_form + '.json'

    path_bib = '{}{}'.format(FOLDERS['Bib'], file_bib)
    path_form = '{}{}'.format(FOLDERS['Form'], file_form)

    name = name if name else None

    pl = paper_list_from_source(name=name, path_bib=path_bib, path_form=path_form, abbr=abbr)
    while pl.Name in PaperLists:
        pl.Name = "{}r".format(pl.Name)

    PaperLists[pl.Name] = pl
    path = os.path.join(FOLDERS['Data'], pl.Name)
    pl.save(path)
    return pl.Name


def attach_project(user, pl_name):
    pl = PaperLists[pl_name]
    Reviewers[user].set_paper_list(pl)


def detach_project(user):
    Reviewers[user].detach_paper_list()


def load_project(file):
    path = os.path.join(FOLDERS['Data'], file) + '.reviewer'
    pl = paper_list_from_reviewer(path)
    PaperLists[pl.Name] = pl
    return pl.Name


def upload_bib(file):
    filename = file.filename
    name = filename.split('.bib')[0]
    file.save(os.path.join(FOLDERS['Bib'], filename))
    return name, filename


def upload_form(file):
    filename = file.filename
    name = filename.split('.json')[0]
    file.save(os.path.join(FOLDERS['Form'], filename))
    return name, filename


def upload_project(file):
    filename = file.filename
    name = filename.split('.reviewer')[0]
    file.save(os.path.join(FOLDERS['Data'], filename))
    return name, filename


def login_reviewer(user):
    if user not in Reviewers:
        Reviewers[user] = Reviewer(user)


def logout_reviewer(user):
    detach_project(user)


def save_project(user):
    pl = Reviewers[user].PaperList
    path = '{}{}.reviewer'.format(FOLDERS['Data'], pl.Name)
    pl.save(path)


def output_bib(user):
    return Reviewers[user].get_bib_all()


def output_select_bib(user):
    return Reviewers[user].get_bib_selected()


def output_project(user):
    return Reviewers[user].PaperList.to_json()


def output_result_json(user):
    return Reviewers[user].get_data_json()


def output_result_csv(user):
    return Reviewers[user].get_data_csv()


def get_project_name(user):
    return Reviewers[user].PaperList.Name


def find_papers(user):
    return Reviewers[user].get_selected_papers()


def find_paper(user, paper_id, detail=True):
    reviewer = Reviewers[user]
    p = reviewer.get_paper_by_id(paper_id)
    if not detail:
        return p

    res = dict()
    res['paper'] = p
    res['form'] = reviewer.PaperList.Forms.new_form(p)
    res.update(reviewer.get_paper_linker(paper_id))
    return res


def fetch_data(user, paper_id, data):
    reviewer = Reviewers[user]
    pap = reviewer.get_paper_by_id(paper_id)
    reviewer.PaperList.Forms.fetch_data(data, pap)


def filter_papers(user, st, tags):
    reviewer = Reviewers[user]
    if st.startswith('ex'):
        ex = True
        st = st.split('ex ')[1]
    else:
        ex = False

    reviewer.select_all(st, tags, exclusive=ex)


def reset_selectors(user):
    reviewer = Reviewers[user]
    reviewer.release_selector()


def approve_paper(user, paper_id):
    reviewer = Reviewers[user]
    p = reviewer.get_paper_by_id(paper_id)
    p.Status = approve_status(p.Status)


def disapprove_paper(user, paper_id):
    reviewer = Reviewers[user]
    p = reviewer.get_paper_by_id(paper_id)
    p.Status = disapprove_status(p.Status)


def drop_paper(user, paper_id, drop_reason):
    reviewer = Reviewers[user]
    p = reviewer.get_paper_by_id(paper_id)
    p.Status = drop_status(p.Status)
    p.DropReason = drop_reason


def summarise_paper_status(user):
    ps = Reviewers[user].PaperList.Papers
    sts = [p.Status for p in ps]
    summary = summarise_status(sts)
    summary += [('ex ' + st, v) for st, v in summarise_status(sts, True) if 'Out' not in st]
    return summary
