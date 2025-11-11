# AICoach-LLM-Benchmark

**AICoach-LLM-Benchmark** is a lightweight framework for evaluating **Large Language Models (LLMs)** as *AI programming coaches* using C/C++ exercises.  
It forms part of an academic research project focused on analyzing how LLMs like **LLaMA 2** and **WizardCoder** perform in both **technical accuracy** and **pedagogical guidance**.

---

## Overview

This benchmark allows researchers and students to:
- Assess the **code generation quality** of LLMs on structured C++ problems.  
- Examine their **coaching abilities**, i.e., how effectively they guide learners without directly revealing full solutions.  
- Compare different models under a unified evaluation pipeline using **Ollama** for local inference.

---

## Repository Structure

```plaintext
AICoach-LLM-Benchmark/
│
├── cpp_results/                  # Model output files (results in JSON format)
│   ├── results_llama2/           # LLaMA 2 evaluation results
│   ├── results_wizardcoder/      # (Future) WizardCoder evaluations
│
├── mini_cpp_eval.jsonl           # Small dataset of C++ tasks used for testing
│                                 # Each line contains an ID and a textual prompt
│
└── run_cpp_eval.py               # Python script that runs the benchmark locally
```

## Example of a Benchmark Task
{
  "id": "CPP_01",
  "prompt": "Diseña una función en C++ que, dado un vector<int>, devuelva un nuevo vector con los elementos únicos en el mismo orden."
}
Each task is used as a prompt for the target model, and its response is automatically stored and evaluated.

- How to Run

1. Prerequisites
Python ≥ 3.9
Ollama installed and running locally
At least one model available (e.g. llama2, wizardcoder, mistral)

2. Execute the benchmark
python run_cpp_eval.py

The script will:
1. Load prompts from mini_cpp_eval.jsonl
2. Send them to the selected LLM through the local Ollama API (http://localhost:11434/api/generate)
3. Store the outputs in cpp_results/<model_name>/results_<timestamp>.json

Output Format.
Each JSON result file contains:

-  id –> task identifier
-  prompt –> C++ problem statement
-  response –> model’s generated answer
-  passed / total –> number of passed tests (if applicable)
-  timestamp –> time of execution

Example:
cpp_results/results_llama2-7b_20251111_160700.json


## Evaluation Criteria

The evaluation of the model responses is **flexible and adaptable** depending on the goals of the researcher or educator.

In this benchmark, the interpretation of results can vary according to the **evaluation framework** applied. For example:

- **Technical evaluation** may focus on:
  - Syntax correctness
  - Compilation success
  - Functional accuracy (e.g., passing predefined test cases)

- **Pedagogical evaluation** may emphasize:
  - The model’s reasoning process and explanation quality
  - Its ability to guide the learner toward a solution without directly revealing it
  - The clarity, tone, and structure of its feedback

In this project, the assessment follows a **custom rubric** designed for measuring the *pedagogical behavior* of LLMs acting as AI coach.  
This rubric includes qualitative dimensions such as:

| **Criteria** | **Level 1 – Needs Improvement** | **Level 2 – Satisfactory** | **Level 3 – Good** | **Level 4 – Excellent** |
|----------------|----------------------------------|-----------------------------|---------------------|--------------------------|
| **Pedagogical Alignment**<br>(How well the AI’s guidance aligns with the learner’s goals) | Provides guidance, but unrelated to the learner’s objectives. | Covers general goals, but with clear gaps. | Well connected with objectives, directs user toward specific improvements. | Deeply integrated with learning goals, anticipates needs, adapts to the learner’s context, and facilitates effective progression. |
| **Feedback / Guidance Quality** | Feedback is vague, generic, or not actionable. | Feedback has some specificity but lacks depth or applicability. | Feedback is clear, useful, and supports user improvement. | Feedback is highly specific, personalized, motivating, and encourages reflection and growth. |
| **Adaptability / Personalization** | Provides standard responses without user adaptation. | Some adaptation to user, but inconsistent. | Reasonably adapts to user profile, detects some differences, adjusts suggestions. | Fully personalized: understands the user’s profile, context, and progress; provides anticipatory and adaptive coaching. |
| **User Engagement & Motivation** | User rarely engages or loses motivation quickly. | Moderate engagement; some interaction achieved. | User is active, AI encourages reflection and continuous improvement. | User is highly engaged; AI sustains motivation, autonomy, and a continuous learning mindset. |
| **Learning Outcomes Effectiveness** | Minimal improvement; little to no measurable progress. | Moderate improvement; some results achieved but inconsistently. | Clear, measurable improvement due to AI coaching. | Significant and sustained learning outcomes; user exceeds goals thanks to AI support. |
| **Ethics, Fairness & Transparency** | Low transparency, possible bias or lack of control. | Some transparency and fairness, but with room for improvement. | Good transparency and fairness, minimal bias, user data handled appropriately. | Fully transparent, equitable, bias-free; user understands system operation and retains control over data and context. |

This rubric allows combining **quantitative** metrics (e.g., correctness, execution success) with **qualitative** indicators (e.g., coaching effectiveness, adaptivity, and motivation).  
It can be adapted for **educational**, **research**, or **comparative** evaluations of different LLMs.
