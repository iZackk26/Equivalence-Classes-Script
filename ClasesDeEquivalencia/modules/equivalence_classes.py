import json
import itertools
import random
import pandas as pd
import os
import chardet

MAX_CASOS = 6  # Puedes modificarlo desde fuera si lo deseas

def detectar_codificacion(path: str, sample: int = 100_000) -> str:
    with open(path, "rb") as f:
        raw = f.read(sample)
    enc = chardet.detect(raw)["encoding"]
    return enc or "utf-8"

def cargar_fuente_equivalencias(path: str):
    ext = os.path.splitext(path)[1].lower()

    # ── 1) JSON ───────────────────────────────────────────────
    if ext == ".json":
        with open(path, "r", encoding="utf‑8") as f:
            cfg = json.load(f)
        return cfg["clases_equivalencia"], None

    # ── 2) CSV ────────────────────────────────────────────────
    if ext == ".csv":
        enc = detectar_codificacion(path)
        df_raw = pd.read_csv(path, encoding=enc)

        var_cols    = df_raw.columns[:-1]
        estado_col  = df_raw.columns[-1]

        df_casos = df_raw[var_cols].copy()
        df_casos.insert(0, "CP", [f"CP{str(i+1).zfill(3)}" for i in range(len(df_casos))])

        clases = []
        for var in var_cols:
            reps_v = (df_raw.loc[df_raw[estado_col].astype(str).str.upper() == "V", var]
                        .dropna().astype(str).unique().tolist())
            if reps_v:
                clases.append({
                    "Variable": var,
                    "Equivalencia": f"{var}-Válidos",
                    "Estado": "V",
                    "Representantes": reps_v
                })

            reps_i = (df_raw.loc[df_raw[estado_col].astype(str).str.upper() != "V", var]
                        .dropna().astype(str).unique().tolist())
            if reps_i:
                clases.append({
                    "Variable": var,
                    "Equivalencia": f"{var}-Inválidos",
                    "Estado": "I",
                    "Representantes": reps_i
                })

        return clases, df_casos

    raise ValueError(f"Formato no soportado: {ext}. Usa .json o .csv.")

def generar_variables_reps(clases_equiv):
    vars_reps = {}
    for ce in clases_equiv:
        var, estado = ce["Variable"], ce["Estado"]
        for rep in ce["Representantes"]:
            vars_reps.setdefault(var, []).append((rep, estado))
    return vars_reps

def generar_combinaciones(vars_reps):
    variables      = list(vars_reps.keys())
    listas_reps    = [vars_reps[v] for v in variables]
    producto       = list(itertools.product(*listas_reps))
    if len(producto) > MAX_CASOS:
        producto = random.sample(producto, MAX_CASOS)
    return variables, producto

def crear_df_casos(variables, combinaciones):
    rows = []
    for i, combo in enumerate(combinaciones, start=1):
        fila = {"CP": f"CP{str(i).zfill(3)}"}
        for idx, var in enumerate(variables):
            fila[var] = combo[idx][0]
        rows.append(fila)
    return pd.DataFrame(rows)

def crear_df_clases(clases_equiv, df_casos):
    datos = []
    for ce in clases_equiv:
        fila = {
            "Variable": ce["Variable"],
            "Equivalencia": ce["Equivalencia"],
            "Estado": ce["Estado"],
            "Representantes": ", ".join(ce["Representantes"]),
            "_RepsList": ce["Representantes"]
        }
        if "Tipo" in ce:
            fila["Tipo"] = ce["Tipo"]
        datos.append(fila)

    df_ce = pd.DataFrame(datos)

    cols_base = ["Variable", "Equivalencia", "Estado"]
    if "Tipo" in df_ce.columns:
        cols_base.append("Tipo")
    cols_base += ["Representantes", "_RepsList"]
    df_ce = df_ce[cols_base]

    cp_cols = [c for c in df_casos["CP"]]
    for cp in cp_cols:
        df_ce[cp] = ""

    for idx, fila in df_ce.iterrows():
        reps = fila["_RepsList"]
        for cp in cp_cols:
            valor = df_casos.loc[df_casos["CP"] == cp, fila["Variable"]].values[0]
            if valor in reps:
                df_ce.at[idx, cp] = "*"

    return df_ce.drop(columns=["_RepsList"])

def exportar_excel(df_ce, df_casos, filename="formulario_casos_prueba.xlsx"):
    with pd.ExcelWriter(filename) as writer:
        df_ce.to_excel(writer, sheet_name="ClasesEquivalencia", index=False)
        df_casos.to_excel(writer, sheet_name="CasosPrueba", index=False)
    print(f"✔ Archivo '{filename}' generado.")

