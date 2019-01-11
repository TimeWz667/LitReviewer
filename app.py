from flask import Flask, request, render_template, send_file, session, redirect, url_for, jsonify, Response
import reviewer

__author__ = 'TimeWz667'

abbreviations = ['HIV', 'STD', 'NCD', 'SD', 'DES', 'ABM', 'EBM', 'BMC', 'I', 'II', 'OR',
                 'SIR', 'SID', 'SEIR', 'SIRS', 'ODE', 'PDE', 'SDE',
                 'IEEE', 'PLOS', 'WSC', 'JAIDS', 'RIVF', '(RIVF)', '(WSC)']


out_reasons = ['X Topic', 'X Paper Type', 'X Human', 'X Between human',
               'X ABM', 'X EBM',
               'X Interaction', 'X Sim or Imp']


class ReviewerFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        block_start_string='<%',
        block_end_string='%>',
        variable_start_string='<{',
        variable_end_string='}>',
        comment_start_string='<#',
        comment_end_string='#>'
    ))

    def __init__(self, name, **kwargs):
        Flask.__init__(self, name, **kwargs)
        self.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


app = ReviewerFlask(__name__)
app.secret_key = 'han han key'


def check_info():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session.get('username')
    if username not in reviewer.Reviewers:
        del session['username']
        return redirect(url_for('login'))
    user = reviewer.Reviewers[username]
    if not user.PaperList:
        return redirect(url_for('select_project'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['UserName']
        # todo validate name
        session['username'] = username
        reviewer.login_reviewer(username)

        return redirect(url_for('select_project'))
    form = reviewer.LoginForm()
    return render_template('Login.html', form=form)


@app.route('/logout', methods=['GET'])
def logout():
    username = session.get('username')
    reviewer.logout_reviewer(username)
    return redirect(url_for('login'))


@app.route('/project', methods=['GET'])
def select_project():
    if 'username' not in session:
        return redirect(url_for('login'))
    reviewer.detach_project(session.get('username'))

    new_form = reviewer.NewProjectForm()
    new_form.BibFile.choices = reviewer.list_bib()
    new_form.FormFile.choices = reviewer.list_form()

    load_form = reviewer.LoadProjectForm()
    load_form.ProjectFile.choices = reviewer.list_project()

    return render_template('Project.html', new_form=new_form, load_form=load_form)


@app.route('/project/load', methods=['POST'])
def load_project():
    form = reviewer.LoadProjectForm()
    if form.ProjectUpload.has_file():
        _, pro = reviewer.upload_bib(form.BibUpload.data)
    else:
        pro = form.ProjectFile.data

    pl_name = reviewer.load_project(pro)

    username = session.get('username')
    reviewer.attach_project(username, pl_name)
    return redirect(url_for('index'))


@app.route('/project/new', methods=['POST'])
def new_project():
    form = reviewer.NewProjectForm()
    if form.BibUpload.has_file():
        _, bib = reviewer.upload_bib(form.BibUpload.data)
    else:
        bib = form.BibFile.data

    if form.FormUpload.has_file():
        _, questions = reviewer.upload_form(form.FormUpload.data)
    else:
        questions = form.FormFile.data

    pl_name = reviewer.new_project(form.ProjectName.data, bib, questions, abbreviations)

    username = session.get('username')
    reviewer.attach_project(username, pl_name)
    return redirect(url_for('index'))


@app.route('/')
def index():
    check = check_info()
    if check:
        return check
    username = session.get('username')
    pro = reviewer.get_project_name(username)
    pl = reviewer.find_papers(username)
    sts = reviewer.summarise_paper_status(username)
    return render_template('PaperList.html', title='List of papers', user=username, obj=pro, sts=sts,
                           papers=pl)


@app.route('/paper/<paper_id>', methods=['GET', 'POST'])
def read_paper(paper_id):
    check = check_info()
    if check:
        return check
    username = session.get('username')

    if request.method == 'POST':
        reviewer.fetch_data(username, paper_id, request.form)
        if 'btn' in request.form:
            if request.form['btn'] == 'Save':
                pass
            elif request.form['btn'] == 'Approve':
                reviewer.approve_paper(username, paper_id)
            elif request.form['btn'] == 'Disapprove':
                reviewer.disapprove_paper(username, paper_id)
        elif 'btn-drop' in request.form:
            reviewer.drop_paper(username, paper_id, request.form['btn-drop'])

        reviewer.save_project(username)

    sts = reviewer.summarise_paper_status(username)
    sel = reviewer.find_paper(username, paper_id)
    hp = 'previous' in sel
    prv = '/paper/{}'.format(sel['previous']) if hp else '/'
    hn = 'next' in sel
    nxt = '/paper/{}'.format(sel['next']) if hn else '/'
    return render_template('Paper.html', title=paper_id, user=username, obj=paper_id, sts=sts,
                           paper=sel['paper'], form=sel['form'], id=paper_id, out_reasons=out_reasons,
                           has_previous=hp, previous=prv,
                           has_next=hn, next=nxt)


@app.route('/filter/<status>')
def filter_status(status):
    username = session.get('username')
    reviewer.filter_papers(username, status, [])
    return redirect(url_for('index'))


@app.route('/summary')
def summary():
    check = check_info()
    if check:
        return check
    username = session.get('username')
    sts = reviewer.summarise_paper_status(username)
    return render_template('Summary.html', title='Summary', user=username, obj='summary', sts=sts)


@app.route('/figure/wordcloud/<paper_id>')
def abstract_wc(paper_id):
    username = session.get('username')

    txt = reviewer.find_paper(username, paper_id, detail=False).Abstract

    return send_file(reviewer.make_word_cloud(txt), mimetype='image/png')


@app.route('/figure/wordcloud/')
def abstract_wc_all():
    username = session.get('username')

    txt = ' '.join(p.Abstract for p in reviewer.find_papers(username))
    return send_file(reviewer.make_word_cloud(txt), mimetype='image/png')


@app.route('/output/csv')
def output_csv():
    username = session.get('username')
    pro = reviewer.get_project_name(username)
    csv = reviewer.output_result_csv(username)

    return Response(
        csv,
        mimetype='text/csv',
        headers={'Content-disposition':
                 'attachment; filename={}_{}.csv'.format(username, pro)})


@app.route('/output/json')
def output_json():
    username = session.get('username')
    pro = reviewer.get_project_name(username)
    json = str(jsonify(reviewer.output_result_json(username)))

    return Response(
        json,
        mimetype='application/json',
        headers={'Content-disposition':
                 'attachment; filename={}_{}.json'.format(username, pro)})


@app.route('/output/bib')
def output_bib():
    username = session.get('username')
    pro = reviewer.get_project_name(username)
    bib = reviewer.output_bib(username)

    return Response(
        bib,
        mimetype='text/bib',
        headers={'Content-disposition':
                 'attachment; filename={}_{}.bib'.format(username, pro)})


@app.route('/output/sel_bib')
def output_sel_bib():
    username = session.get('username')
    pro = reviewer.get_project_name(username)
    bib = reviewer.output_select_bib(username)

    return Response(
        bib,
        mimetype='text/bib',
        headers={'Content-disposition':
                 'attachment; filename={}_{}.bib'.format(username, pro)})


if __name__ == '__main__':
    app.run(port=300)
