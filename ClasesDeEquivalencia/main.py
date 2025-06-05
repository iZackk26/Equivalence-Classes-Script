from modules.equivalence_classes import *

CONFIG_PATH = "config.csv"

def main():
    clases_equiv, df_casos_csv = cargar_fuente_equivalencias(CONFIG_PATH)

    if df_casos_csv is None:
        vars_reps         = generar_variables_reps(clases_equiv)
        variables, combos = generar_combinaciones(vars_reps)
        df_casos          = crear_df_casos(variables, combos)
    else:
        df_casos = df_casos_csv

    df_ce = crear_df_clases(clases_equiv, df_casos)
    exportar_excel(df_ce, df_casos)

if __name__ == "__main__":
    main()

