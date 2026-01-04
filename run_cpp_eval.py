import os, json, requests, time, re
from datetime import datetime
from tqdm import tqdm

# ========= CONFIGURACIÓN =========

MODEL = "wizardcoder_ft"          # cambia aquí si evalúas otro modelo
DATASET = "mini_cpp_eval.jsonl"
OUT_DIR = "cpp_results"
os.makedirs(OUT_DIR, exist_ok=True)

SYSTEM_COACH_BENCH = (
    "Eres un tutor experto en C++ que actúa como AI-coach. "
    "Responde con UNA SOLA PISTA en una única frase DECLARATIVA y termina con un punto. "
    "NO formules preguntas. "
    "NO uses prefijos como 'Coach:' ni 'La pista es:'. "
    "NO simules diálogo ni inventes nuevas secciones. "
    "NO des código ni pseudocódigo. "
    "NO des la solución completa. "
    "Devuelve solo la pista (una frase), sin listas."
)

# ========= OLLAMA =========

def run_ollama(prompt: str) -> str:
    try:
        r = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    # determinista
                    "temperature": 0.0,
                    "top_p": 1.0,
                    "repeat_penalty": 1.12,

                    # evita truncados a media palabra
                    "num_predict": 140,

                    # stops seguros: corta si intenta abrir código o nuevas secciones
                    "stop": ["```", "\n###"]
                }
            },
            timeout=600
        )

        if r.status_code != 200:
            raise Exception(f"Error Ollama ({r.status_code}): {r.text}")

        return r.json().get("response", "").strip()

    except requests.exceptions.Timeout:
        return "[TIMEOUT]"
    except Exception as e:
        return f"[ERROR: {e}]"

# ========= POSTPROCESADO =========

def _strip_prefixes(s: str) -> str:
    # elimina prefijos comunes repetidos
    s = re.sub(r'^\s*(Coach:|Alumno:)\s*', '', s, flags=re.IGNORECASE)
    s = re.sub(r'^\s*(La\s+pista\s+es:|Pista:|La\s+respuesta\s+es:)\s*', '', s, flags=re.IGNORECASE)
    s = re.sub(r'^\s*[-•\d]+\s*', '', s)  # listas / bullets al inicio
    return s.strip()

def postprocess_one_hint(text: str) -> str:
    if not text:
        return text

    t = text.strip()

    # corta intentos de secciones / código
    t = t.split("\n###")[0].strip()
    t = t.split("```")[0].strip()

    # primera línea no vacía
    lines = [ln.strip() for ln in t.splitlines() if ln.strip()]
    t = lines[0] if lines else ""

    t = _strip_prefixes(t)

    # si empieza con "¿" o contiene "?" (pregunta), intenta rescatar una frase declarativa del resto
    if "?" in t or t.startswith("¿"):
        # elimina todo lo interrogativo y quédate con lo que venga después, si lo hay
        t2 = re.split(r'\?', t, maxsplit=1)
        t = t2[1].strip() if len(t2) > 1 else ""
        t = _strip_prefixes(t)

    # quita comillas envolventes si las pone
    t = t.strip().strip('"').strip("'").strip()

    # recorta a 1 frase por delimitadores fuertes
    # (preferimos punto; si no hay, aceptamos !; evitamos ? por requisito)
    m = re.search(r'(.+?\.)\s*', t)
    if m:
        out = m.group(1).strip()
        return out

    m = re.search(r'(.+?[!])\s*', t)
    if m:
        out = m.group(1).strip()
        # normaliza a punto para cumplir "frase declarativa"
        out = out.rstrip("!") + "."
        return out

    # si no hay puntuación final, añade punto
    t = re.sub(r'\s+', ' ', t).strip()
    if not t:
        return "Usa un enfoque incremental y verifica cada caso límite antes de optimizar."

    return t.rstrip(".") + "."

# ========= EJECUCIÓN =========

results = []

with open(DATASET, encoding="utf-8") as f:
    for line in tqdm(f, desc=f"Ejecutando prompts con {MODEL}"):
        task = json.loads(line)
        start_time = time.time()

        prompt = f"""### Sistema:
{SYSTEM_COACH_BENCH}

### Instrucción:
{task["prompt"]}

### Respuesta:
"""

        raw_response = run_ollama(prompt)
        response = postprocess_one_hint(raw_response)

        elapsed = round(time.time() - start_time, 2)

        results.append({
            "id": task.get("id", ""),
            "prompt": prompt,
            "model": MODEL,
            "response": response,
            "time_seconds": elapsed
        })

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
outfile = os.path.join(OUT_DIR, f"results_{MODEL}_{timestamp}.json")

with open(outfile, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4, ensure_ascii=False)

print(f"\nEvaluación completada. Resultados guardados en: {outfile}\n")
