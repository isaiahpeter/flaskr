from flask import (Blueprint,Flask, flash, g, redirect, render_template, request, url_for)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
bp = Blueprint('blog', __name__)


upload_folder = '/home/isaiah/myproject/flaskr/static/images'
allowed_extensions = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['upload_folder'] = upload_folder
img_folder = os.path.join('static', 'images')
app.config['upload_folder'] = img_folder
Flask_Logo = os.path.join(app.config['upload_folder'], 'isaiah_peter.jpg')

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
        ).fetchall()
    return render_template('blog/index.html', posts=posts, user_image=Flask_Logo)
   
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None
        
        if not title:
            error = 'Title is required.'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))
    return render_template('blog/create.html')
    
def get_post(id, check_author=True):
    post = get_db().execute(
        ' SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id, )
    ).fetchone()
    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))
    if check_author and post['author_id'] != g.user['id']:
        abort(403)
    return post
    
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None
        if not title:
            error = 'Title is required.'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))
    return render_template('blog/update.html', post=post)
    
@bp.route('/<int:id>delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
    


def get_detail(id, check_author=True):
    post = get_db().execute(
        ' SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id, )
    ).fetchone()
    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))
    #if check_author and post['author_id'] != g.user['id']:
        #abort(403)
    return post




@bp.route('/comment', methods=('GET', 'POST'))
@login_required
def comment():
    if request.method == 'POST':
        body = request.form['body']
        error = None
        
        if not body:
            error = 'Body is required.'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO comment ( body, author_id)'
                ' VALUES (?,?)',
                (body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))
    return render_template('blog/comments.html')

def get_comment():
    comment = get_db().execute(
        ' SELECT  body, created, author_id'
        ' from comment'
    ).fetchone()
    if comment is None:
        abort(404, "Post id {0} doesn't exist.".format(id))
    
    return comment


@bp.route('/<int:id>/detail', methods=('GET',))
#@login_required
def detail(id):
    post = get_detail(id)
    comment = get_comment()
    return render_template('blog/detail.html', post=post, comment=comment)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@bp.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['upload_folder'], filename))
            return redirect(url_for('blog.index', filename=filename))
    return render_template('blog/upload_file.html')