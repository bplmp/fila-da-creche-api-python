# -*- coding: UTF-8 -*-

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from flask import Flask, jsonify, abort, request, make_response, url_for
# from flask_httpauth import HTTPBasicAuth
from tenacity import retry, wait_fixed
from geojson import Feature, Point, FeatureCollection

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DBNAME = os.getenv("POSTGRES_DBNAME")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")

# # HACK:
from flask_cors import CORS, cross_origin

app = Flask(__name__, static_url_path = "")

# # HACK:
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

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

# wait to see if db is up, 5 seconds between retries
@retry(wait=wait_fixed(5))
def init_api():
    try:
        con = psycopg2.connect(dbname=POSTGRES_DBNAME, user=POSTGRES_USER, host=POSTGRES_HOST, password=POSTGRES_PASSWORD)
    except Exception as e:
        print("I am unable to connect to the database.")
        print(e)
        abort(400)

    # cur = con.cursor()
    cur = con.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

    # 2000 meters
    searchRadius = 2000

    @app.errorhandler(400)
    def not_found(error):
        return make_response(jsonify( { 'error': 'Bad request' } ), 400)

    @app.errorhandler(404)
    def not_found(error):
        return make_response(jsonify( { 'error': 'Not found' } ), 404)

    @app.route('/', methods = ['GET'])
    # @auth.login_required
    def get_hello():
        return 'hello world'

    # http://localhost:5000/v1/schools/id/091383
    @app.route('/v1/schools/id/<string:cd_unidade_educacao>', methods = ['GET'])
    # @auth.login_required
    def get_school_id(cd_unidade_educacao):
        try:
            if validate_school_id_request(cd_unidade_educacao):
                cur.execute(f"""SELECT *
                FROM unidades_educacionais_ativas_endereco_contato
                WHERE cd_unidade_educacao = '{cd_unidade_educacao}'""")
                schools = cur.fetchall()
                return jsonify( { 'results': schools } )
            else:
                abort(400)
        except Exception as e:
            print(e)
            abort(400)

    # sample url
    # http://localhost:5000/v1/schools/radius/-46.677023599999984/-23.5814295
    @app.route('/v1/schools/radius/<string:lon>/<string:lat>', methods = ['GET'])
    # @auth.login_required
    def get_schoolradius(lat, lon):
        try:
            if validate_wait_request(lat, lon):
                cur.execute(f"""SELECT *
                FROM unidades_educacionais_ativas_endereco_contato
                WHERE ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326), {searchRadius})""")
                rowsSchools = cur.fetchall()
                return jsonify( { 'results': rowsSchools } )
            else:
                abort(400)
        except Exception as e:
            print(e)
            abort(400)

    # sample url
    # http://localhost:5000/v1/schools/wait
    @app.route('/v1/schools/wait', methods = ['GET'])
    # @auth.login_required
    def get_schoolwait():
        try:
            cur.execute(f"""
            SELECT c.cd_unidade_educacao,
                   c.nm_unidade_educacao,
                   c.tp_escola,
                   c.sg_tp_escola,
                   c.cd_latitude,
                   c.cd_longitude,
                   c.geom,
                   v.vagas_cd_serie_1,
                   v.vagas_cd_serie_4,
                   v.vagas_cd_serie_27,
                   v.vagas_cd_serie_28,
                   solicit_1,
                   solicit_4,
                   solicit_27,
                   solicit_28
            from unidades_educacionais_infantil_vagas_serie as v
            left join unidades_educacionais_ativas_endereco_contato as c
            ON c.cd_unidade_educacao = v.cd_unidade_educacao
            left join
            (SELECT
                cd_unidade_educacao,
                SUM(CASE WHEN cd_serie_ensino = 1 then 1 ELSE NULL END) as solicit_1,
                SUM(CASE WHEN cd_serie_ensino = 4 then 1 ELSE NULL END) as solicit_4,
                SUM(CASE WHEN cd_serie_ensino = 27 then 1 ELSE NULL END) as solicit_27,
                SUM(CASE WHEN cd_serie_ensino = 28 then 1 ELSE NULL END) as solicit_28
              FROM solicitacao_matricula_grade_dw
              GROUP BY cd_unidade_educacao) as solicit
            on v.cd_unidade_educacao::integer = solicit.cd_unidade_educacao
            where (
              v.vagas_cd_serie_1 IS NOT NULL OR
              v.vagas_cd_serie_4 IS NOT NULL OR
              v.vagas_cd_serie_27 IS NOT NULL OR
              v.vagas_cd_serie_28 IS NOT NULL
            )
            """)
            rowsSchoolsWait = cur.fetchall()

            features = []

            for row in rowsSchoolsWait:
                properties = row
                feature = Feature(geometry=Point((row["cd_longitude"], row["cd_latitude"])), properties=properties)
                features.append(feature)

            collection = FeatureCollection(features)

            return jsonify(collection)
        except Exception as e:
            print(e)
            abort(400)

    # sample url
    # http://localhost:5000/v1/schools/radius/wait/-46.677023599999984/-23.5814295/27
    @app.route('/v1/schools/radius/wait/<string:lon>/<string:lat>/<int:cd_serie>', methods = ['GET'])
    # # HACK:
    # @cross_origin()
    # @auth.login_required
    def get_schoolradiuswait(lat, lon, cd_serie):
        try:
            # FIXME: validate by bouding box too
            if validate_wait_request(lat, lon, cd_serie):
                cur.execute(f"""
                SELECT count(DISTINCT cd_solicitacao_matricula_random) FROM unidades_educacionais_ativas_endereco_contato AS u
                LEFT JOIN solicitacao_matricula_grade_dw AS s
                ON u.cd_unidade_educacao::integer = s.cd_unidade_educacao
                WHERE ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326), {searchRadius})
                  AND s.cd_serie_ensino = {cd_serie}
                """)
                rowsWait = cur.fetchall()
                cur.execute(f"""
                SELECT dt_solicitacao as updated_at
                FROM solicitacao_matricula_grade_dw_atualizacao
                """)
                rowsUpdated = cur.fetchall()
                cur.execute(f"""
                SELECT *, (ST_Distance(geom::geography, ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326)) / 1000) as distance FROM unidades_educacionais_ativas_endereco_contato AS u
                LEFT JOIN unidades_educacionais_infantil_vagas_serie as v
                ON u.cd_unidade_educacao = v.cd_unidade_educacao
                WHERE ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326), {searchRadius})
                  AND v.vagas_cd_serie_{cd_serie} IS NOT NULL
                ORDER BY distance
                """)
                rowsSchools = cur.fetchall()
                results = {'wait': rowsWait[0]['count'], 'wait_updated_at': rowsUpdated[0]['updated_at'], 'schools': rowsSchools}
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

    def validate_school_id_request(id):
        if float(id):
            return True
        else:
            return False

init_api()

if __name__ == '__main__':
    # app.run(debug = True)
    app.run(host='0.0.0.0', debug=True)
