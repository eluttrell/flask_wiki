from flask import Flask, render_template, request, redirect, session, flash
from wiki_linkify import wiki_linkify
import pg
import markdown
import datetime

# is our current format with the title in layout.html the best way ? -----

app = Flask('Wiki')
db = pg.DB(dbname='wiki_db')
app.secret_key = 'happy_slappy'

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


@app.route('/page_search', methods=['POST'])
def page_search():
    page_name = request.form.get('page_search')
    query = db.query('select title from pages where title = $1', page_name)
    results_list = query.namedresult()
    if len(results_list) > 0:
        return redirect('/%s' % page_name)
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
        where title = $1;
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


@app.route('/signup')
def signup():
    return render_template(
        'signup.html',
        title='Signup'
    )


# @app.route('/submit_signup', methods=['POST'])
# def submit_signup():
#     username = request.form.get('username')
#     password = request.form.get('password')
#     print username, password
#     query = db.query(
#         "select name from wiki_user where name = $1", username)
#     results_list = query.namedresult()
#     if len(results_list) == 0:
#         print "here we are"
#         db.query(
#             '''insert into wiki_user (name, password) values ($1, $2)''', username, password)
#         return redirect('/')
#     else:
#         return redirect('/signup')
#         flash("Username already exists!")


@app.route('/login')
def login():
    return render_template(
        'login.html',
        title='Login'
    )


@app.route('/logout')
def logout():
    del session['username']

    return redirect('/')


@app.route('/submit_login', methods=['POST'])
def submit_login():
    username = request.form.get('username')
    password = request.form.get('password')
    action = request.form.get('action')
    query = db.query("select * from wiki_user where name = $1", username)
    results_list = query.namedresult()
    if len(results_list) > 0 and action == 'login':
        user = results_list[0]
        if user.password == password:
            session['username'] = user.name
            # flash("'%s', you have successfully logged in.'" % username)
            return redirect('/')
        else:
            return redirect('/login')
    elif action == 'signup':
        print "here we are"
        db.query(
            '''insert into wiki_user (name, password) values ($1, $2)''', username, password)
        session['username'] = username
        return redirect('/')
    else:
        return redirect('/signup')


if __name__ == '__main__':
    app.run(debug=True)
# , host='0.0.0.0' Use this line to make webpage accesible to others
