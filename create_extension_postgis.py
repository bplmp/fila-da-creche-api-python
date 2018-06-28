import psycopg2
import sys

import credentials

try:
    con = psycopg2.connect(dbname=credentials.dbname, user=credentials.user, host=credentials.host, password=credentials.password)
    cur = con.cursor()
    cur.execute("CREATE EXTENSION postgis")
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
