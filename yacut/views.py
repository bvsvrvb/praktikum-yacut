import random
import string

from flask import flash, redirect, render_template, url_for

from . import app, db
from .models import URLMap
from .forms import URLMapForm


def is_short_unique(custom_id):
    if URLMap.query.filter_by(short=custom_id).first():
        return False
    return True


def get_unique_short_id():
    chars = string.ascii_letters + string.digits
    while True:
        short_link = ''.join(random.choice(chars) for _ in range(6))
        if is_short_unique(short_link):
            return short_link


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = URLMapForm()
    if form.validate_on_submit():
        if form.custom_id.data:
            if not is_short_unique(form.custom_id.data):
                flash('Такая короткая ссылка уже занята')
                return render_template('index.html', form=form)
            custom_id = form.custom_id.data
        else:
            custom_id = get_unique_short_id()
        url_map = URLMap(
            original=form.original_link.data,
            short=custom_id
        )
        db.session.add(url_map)
        db.session.commit()
        flash('Ваша новая ссылка готова:')
        return render_template(
            'index.html',
            form=form,
            link=url_for('redirect_view', custom_id=custom_id, _external=True)
        )
    return render_template('index.html', form=form)


@app.route('/<string:custom_id>')
def redirect_view(custom_id):
    url_map = URLMap.query.filter_by(short=custom_id).first_or_404()
    return redirect(url_map.original)
