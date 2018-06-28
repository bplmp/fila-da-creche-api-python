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
    cur.execute("DROP TABLE IF EXISTS unidades_educacionais_ativas")
    cur.execute("""CREATE TABLE unidades_educacionais_ativas(
    cd_unidade_educacao                 character(6),
    nm_unidade_educacao                 character varying(60),
    nm_exibicao_unidade_educacao        character varying(60),
    tp_situacao_unidade                 integer,
    tp_unidade_educacao                 integer,
    cd_unidade_administrativa           character(6),
    nm_unidade_administrativa           character varying(60),
    nm_exibicao_unidade_administrativa  character varying(60),
    dc_tipo_unidade_educacao            character varying(25),
    tp_escola                           integer,
    sg_tp_escola                        character varying(12),
    sg_tipo_situacao_unidade            character varying(10),
    nm_distrito                         text,
    nm_micro_regiao                     character varying(40),
    cd_micro_regiao                     integer,
    cd_distrito_mec                     text,
    cd_sub_prefeitura                   integer,
    dc_sub_prefeitura                   character varying(35),
    cd_latitude                         double precision,
    cd_longitude                        double precision,
    nu_turmas_2018                      bigint,
    nu_ambientes_2018                   bigint,
    nu_vagas_oferecidas_2018            bigint
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
