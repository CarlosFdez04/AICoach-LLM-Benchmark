import os, json, requests, time
from datetime import datetime
from tqdm import tqdm

MODEL = "deepseek-coder:1.3b"
DATASET = "mini_cpp_eval.jsonl"
OUT_DIR = "cpp_results"
os.makedirs(OUT_DIR, exist_ok=True)

def run_ollama(prompt):
    """Llama al modelo local de Ollama y devuelve la respuesta completa (sin streaming)."""
    try:
        r = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,  # Pedimos respuesta completa
                "options": {"temperature": 0.2}
            },
            timeout=600  # Hasta 10 minutos por pregunta
        )

        if r.status_code != 200:
            raise Exception(f"Error Ollama ({r.status_code}): {r.text}")

        data = r.json()
        return data.get("response", "").strip()

    except requests.exceptions.Timeout:
        return "[TIMEOUT: el modelo tardó demasiado en responder]"
    except Exception as e:
        return f"[ERROR: {e}]"

results = []

with open(DATASET) as f:
    for line in tqdm(f, desc=f"Ejecutando prompts con {MODEL}"):
        task = json.loads(line)
        start_time = time.time()

        # Contexto de AI-Coach
        coach_prompt = (
            "Actúa como un tutor experto en programación en C++. "
            "Tu tarea es guiar al estudiante paso a paso para que llegue por sí mismo a la solución. "
            "No escribas directamente el código completo a menos que se te pida explícitamente. "
            "En su lugar, ofrece explicaciones, ejemplos parciales, analogías y preguntas que fomenten el razonamiento.\n\n"
        )

        # Combinar el contexto del coach con el enunciado del ejercicio
        prompt = coach_prompt + task["prompt"]

        # Obtener respuesta del modelo
        response = run_ollama(prompt)

        elapsed = round(time.time() - start_time, 2)

        # Guardar resultados sin validación automática
        results.append({
            "id": task.get("id", ""),
            "prompt": prompt,
            "model": MODEL,
            "response": response.strip(),
            "time_seconds": elapsed
        })

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # generar nombre único
outfile = os.path.join(OUT_DIR, f"results_{MODEL}_{timestamp}.json")

with open(outfile, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4, ensure_ascii=False)

print(f"\n Evaluación completada. Resultados guardados en: {outfile}\n")

