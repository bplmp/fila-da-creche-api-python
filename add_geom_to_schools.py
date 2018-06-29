import psycopg2
import sys

import dotenv_variables

try:
    con = psycopg2.connect(dbname=dotenv_variables.POSTGRES_DBNAME, user=dotenv_variables.POSTGRES_USER, host=dotenv_variables.POSTGRES_HOST, password=dotenv_variables.POSTGRES_PASSWORD)
    cur = con.cursor()
    cur.execute("""ALTER TABLE unidades_educacionais_ativas_endereco_contato
    ADD COLUMN geom geometry(Point, 4326)""")
    cur.execute("""UPDATE unidades_educacionais_ativas_endereco_contato
    SET geom = ST_SetSrid(ST_MakePoint(cd_longitude, cd_latitude), 4326)""")
    con.commit()
    con.close()
except Exception as e:
    if con:
        con.rollback()

    print('Error %s' % e)
    sys.exit(1)

finally:
    if con:
        con.close()
