import os
import json
import openai
from dotenv import load_dotenv

load_dotenv()

# ——————————————————————————————————————————————————————————————————
# Leemos la API Key desde la variable de entorno y la asignamos
openai.api_key = os.getenv("OPENAI_API_KEY")
if openai.api_key is None:
    raise RuntimeError("La variable de entorno OPENAI_API_KEY no está definida.")

def generar_descripcion_y_resultados(caso: dict) -> dict:
    """
    Usa la API de OpenAI para generar:
      - 'descripcion': explicación del defecto basado en la tabla de clases válidas/inválidas.
      - 'resultado_esperado': lo que debería ocurrir según reglas de validación.
      - 'resultado_obtenido': el mensaje actual de error (o comportamiento observado).

    El argumento `caso` debe ser un dict con al menos estas claves:
      - "tipo_usuario" (str)
      - "username"     (str)
      - "password"     (str)
      - "slider"       (str)  # "arrastrado" o "sin arrastrar"
      - "remember_me"  (str)  # "marcado" o "no marcado"
      - "is_valid"     (bool)
      - "error_message"(str)

    Devuelve un dict con las claves:
      - "descripcion"
      - "resultado_esperado"
      - "resultado_obtenido"
    """

    reglas = """
Variable                  | Clase Válida                                | Clase Inválida                                         | Representantes
--------------------------|----------------------------------------------|---------------------------------------------------------|---------------------------
Campo tipo de username    | Cualquier valor dentro del dropdown.         | Ninguna (el dropdown siempre tiene “Super” por defecto). | Super, Admin, User
Campo de username         | Texto con longitud > 1 carácter.             | Texto vacío.                                            | “vacío”, u, us…
Campo de password         | Texto con longitud > 1 carácter.             | Texto vacío.                                            | “vacío”, p, pa…
Campo de Slider & Drag    | Slider arrastrado por completo.              | Slider sin arrastrar.                                   | arrastrado, sin arrastrar
Campo de Remember Me      | Checkbox presionado o no. (opcionales).      | No aplica clase inválida (siempre válido).              | “marcado”, “no marcado”
"""

    prompt = f"""
A continuación se muestra la tabla de reglas de validación para cada variable en el formulario:

{reglas}

Ahora, para el siguiente caso de prueba, genera:
1) Una descripción del defecto. Usa saltos de línea (\\n) para cada punto. El texto debe explicar exactamente cuál es la regla violada (o por qué es inválido) basándose en la tabla.
2) El bloque “Resultados esperados”: qué debería haber ocurrido según las reglas.
3) El bloque “Resultado obtenido”: qué sucedió realmente (usa el campo error_message).

Caso de prueba:
- tipo_usuario: "{caso['tipo_usuario']}"
- username: "{caso['username']}"
- password: "{caso['password']}"
- slider: "{caso['slider']}"
- remember_me: "{caso['remember_me']}"
- is_valid: {caso['is_valid']}
- error_message: "{caso['error_message']}"

Por favor, devuelve la respuesta en formato JSON con claves EXACTAS:
- "descripcion"
- "resultado_esperado"
- "resultado_obtenido"
Nada más.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Eres un asistente que genera descripciones de defectos y resultados de prueba basados en reglas de validación."},
            {"role": "user",   "content": prompt}
        ],
        temperature=0.0
    )

    raw = response["choices"][0]["message"]["content"].strip()

    # Si ChatGPT devolvió bloque con triple-backticks, recortamos todo antes del primer '{' y después del último '}'
    if raw.startswith("```"):
        # Buscamos el primer '{' y el último '}'
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            raw = raw[start:end+1]

    # Ahora raw debería ser un JSON puro. Lo parseamos.
    return json.loads(raw)

