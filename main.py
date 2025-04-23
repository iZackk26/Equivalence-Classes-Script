import json
import itertools
import random
import pandas as pd

# ────────────────────────────────
#  CONFIGURACIÓN GLOBAL
# ────────────────────────────────
CONFIG_PATH = "config.json"   # <-- ruta a tu JSON de equivalencias
MAX_CASOS   = 100             # <-- número máximo de CP a generar
# ────────────────────────────────

def cargar_clases_equivalencia(path):
    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    return cfg["clases_equivalencia"]

def generar_variables_reps(clases_equiv):
    """
    Devuelve dict:
      { Variable: [(valor, estado), ...], ... }
    """
    vars_reps = {}
    for ce in clases_equiv:
        var       = ce["Variable"]
        estado    = ce["Estado"]
        for rep in ce["Representantes"]:
            vars_reps.setdefault(var, []).append((rep, estado))
    return vars_reps

def generar_combinaciones(vars_reps):
    """
    Toma el diccionario de reps y devuelve una lista de tuplas:
      [ ((val1, est1),(val2, est2),...), ... ]
    Aplica muestreo aleatorio si supera MAX_CASOS.
    """
    variables         = list(vars_reps.keys())
    listas_de_reps    = [vars_reps[v] for v in variables]
    producto          = list(itertools.product(*listas_de_reps))
    if len(producto) > MAX_CASOS:
        producto = random.sample(producto, MAX_CASOS)
    return variables, producto

def crear_df_casos(variables, combinaciones):
    """
    Crea el DataFrame de CasosPrueba con columnas:
      CP, Variable1, Variable2, ...
    """
    rows = []
    for i, combo in enumerate(combinaciones, start=1):
        fila = {"CP": f"CP{str(i).zfill(3)}"}
        for var_idx, var in enumerate(variables):
            valor, _ = combo[var_idx]
            fila[var] = valor
        rows.append(fila)
    return pd.DataFrame(rows)

def crear_df_clases(clases_equiv, df_casos):
    """
    Crea el DataFrame de ClasesEquivalencia:
      Variable, Equivalencia, Estado, Representantes, CP001, CP002, ...
    Pone '*' cuando el valor del CP aparece en Representantes.
    """
    # 1) Base DF
    datos = []
    for ce in clases_equiv:
        datos.append({
            "Variable": ce["Variable"],
            "Equivalencia": ce["Equivalencia"],
            "Estado": ce["Estado"],
            "Representantes": ", ".join(ce["Representantes"]),
            "_RepsList": ce["Representantes"]
        })
    df_ce = pd.DataFrame(datos)

    # 2) Agregar columnas vacías CPxxx
    num_casos = len(df_casos)
    cp_cols = [f"CP{str(i).zfill(3)}" for i in range(1, num_casos+1)]
    for cp in cp_cols:
        df_ce[cp] = ""

    # 3) Rellenar "*"
    for idx, fila in df_ce.iterrows():
        var = fila["Variable"]
        reps_list = fila["_RepsList"]
        for tc in cp_cols:
            val = df_casos.loc[df_casos["CP"] == tc, var].values[0]
            if val in reps_list:
                df_ce.at[idx, tc] = "*"

    # 4) Eliminar columna interna
    return df_ce.drop(columns=["_RepsList"])

def exportar_excel(df_ce, df_casos, filename="formulario_casos_prueba.xlsx"):
    with pd.ExcelWriter(filename) as writer:
        df_ce.to_excel(writer, sheet_name="ClasesEquivalencia", index=False)
        df_casos.to_excel(writer, sheet_name="CasosPrueba", index=False)
    print(f"Archivo '{filename}' generado.")

def main():
    clases_equiv = cargar_clases_equivalencia(CONFIG_PATH)

    # 2) Prepare the combinations
    vars_reps    = generar_variables_reps(clases_equiv)
    variables, combos = generar_combinaciones(vars_reps)

    # 3) DataFrames
    df_casos = crear_df_casos(variables, combos)
    df_ce     = crear_df_clases(clases_equiv, df_casos)

    # 4) Export
    exportar_excel(df_ce, df_casos)

if __name__ == "__main__":
    main()

