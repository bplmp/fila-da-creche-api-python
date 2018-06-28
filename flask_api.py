# -*- coding: UTF-8 -*-

from flask import Flask, jsonify, abort, request, make_response, url_for
# from flask_httpauth import HTTPBasicAuth

app = Flask(__name__, static_url_path = "")
# auth = HTTPBasicAuth()

# @auth.get_password
# def get_password(username):
#     if username == 'miguel':
#         return 'python'
#     return None

# @auth.error_handler
# def unauthorized():
#     return make_response(jsonify( { 'error': 'Unauthorized access' } ), 403)
#     # return 403 instead of 401 to prevent browsers from displaying the default auth dialog

import psycopg2
from psycopg2.extras import RealDictCursor

import credentials

try:
    con = psycopg2.connect(dbname=credentials.dbname, user=credentials.user, host=credentials.host, password=credentials.password)
except Exception as e:
    print("I am unable to connect to the database.")
    print(e)
    abort(400)

# cur = con.cursor()
cur = con.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

searchRadius = 2000

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify( { 'error': 'Bad request' } ), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)

@app.route('/v1/schoolradius/<string:lat>/<string:lon>', methods = ['GET'])
# @auth.login_required
def get_schoolradius(lat, lon):
    try:
        if validate_wait_request(lat, lon):
            cur.execute(f"""SELECT *
            FROM unidades_educacionais_ativas
            WHERE ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326), {searchRadius})""")
            rowsSchools = cur.fetchall()
            return jsonify( { 'results': rowsSchools } )
        else:
            abort(400)
    except Exception as e:
        print(e)
        abort(400)

# sample url
@app.route('/v1/schoolradiuswait/<string:lat>/<string:lon>/<int:cd_serie>', methods = ['GET'])
# @auth.login_required
def get_schoolradiuswait(lat, lon, cd_serie):
    try:
        # FIXME: validate by bouding box too
        if validate_wait_request(lat, lon, cd_serie):
            cur.execute(f"""
            SELECT count(DISTINCT cd_solicitacao_matricula_random) FROM unidades_educacionais_ativas AS u
            LEFT JOIN solicitacao_matricula_grade_dw AS s
            ON u.cd_unidade_educacao::integer = s.cd_unidade_educacao
            WHERE ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326), {searchRadius})
              AND s.cd_serie_ensino = {cd_serie}
            """)
            rowsWait = cur.fetchall()
            # FIXME: fix filter by schools; right now it only shows if there is some wait for that cd_serie, but maybe there's no wait
            cur.execute(f"""
            SELECT count(DISTINCT u.cd_unidade_educacao) FROM unidades_educacionais_ativas AS u
            LEFT JOIN solicitacao_matricula_grade_dw AS s
            ON u.cd_unidade_educacao::integer = s.cd_unidade_educacao
            WHERE ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326), {searchRadius})
              AND s.cd_serie_ensino = {cd_serie}
            """)
            rowsSchools = cur.fetchall()
            results = {'wait': rowsWait[0]['count'], 'schools': rowsSchools[0]['count']}
            return jsonify( { 'results': results } )
        else:
            abort(400)
    except Exception as e:
        print(e)
        abort(400)

def validate_wait_request(lat, lon, cd_serie=1):
    if float(lat) and float(lon) and (cd_serie in [1, 4, 27, 28]):
        return True
    else:
        return False

if __name__ == '__main__':
    app.run(debug = True)
