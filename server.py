from flask import Flask, render_template, request, redirect
from wiki_linkify import wiki_linkify
import pg
import markdown
import datetime

# is our current format with the title in layout.html the best way ? -----

app = Flask('Wiki')
db = pg.DB(dbname='wiki_db')

# unfinished capitalize title function


def cap_title(string):
    result = ''
    title = string.split()
    multiple = False
    for word in title:
        if multiple == True:
            result += ' '
        result += word.capitalize()
        multiple = True
    return result

# prevent users from writing script tags


def anti_script(content):
    edited = content.replace('<script>', '&lt;script&gt;').replace(
        '</script>', '&lt;/script&gt;')
    return edited


@app.route('/')
def home_page():
    return render_template(
        'homepage.html',
        title=cap_title('Wiki home')
    )


@app.route('/all_pages')
def show_all():
    query = db.query('select title from pages')
    results_list = query.namedresult()
    return render_template(
        'all_pages.html',
        title="All Pages",
        results_list=results_list
    )


@app.route('/<page_name>')
def view_page(page_name):
    query = db.query('''
        select title, page_content
        from pages
        where title = $1
        ''', page_name)
    results_list = query.namedresult()
    if len(results_list) > 0:
        page_content = results_list[0].page_content
        page_content = page_content.replace('<', '&lt;').replace('>', '&gt;')
        return render_template(
            'view_page.html',
            title=page_name,
            page_name=page_name,
            page_content=markdown.markdown(wiki_linkify(page_content))
        )
    else:
        return render_template(
            'placeholder.html',
            title="No Title",
            page_name=page_name
        )


@app.route('/<page_name>/edit')
def edit_page(page_name):
    query = db.query('''
        select *
        from pages
        where title = $1
        ''', page_name)

    results_list = query.namedresult()
    if len(results_list) > 0:
        db.insert(
            'history',
            title=page_name,
            page_content=results_list[0].page_content,
            last_modified=results_list[0].last_modified,
            last_author=results_list[0].last_author
        )
        return render_template(
            'edit_page.html',
            title="Edit Page",
            page_name=page_name,
            page_content=results_list[0].page_content,
            page_id=results_list[0].id
        )
    else:
        return render_template(
            'edit_page.html',
            title="Edit Page",
            page_name=page_name
        )


@app.route('/<page_name>/save', methods=['POST'])
def save_page(page_name):
    title = page_name
    #page_content = anti_script(request.form.get('content'))
    page_content = request.form.get('content')
    page_id = request.form.get('id')
    if page_id != '':
        db.update(
            'pages',
            {
                'id': page_id,
                'page_content': page_content,
                'last_modified': datetime.datetime.now()
            }
        )
    else:
        db.insert(
            'pages',
            title=title,
            page_content=page_content

        )
    return redirect('/%s' % title)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
