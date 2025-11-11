# AICoach-LLM-Benchmark

**AICoach-LLM-Benchmark** is a lightweight framework for evaluating **Large Language Models (LLMs)** as *AI programming coaches* using C/C++ exercises.  
It forms part of an academic research project focused on analyzing how LLMs like **LLaMA 2** and **WizardCoder** perform in both **technical accuracy** and **pedagogical guidance**.

---

## Overview

This benchmark allows researchers and students to:
- Assess the **code generation quality** of LLMs on structured C++ problems.  
- Examine their **tutoring abilities**, i.e., how effectively they guide learners without directly revealing full solutions.  
- Compare different models under a unified evaluation pipeline using **Ollama** for local inference.

---

## Repository Structure

AICoach-LLM-Benchmark/
│
├── cpp_results/ # Model output files (results in JSON format)
│ ├── results_llama2/ # LLaMA 2 evaluation results
│ ├── results_wizardcoder/ # (Future) WizardCoder evaluations
│
├── mini_cpp_eval.jsonl # Small dataset of C++ tasks used for testing
│ # Each line contains an ID and a textual prompt
│
└── run_cpp_eval.py # Python script that runs the benchmark locally

---

## Example of a Benchmark Task
{
  "id": "CPP_01",
  "prompt": "Diseña una función en C++ que, dado un vector<int>, devuelva un nuevo vector con los elementos únicos en el mismo orden."
}
Each task is used as a prompt for the target model, and its response is automatically stored and evaluated.

- How to Run

1.Prerequisites
Python ≥ 3.9
Ollama installed and running locally
At least one model available (e.g. llama2, wizardcoder, mistral)

2.Execute the benchmark
python run_cpp_eval.py

The script will:
1.Load prompts from mini_cpp_eval.jsonl
2.Send them to the selected LLM through the local Ollama API (http://localhost:11434/api/generate)
3.Store the outputs in cpp_results/<model_name>/results_<timestamp>.json

- Output Format
Each JSON result file contains:

id – task identifier
prompt – C++ problem statement
response – model’s generated answer
passed / total – number of passed tests (if applicable)
timestamp – time of execution

Example:
cpp_results/results_llama2-7b_20251111_160700.json
