-- =====================================================================================
-- Procedimientos almacenados del PMV2 sobre PostgreSQL (guion del video)
--
-- Se ejecuta contra una base de demostracion con los procedimientos ya instalados:
--   psql -h 127.0.0.1 -U postgres -d quechua_wanka_demo -f docs/video/consultas_postgres.sql
-- (la contrasena va en la variable PGPASSWORD; no se escribe aqui).
-- La forma ZORRO: Atuq. (pag. 37) es un fragmento real del diccionario indexado.
-- =====================================================================================
\set ON_ERROR_STOP on
\pset null '(nulo)'
\pset border 2

\echo
\echo '== 1. Consultas por origen antes de la transaccion (fn_conteo_por_origen) =='
SELECT * FROM fn_conteo_por_origen();

\echo
\echo '== 2. sp_registrar_consulta dentro de BEGIN ... ROLLBACK (no deja nada guardado) =='
BEGIN;

CALL sp_registrar_consulta(
    'demo-ejemplo-0001',                          -- p_id
    '¿cómo se dice zorro en quechua wanka?',      -- p_texto
    'es',                                         -- p_idioma
    NULL,                                         -- p_texto_traducido
    now(),                                        -- p_momento
    'ZORRO: Atuq.',                               -- p_respuesta
    FALSE,                                        -- p_abstenida
    0.61,                                         -- p_similitud_maxima
    'similitud',                                  -- p_via_respaldo
    0.97,                                         -- p_probabilidad_cobertura
    NULL,                                         -- p_probabilidad_pasajes
    FALSE,                                        -- p_abstencion_por_predictor
    0,                                            -- p_pasajes_ofrecidos
    12.5,                                         -- p_latencia_ms
    '[{"fragmento_id": "demo-zorro-37",
       "documento": "293274822-diccionario-quechua-Wanka-docx.pdf",
       "pagina": 37, "texto": "ZORRO: Atuq.", "puntuacion": 0.61,
       "derivado_ocr": false}]'::jsonb,           -- p_respaldos (documento y pagina)
    'usuario'                                     -- p_origen (usuario | carga | arnes | humo)
);

\echo 'Dentro de la transaccion ya se ve la consulta nueva:'
SELECT * FROM fn_conteo_por_origen();

\echo 'RNF-08: una respuesta afirmativa sin respaldo documental la rechaza el procedimiento.'
SAVEPOINT sin_respaldo;
\set ON_ERROR_STOP off
CALL sp_registrar_consulta('demo-sin-respaldo', 't', 'es', NULL, now(), 'r', FALSE, 0.9,
                           'similitud', NULL, NULL, FALSE, 0, 1.0, '[]'::jsonb);
\set ON_ERROR_STOP on
ROLLBACK TO SAVEPOINT sin_respaldo;

ROLLBACK;

\echo
\echo '== 3. Despues del ROLLBACK el conteo vuelve al de antes =='
SELECT * FROM fn_conteo_por_origen();

\echo
\echo '== 4. fn_resumen_demanda(): solo demanda real (origen = usuario, valor por defecto) =='
SELECT * FROM fn_resumen_demanda();

\echo
\echo '== 5. fn_resumen_demanda(FALSE): incluye las consultas sinteticas (demostracion) =='
SELECT * FROM fn_resumen_demanda(FALSE);

\echo
\echo '== 6. fn_respaldo_por_documento(): consultas respaldadas por cada documento (real) =='
SELECT * FROM fn_respaldo_por_documento();

\echo
\echo '== 7. fn_demanda_insatisfecha(10): terminos abstenidos, solo demanda real =='
SELECT * FROM fn_demanda_insatisfecha(10);

\echo
\echo '== 8. fn_demanda_insatisfecha(10, FALSE): con sinteticas (demostracion), solo huella =='
-- No se muestra el texto: las sinteticas se derivan de conjuntos de evaluacion y se identifican
-- por una huella (md5 abreviado). Solo se ven la huella y la probabilidad de cobertura.
SELECT left(md5(texto), 8) AS huella, probabilidad_cobertura
  FROM fn_demanda_insatisfecha(10, FALSE);
