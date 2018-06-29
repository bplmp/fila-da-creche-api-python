import psycopg2
import sys

import credentials

try:
    con = psycopg2.connect(dbname=credentials.dbname, user=credentials.user, host=credentials.host, password=credentials.password)
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS solicitacao_matricula_grade_dw")
    cur.execute("""CREATE TABLE solicitacao_matricula_grade_dw(
    cd_solicitacao_matricula_random INTEGER,
    cd_serie_ensino INTEGER,
    cd_solicitacao_matricula_grade_distancia INTEGER,
    cd_unidade_educacao INTEGER,
    in_elegivel_compatibilizacao VARCHAR(20),
    in_grade_ano_corrente VARCHAR(20),
    in_grade_ano_seguinte VARCHAR(20)
    )""")
    cur.execute("DROP TABLE IF EXISTS unidades_educacionais_ativas_endereco_contato")
    cur.execute("""CREATE TABLE unidades_educacionais_ativas_endereco_contato(
    cd_unidade_educacao character varying(60),
    nm_exibicao_unidade_educacao character varying(255),
    nm_unidade_educacao character varying(255),
    tp_escola integer,
    sg_tp_escola character varying(60),
    cd_latitude float,
    cd_longitude float,
    endereco_completo character varying(255),
    telefones character varying(60)[],
    sg_tipo_situacao_unidade character varying(60)
    )""")
    con.commit()
    cur.execute("DROP TABLE IF EXISTS unidades_educacionais_infantil_vagas_serie")
    cur.execute("""CREATE TABLE unidades_educacionais_infantil_vagas_serie(
    cd_unidade_educacao character varying(60),
    nm_exibicao_unidade_educacao character varying(255),
    nm_unidade_educacao character varying(255),
    tp_escola integer,
    sg_tp_escola character varying(60),
    vagas_cd_serie_1 integer,
    vagas_cd_serie_4 integer,
    vagas_cd_serie_27 integer,
    vagas_cd_serie_28 integer,
    sg_tipo_situacao_unidade character varying(60)
    )""")
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
