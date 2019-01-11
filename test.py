from flask import Flask, request
from flask import render_template
from flask import redirect


app = Flask(__name__)

Tags = ['A', 'B', 'C']


@app.route('/exclusion')
def tags_list():
    tags = Tags
    return render_template('Tags.html', tags=tags)


@app.route('/exclusion/add', methods=['POST'])
def add_tag():
    content = request.form['content']
    if not content or content in Tags:
        return redirect('/')

    Tags.append(content)
    return redirect('/')


@app.route('/exclusion/<tag_id>')
def delete_tag(tag):
    Tags.remove(tag)
    return redirect('/')


if __name__ == '__main__':
    app.run()
