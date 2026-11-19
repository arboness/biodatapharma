CREATE OR REPLACE VIEW schezofrenia.vw_medicamentos_kpis AS
SELECT
    medicamentos.*,
    ROUND((pvp - precio_de_referencia) / NULLIF(precio_de_referencia, 0) * 100, 2) AS desviacion_de_precio,
    ROUND(palabras_seccion_4_4 / NULLIF(num_tablas, 0), 2) AS densidad_ficha_tecnica,
    num_principios_activos + num_excipientes AS total_componentes,
    pvp - precio_de_referencia AS margen_economico_absoluto,
    DENSE_RANK() OVER (
        PARTITION BY forma_farmaceutica_simplificada
        ORDER BY pvp DESC
    ) AS ranking_precio_por_forma
FROM schezofrenia.medicamentos;