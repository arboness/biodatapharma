CREATE OR REPLACE VIEW schezofrenia.vw_medicamentos_kpis AS
SELECT
    medicamentos.*,
    num_principios_activos + num_excipientes AS total_componentes,
    pvp - precio_de_referencia AS margen_economico_absoluto
FROM schezofrenia.medicamentos;