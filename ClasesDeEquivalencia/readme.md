
## Dependencies

* pandas>=1.1.0
* openpyxl>=3.0.0


## Configuration (`config.json`)

Your **`config.json`** must follow this schema:

```jsonc
{
  // -- This top-level comment is optional.
  // CONFIG FORMAT:
  // - Top-level key: "clases_equivalencia" (array of objects)
  // - Each object must contain:
  //     • "Variable"      (string): the field name
  //     • "Equivalencia"  (string): description of the class
  //     • "Estado"        (string): "Válido" or "Inválido"
  //     • "Representantes" (array of strings): example values
  //     • "Tipo": Caja Negra o Caja Blanca


    "clases_equivalencia": [
      {
        "Variable": "Tipo identificación",
        "Equivalencia": "Nacional (dropdown)",
        "Estado": "Válido",
        "Representantes": ["Nacional"]
        "Tipo": "caja negra" // Opcional
      },
      ...
    ]
}

```
