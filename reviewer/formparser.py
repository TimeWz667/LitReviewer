import wtforms.fields as fld
from collections import OrderedDict


__author__ = 'TimeWz667'
__all__ = ['json_to_questions']


def json_to_questions(js):
    questions = OrderedDict()

    for v in js:
        k = v['Name']
        if v['Type'] == 'Bool':
            item = fld.BooleanField(v['Text'], false_values='n')
        elif v['Type'] == 'Options':
            choices = [(i, opt) for i, opt in enumerate(v['Value'])]
            item = fld.SelectField(v['Text'], choices=choices)
        else:
            item = fld.TextAreaField(v['Text'])

        questions[k] = item

    return questions
