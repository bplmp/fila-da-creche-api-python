-23.557605, -46.645362

SELECT cd_unidade_educacao FROM unidades_educacionais_ativas WHERE ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint(-46.645362, -23.557605), 4326), 2000);


SELECT count(DISTINCT cd_solicitacao_matricula_random) FROM unidades_educacionais_ativas AS u
LEFT JOIN solicitacao_matricula_grade_dw AS s
ON u.cd_unidade_educacao::integer = s.cd_unidade_educacao
WHERE ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint(-46.645362, -23.557605), 4326), 2000)
  AND s.cd_serie_ensino = 27
;

-- group
SELECT count(DISTINCT cd_solicitacao_matricula_random), u.cd_unidade_educacao FROM unidades_educacionais_ativas AS u
LEFT JOIN solicitacao_matricula_grade_dw AS s
ON u.cd_unidade_educacao::integer = s.cd_unidade_educacao
WHERE ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint(-46.645362, -23.557605), 4326), 2000)
  AND s.cd_serie_ensino = 27
GROUP BY u.cd_unidade_educacao
;

-- number of schools
SELECT count(DISTINCT u.cd_unidade_educacao) FROM unidades_educacionais_ativas AS u
LEFT JOIN solicitacao_matricula_grade_dw AS s
ON u.cd_unidade_educacao::integer = s.cd_unidade_educacao
WHERE ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint(-46.645362, -23.557605), 4326), 2000)
  AND s.cd_serie_ensino = 27
;
