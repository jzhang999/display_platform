import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_from_directory)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

# / means the first page?
@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, product_name, description, created, author_id, username, pic_name'
        ' FROM product p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory("./flaskr/static/uploaded_files", filename)


@bp.route('/product_create', methods=('GET', 'POST'))
@login_required
def product_create():
    if request.method == 'POST':
        product_name = request.form['product_name']
        description = request.form['description']
        cat = request.form['cat']

        # for saving the pics
        pic = request.files['file']
        pic_name = pic.filename
        pic.save(os.path.join("./flaskr/static/uploaded_files", pic_name))

        error = None

        if not product_name:
            error = 'Product name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO product (product_name, description, author_id, pic_name, category)'
                ' VALUES (?, ?, ?, ?, ?)',
                (product_name, description, g.user['id'], pic_name, cat,)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/product_create.html')


@bp.route('/cat_create', methods=('GET', 'POST'))
@login_required
def cat_create():
    if request.method == 'POST':
        cat_name = request.form['cat_name']
        error = None

        if not cat_name:
            error = 'Category name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO category (cat_name)'
                ' VALUES (?)',
                (cat_name,)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/cat_create.html')


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, product_name, description, created, author_id, username, pic_name'
        ' FROM product p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

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
            error = 'Product name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE product SET product_name = ?, description= ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM product WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))