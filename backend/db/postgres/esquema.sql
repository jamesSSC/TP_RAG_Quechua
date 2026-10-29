-- =====================================================================================
-- Esquema del corpus en PostgreSQL (nube, ADR-031)
--
-- Idempotente: se aplica en cada arranque con BASE_DATOS=postgres y desde
-- scripts/sembrar_nube.py. Las tablas `fuentes`, `consultas` y `respaldos` las crea el
-- adaptador a partir de los modelos (create_all) antes de este script; aqui solo va lo que
-- los modelos no cubren.
--
--   fragmentos   corpus segmentado con su procedencia (documento, pagina, OCR). Sustituye al
--                archivo fragmentos_v3.jsonl: el disco de Render es efimero y lo que se
--                incorpora en la nube (HU-02) debe sobrevivir a un redespliegue.
-- =====================================================================================

CREATE TABLE IF NOT EXISTS fragmentos (
    -- `orden` conserva el orden de carga: el indice se reconstruye en el mismo orden que el
    -- archivo JSONL de origen.
    orden         BIGSERIAL    NOT NULL,
    id            VARCHAR(64)  PRIMARY KEY,
    documento     VARCHAR(300) NOT NULL,
    pagina        INTEGER      NOT NULL CHECK (pagina >= 0),
    texto         TEXT         NOT NULL,
    tipo          VARCHAR(20)  NOT NULL,
    derivado_ocr  BOOLEAN      NOT NULL DEFAULT FALSE,
    incorporado   TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_fragmentos_documento ON fragmentos (documento);
CREATE INDEX IF NOT EXISTS ix_fragmentos_orden ON fragmentos (orden);

-- Conteo por documento: lo usan el seeding y las capturas de Neon (U6).
CREATE OR REPLACE FUNCTION fn_fragmentos_por_documento()
RETURNS TABLE (documento VARCHAR, fragmentos BIGINT, paginas BIGINT)
LANGUAGE sql STABLE AS $$
    SELECT f.documento, COUNT(*)::BIGINT, COUNT(DISTINCT f.pagina)::BIGINT
    FROM fragmentos f
    GROUP BY f.documento
    ORDER BY f.documento;
$$;
