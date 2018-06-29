import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys

import dotenv_variables

try:
    con = psycopg2.connect(dbname=dotenv_variables.POSTGRES_DBNAME, user=dotenv_variables.POSTGRES_USER, host=dotenv_variables.POSTGRES_HOST, password=dotenv_variables.POSTGRES_PASSWORD)
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
