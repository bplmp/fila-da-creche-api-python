import psycopg2
import sys

import credentials

try:
    con = psycopg2.connect(dbname=credentials.dbname, user=credentials.user, host=credentials.host, password=credentials.password)
    cur = con.cursor()
    cur.execute("""ALTER TABLE unidades_educacionais_ativas
    ADD COLUMN geom geometry(Point, 4326)""")
    cur.execute("""UPDATE unidades_educacionais_ativas
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
