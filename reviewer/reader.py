import pandas as pd
__author__ = 'TimeWz667'


class Reviewer:
    def __init__(self, name):
        self.Name = name
        self.PaperList = None
        self.Selected = None
        self.SelectedTags = []
        self.SelectedStatus = 'None'
        self.SelectedStatusExclusive = False

    def set_paper_list(self, pl):
        self.PaperList = pl
        self.Selected = self.PaperList.id_list()

    def detach_paper_list(self):
        self.PaperList = None
        self.Selected = None
        self.SelectedTags = []
        self.SelectedStatus = 'None'

    def release_selector(self):
        self.Selected = self.PaperList.id_list()
        self.SelectedTags = []
        self.SelectedStatus = 'None'
        self.SelectedStatusExclusive = {}

    def select_all(self, state, tags, exclusive=False):
        self.SelectedStatus = state
        self.SelectedTags = tags
        self.SelectedStatusExclusive = exclusive
        self.Selected = self.PaperList.id_list(state, [], exclusive=exclusive)

    def get_selected_papers(self):
        return [self.PaperList[p] for p in self.Selected]

    def get_paper_by_id(self, paper_id):
        return self.PaperList[paper_id]

    def get_paper_linker(self, paper_id):
        i = self.Selected.index(paper_id)
        res = {'index': i}
        if i > 0:
            res['previous'] = self.Selected[i - 1]
        if i < (len(self.Selected) - 1):
            res['next'] = self.Selected[i + 1]
        return res

    def get_exclusion_tags(self):
        return self.PaperList.ExclusionTags

    def get_bib_all(self):
        return self.PaperList.get_bib_string()

    def get_bib_selected(self):
        return self.PaperList.get_select_bib_string(self.Selected)

    def get_data_json(self):
        return self.PaperList.get_data()

    def get_data_csv(self):
        return pd.DataFrame(self.PaperList.get_data()).to_csv()
