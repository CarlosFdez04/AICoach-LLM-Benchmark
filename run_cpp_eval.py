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
    "Responde con UNA SOLA PISTA en una única frase declarativa. "
    "NO formules preguntas. "
    "NO uses prefijos como 'Coach:' ni 'La pista es:'. "
    "NO simules diálogo ni inventes nuevas secciones. "
    "NO des código ni pseudocódigo. "
    "NO des la solución completa. "
    "Devuelve solo la pista (una frase)."
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
                    "temperature": 0.0,
                    "top_p": 1.0,
                    "repeat_penalty": 1.1,
                    "num_predict": 80,
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

def postprocess_one_hint(text: str) -> str:
    if not text:
        return text

    t = text.strip()

    # cortar intentos de secciones / código
    t = t.split("\n###")[0].strip()
    t = t.split("```")[0].strip()

    # eliminar prefijos típicos
    t = re.sub(
        r'^(Coach:|Alumno:|La pista es:|La respuesta es:)\s*',
        '',
        t,
        flags=re.IGNORECASE
    ).strip()

    # primera línea
    t = t.splitlines()[0].strip()

    # quedarse con la primera frase
    m = re.search(r'(.+?[.!?])(\s|$)', t)
    if m:
        return m.group(1).strip()

    # si no hay puntuación final, la añadimos
    return t.rstrip() + "."

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
