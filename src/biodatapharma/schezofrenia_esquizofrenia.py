



from biodatapharma import hu1, hu2, hu3, hu4_limpieza, hu5, hu6_create_table, hu6_kpis, hu6_load

def main():
    logging.info(f"fINALIZADO ejecución de: {script_name}")
    if hu1.extract_nomenclator() != 0:
        logging.error(f"fINALIZADO ejecución de: {script_name}")
        return 1
    logging.error(f"fINALIZADO ejecución de: {script_name}")
    if hu4_limpieza.clean_and_transform() != 0:
        return 2
    
    if hu5.cluster_kmeans() != 0:
        return 3
    if hu6_create_table.create_table() != 0:
        return 4
    
    if hu6_load.load_data() != 0:
        
    if hu6_kpis.kpis() != 0:
    

if __name__=="__main__":
    main()