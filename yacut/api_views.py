import re
from http import HTTPStatus

from flask import jsonify, request

from . import app, db
from .error_handlers import InvalidAPIUsage
from .models import URLMap
from .views import get_unique_short_id, is_short_id_unique


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_original_link(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    if url_map is None:
        raise InvalidAPIUsage('Указанный id не найден', HTTPStatus.NOT_FOUND)
    return jsonify({'url': url_map.original}), HTTPStatus.OK


@app.route('/api/id/', methods=['POST'])
def add_url_map():
    data = request.get_json()
    if data is None:
        raise InvalidAPIUsage('Отсутствует тело запроса')
    url = data.get('url')
    custom_id = data.get('custom_id')
    if url is None:
        raise InvalidAPIUsage('\"url\" является обязательным полем!')
    elif custom_id is None or custom_id == '':
        data['custom_id'] = get_unique_short_id()
    elif not is_short_id_unique(custom_id):
        raise InvalidAPIUsage(f'Имя \"{custom_id}\" уже занято.')
    elif (not re.match(r'^[a-zA-Z0-9]{1,16}$', custom_id) or
          len(custom_id) < 1 or len(custom_id) > 16):
        raise InvalidAPIUsage('Указано недопустимое имя для короткой ссылки')
    url_map = URLMap(original=url, short=data.get('custom_id'))
    db.session.add(url_map)
    db.session.commit()
    return jsonify(url_map.to_dict()), HTTPStatus.CREATED
