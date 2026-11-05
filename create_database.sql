CREATE DATABASE IF NOT EXISTS SCHIZOFRENIA;

USE SCHIZOFRENIA;

DROP TABLE IF EXISTS mediacamentos

CREATE TABLE medicamentos(

    nregistro VARCHAR(250) PRIMARY KEY,

    labcomercializador VARCHAR(250),

    forma_farmaceutica_simplificada VARCHAR(250),

    vias_administracion VARCHAR(250),

    comercializado TINYINT, 

    generico TINYINT,

    num_excipientes INT, 

    palabras_seccion_4_4 INT, 

    num_tablas INT,

    num_grave INT,
    
    estado VARCHAR(50),

    pvp float,

    antiguedad_anios float,

    revocado TINYINT,

    tld_unknown TINYINT,

    pa_base VARCHAR(30),

    dosis_mg float,

    dosis_es_concentracion TINYINT,

    CLUSTER INT

);
LOAD DATA LOCAL INFILE "data/hu5.csv"

INTO TABLE medicamentos

FIELDS TERMINATED BY ','

OPTIONALLY ENCLOSED BY '""'

LINES TERMINATED BY '\n'

IGNORE LINES 1;
