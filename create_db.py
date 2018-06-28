import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys

import credentials

try:
    con = psycopg2.connect(dbname='postgres', user=credentials.user, host=credentials.host, password=credentials.password)
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    cur.execute('CREATE DATABASE ' + credentials.dbname)
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
