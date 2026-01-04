import os, json, requests, time
from datetime import datetime
from tqdm import tqdm

MODEL = "deepseek-coder:1.3b"
DATASET = "mini_cpp_eval.jsonl"
OUT_DIR = "cpp_results"
os.makedirs(OUT_DIR, exist_ok=True)

# System fijo para forzar "una sola pista" (comportamiento comparable a tu prueba)
SYSTEM_COACH_BENCH = (
    "Eres un tutor experto en C++ que actúa como AI-coach. "
    "Responde con UNA SOLA PISTA en una única frase. "
    "No simules diálogo ni inventes nuevas secciones. "
    "No des código ni la solución completa. "
    "Devuelve solo la pista, sin listas ni preguntas adicionales."
)

def run_ollama(prompt: str) -> str:
    """Llama al modelo local de Ollama y devuelve la respuesta completa (sin streaming)."""
    try:
        r = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,  # respuesta completa
                "options": {
                    # Determinista y corto (benchmark reproducible)
                    "temperature": 0.0,
                    "top_p": 1.0,
                    "num_predict": 20,        # equivalente a max_new_tokens
                    "repeat_penalty": 1.1,
                    # Parada para evitar que "continúe el formato"
                    "stop": ["\n###", "\n\n"]
                }
            },
            timeout=600
        )

        if r.status_code != 200:
            raise Exception(f"Error Ollama ({r.status_code}): {r.text}")

        data = r.json()
        return data.get("response", "").strip()

    except requests.exceptions.Timeout:
        return "[TIMEOUT: el modelo tardó demasiado en responder]"
    except Exception as e:
        return f"[ERROR: {e}]"

def postprocess_one_hint(text: str) -> str:
    """Corta a 'una sola pista' aunque el modelo genere de más."""
    if not text:
        return text
    text = text.strip()
    text = text.split("\n###")[0].strip()
    text = text.split("\n")[0].strip()
    return text

results = []

with open(DATASET, encoding="utf-8") as f:
    for line in tqdm(f, desc=f"Ejecutando prompts con {MODEL}"):
        task = json.loads(line)
        start_time = time.time()

        # Prompt con plantilla estable para minimizar variabilidad
        prompt = f"""### Sistema:
{SYSTEM_COACH_BENCH}

### Instrucción:
{task["prompt"]}

### Respuesta:
"""

        response = run_ollama(prompt)
        response = postprocess_one_hint(response)

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
