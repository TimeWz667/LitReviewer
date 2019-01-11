from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms.form import BaseForm
import wtforms.fields as fld
from .formparser import json_to_questions

__author__ = 'TimeWz667'
__all__ = ['PaperForm', 'LoginForm', 'NewProjectForm', 'LoadProjectForm']


class LoginForm(FlaskForm):
    UserName = fld.StringField('username')


class NewProjectForm(FlaskForm):
    BibFile = fld.SelectField('Bibtex file')
    FormFile = fld.SelectField('Appraisal Form file')
    BibUpload = FileField('Upload Bibtex file (.bibtex)')
    FormUpload = FileField('Upload appraisal file (.json)')
    ProjectName = fld.StringField('Project name')
    NewProject = fld.SubmitField('Create new project')


class LoadProjectForm(FlaskForm):
    ProjectFile = fld.SelectField('Project file')
    ProjectUpload = FileField('Upload project (.reviewer)')
    LoadProject = fld.SubmitField('Load project')


class PaperForm:
    def __init__(self, fs, js):
        self.Fields = fs
        self.Bool = [k for k, v in fs.items() if isinstance(v, fld.BooleanField)]
        self.JSON = js

    def new_form(self, paper=None):
        form = BaseForm(fields=self.Fields)
        form.process()
        if paper:
            self.inject_data(form, paper)
        return form

    def inject_data(self, form, paper):
        for k, v in paper.Attributes.items():
            if k in form:
                form[k].data = bool(v) if k in self.Bool else v

    def fetch_data(self, form, paper):
        for k, v in form.items():
            if k == 'btn':
                continue
            elif k in self.Bool:
                paper.Attributes[k] = True
            else:
                paper.Attributes[k] = v

    def to_json(self):
        return self.JSON

    @staticmethod
    def from_json(js):
        fs = json_to_questions(js)
        return PaperForm(fs, js)

    @staticmethod
    def from_txt(txt):
        js = {}
        # todo
        return PaperForm.from_json(js)
