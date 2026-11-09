CREATE OR REPLACE VIEW schezofrenia.vw_medicamentos_kpis AS
SELECT
    medicamentos.*,
    (pvp - precio_de_referencia)/precio de referencia AS desviacion_de_precio(%),
    palabras_seccion_4_4/num_tablas AS densidad_ficha_tecnica,
    num_principios_activos + num_excipientes AS total_componentes,
    pvp - precio_de_referencia AS margen_economico_absoluto
FROM schezofrenia.medicamentos;

