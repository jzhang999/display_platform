import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_from_directory)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('categories', __name__)


@bp.route('/categories')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, product_name, description, created, author_id, username, pic_name'
        ' FROM product p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('categories/index.html', posts=posts)