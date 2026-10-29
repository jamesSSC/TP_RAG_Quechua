-- =====================================================================================
-- Procedimientos almacenados del asistente de consulta del quechua wanka (PostgreSQL)
--
-- Se aplican al arrancar el servicio cuando BASE_DATOS=postgres (CREATE OR REPLACE: son
-- idempotentes). Los invoca el adaptador RepositorioConsultasPostgres; el nucleo hexagonal
-- no sabe que existen: para el dominio sigue habiendo un RepositorioConsultasPort.
--
--   sp_registrar_consulta      PROCEDURE  registra consulta + respaldos en una transaccion
--   sp_borrar_historial        PROCEDURE  borra el historial (los respaldos caen en cascada)
--   fn_resumen_demanda         FUNCTION   agregados del historial para la analitica (HU-09)
--   fn_respaldo_por_documento  FUNCTION   consultas respaldadas por cada documento (sesgo, M17)
--   fn_demanda_insatisfecha    FUNCTION   terminos abstenidos con su frecuencia y P(cobertura)
--   fn_conteo_por_origen       FUNCTION   consultas por origen (usuario, carga, arnes, humo)
-- =====================================================================================

-- HU-09 (ADR-013): cada consulta lleva su origen (usuario | carga | arnes | humo).
-- Migracion compatible: las filas anteriores quedan como `usuario`.
ALTER TABLE consultas ADD COLUMN IF NOT EXISTS origen VARCHAR(10) NOT NULL DEFAULT 'usuario';

-- Las firmas cambian (parametro nuevo): se retiran las anteriores para no dejar sobrecargas
-- ambiguas. Idempotente.
DROP PROCEDURE IF EXISTS sp_registrar_consulta(
    VARCHAR, TEXT, VARCHAR, TEXT, TIMESTAMPTZ, TEXT, BOOLEAN, DOUBLE PRECISION, VARCHAR,
    DOUBLE PRECISION, DOUBLE PRECISION, BOOLEAN, INTEGER, DOUBLE PRECISION, JSONB);
DROP FUNCTION IF EXISTS fn_resumen_demanda();
DROP FUNCTION IF EXISTS fn_respaldo_por_documento();
DROP FUNCTION IF EXISTS fn_demanda_insatisfecha(INTEGER);

CREATE OR REPLACE PROCEDURE sp_registrar_consulta(
    p_id                        VARCHAR,
    p_texto                     TEXT,
    p_idioma                    VARCHAR,
    p_texto_traducido           TEXT,
    p_momento                   TIMESTAMPTZ,
    p_respuesta                 TEXT,
    p_abstenida                 BOOLEAN,
    p_similitud_maxima          DOUBLE PRECISION,
    p_via_respaldo              VARCHAR,
    p_probabilidad_cobertura    DOUBLE PRECISION,
    p_probabilidad_pasajes      DOUBLE PRECISION,
    p_abstencion_por_predictor  BOOLEAN,
    p_pasajes_ofrecidos         INTEGER,
    p_latencia_ms               DOUBLE PRECISION,
    p_respaldos                 JSONB,
    p_origen                    VARCHAR DEFAULT 'usuario'
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- RNF-08: una respuesta afirmativa sin respaldo no puede quedar registrada.
    IF NOT p_abstenida AND jsonb_array_length(COALESCE(p_respaldos, '[]'::jsonb)) = 0 THEN
        RAISE EXCEPTION 'Respuesta % sin respaldo documental', p_id;
    END IF;

    INSERT INTO consultas (
        id, texto, idioma, texto_traducido, momento, respuesta_texto, abstenida,
        similitud_maxima, via_respaldo, probabilidad_cobertura, probabilidad_pasajes,
        abstencion_por_predictor, pasajes_ofrecidos, latencia_ms, origen
    ) VALUES (
        p_id, p_texto, p_idioma, p_texto_traducido, p_momento, p_respuesta, p_abstenida,
        p_similitud_maxima, p_via_respaldo, p_probabilidad_cobertura, p_probabilidad_pasajes,
        p_abstencion_por_predictor, p_pasajes_ofrecidos, p_latencia_ms,
        COALESCE(p_origen, 'usuario')
    );

    INSERT INTO respaldos (consulta_id, fragmento_id, documento, pagina, texto, puntuacion, derivado_ocr)
    SELECT p_id,
           r ->> 'fragmento_id',
           r ->> 'documento',
           (r ->> 'pagina')::INTEGER,
           r ->> 'texto',
           (r ->> 'puntuacion')::DOUBLE PRECISION,
           COALESCE((r ->> 'derivado_ocr')::BOOLEAN, FALSE)
      FROM jsonb_array_elements(COALESCE(p_respaldos, '[]'::jsonb)) AS r;
END;
$$;


CREATE OR REPLACE PROCEDURE sp_borrar_historial(INOUT p_borradas INTEGER DEFAULT 0)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM consultas;
    GET DIAGNOSTICS p_borradas = ROW_COUNT;
END;
$$;


-- p_solo_usuario = TRUE (por defecto): solo la demanda real. FALSE incluye las sinteticas.
CREATE OR REPLACE FUNCTION fn_resumen_demanda(p_solo_usuario BOOLEAN DEFAULT TRUE)
RETURNS TABLE (
    total                         BIGINT,
    abstenidas                    BIGINT,
    abstenciones_por_predictor    BIGINT,
    probabilidad_cobertura_media  DOUBLE PRECISION,
    latencia_media_ms             DOUBLE PRECISION,
    latencia_p95_ms               DOUBLE PRECISION
)
LANGUAGE sql
STABLE
AS $$
    SELECT COUNT(*),
           COUNT(*) FILTER (WHERE abstenida),
           COUNT(*) FILTER (WHERE abstencion_por_predictor),
           AVG(probabilidad_cobertura),
           AVG(latencia_ms),
           PERCENTILE_DISC(0.95) WITHIN GROUP (ORDER BY latencia_ms)
      FROM consultas
     WHERE NOT p_solo_usuario OR origen = 'usuario';
$$;


CREATE OR REPLACE FUNCTION fn_respaldo_por_documento(p_solo_usuario BOOLEAN DEFAULT TRUE)
RETURNS TABLE (documento VARCHAR, consultas BIGINT)
LANGUAGE sql
STABLE
AS $$
    SELECT r.documento, COUNT(DISTINCT r.consulta_id)
      FROM respaldos r
      JOIN consultas c ON c.id = r.consulta_id
     WHERE NOT p_solo_usuario OR c.origen = 'usuario'
     GROUP BY r.documento
     ORDER BY 2 DESC;
$$;


CREATE OR REPLACE FUNCTION fn_demanda_insatisfecha(
    p_limite INTEGER DEFAULT 5000, p_solo_usuario BOOLEAN DEFAULT TRUE)
RETURNS TABLE (texto TEXT, probabilidad_cobertura DOUBLE PRECISION)
LANGUAGE sql
STABLE
AS $$
    SELECT c.texto, c.probabilidad_cobertura
      FROM consultas c
     WHERE c.abstenida
       AND (NOT p_solo_usuario OR c.origen = 'usuario')
     ORDER BY c.momento DESC
     LIMIT p_limite;
$$;


-- Conteo por origen, sin filtrar: lo que permite declarar cuanta demanda es real.
CREATE OR REPLACE FUNCTION fn_conteo_por_origen()
RETURNS TABLE (origen VARCHAR, consultas BIGINT)
LANGUAGE sql
STABLE
AS $$
    SELECT c.origen, COUNT(*) FROM consultas c GROUP BY c.origen ORDER BY 2 DESC;
$$;
