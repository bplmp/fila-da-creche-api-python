import psycopg2

import credentials
# Try to connect

try:
    con = psycopg2.connect(dbname=credentials.dbname, user=credentials.user, host=credentials.host, password=credentials.password)
except:
    print("I am unable to connect to the database.")

cur = con.cursor()
try:
    cur.execute("""SELECT DISTINCT cd_solicitacao_matricula_random
    FROM solicitacao_ativa_matricula_grade_distancia
    WHERE cd_unidade_educacao IN (400759, 308893)""")
    # FIXME: need to include ano (mini grupo, bercario...)
except:
    print("I can't SELECT from bar")

rows = cur.fetchall()
for row in rows:
    # print("   ", row[1][1])
    print(row)

print(len(rows))
