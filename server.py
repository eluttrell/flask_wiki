from flask import Flask, render_template, request, redirect
import pg

app = Flask('Wiki')
db = pg.DB(dbname = 'wiki_db')

@app.route('/')
def home_page():
    return 'home'

@app.route('/<page_name>')
def view_page(page_name):
    query = db.query('''
        select title, page_content
        from page
        where title = '%s'
        ''' % page_name).namedresult()
    if len(query) > 0:
        return render_template(
            'view_page.html',
            title = page_name,
            page_name = page_name,
            page_content = query[0].page_content
        )
    else:
        return render_template(
            'placeholder.html',
            title="No Title",
            page_name = page_name
        )

@app.route('/<page_name>/edit')
def edit_page(page_name):
    query = db.query('''
        select id, page_content
        from page
        where title = '%s';
        ''' % page_name).namedresult()[0]
    return render_template(
        'edit_page.html',
        title="Edit Page",
        page_name = page_name,
        page_content = query.page_content,
        page_id = query.id
    )

@app.route('/<page_name>/save', methods=['POST'])
def save_page(page_name):
    title = page_name
    page_content = request.form.get('content')
    page_id = request.form.get('id')
    if page_id > 0:
        db.update(
            'page',
            {
                'id': page_id,
                'page_content': page_content
            }
        )
    else:
        db.insert(
            'page',
            title = title,
            page_content = page_content
        )
    return redirect('/')



if __name__ == '__main__':
    app.run(debug = True)
