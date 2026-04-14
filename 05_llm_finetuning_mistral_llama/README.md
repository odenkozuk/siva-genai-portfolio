# LLM Fine-Tuning — Mistral-7B & LLaMA-3-8B with LoRA/QLoRA

Parameter-efficient fine-tuning (PEFT) of Mistral-7B and LLaMA-3-8B for enterprise RAG use cases using QLoRA (4-bit quantization + LoRA adapters). Enables domain-specific LLMs without full GPU infrastructure.

---

## Overview

Off-the-shelf LLMs lack enterprise domain knowledge and often generate generic responses to internal queries. Fine-tuning with QLoRA adapts these models to enterprise-specific tone, terminology, and knowledge — at a fraction of the compute cost of full fine-tuning.

---

## Architecture

```
Base Model (Mistral-7B / LLaMA-3-8B)
    │
    ▼
4-bit Quantization (bitsandbytes NF4)
    │
    ▼
LoRA Adapter Injection (q_proj, v_proj, k_proj, o_proj)
    │
    ▼
SFT Training (Supervised Fine-Tuning via TRL)
    │
    ▼
LoRA Adapter Saved (merge into base on demand)
```

---

## Features

- **QLoRA 4-bit** — trains on consumer GPU (16GB VRAM) via bitsandbytes NF4
- **Mistral fine-tuning** — `[INST]` instruction format, `r=16` LoRA rank
- **LLaMA-3 fine-tuning** — LLaMA-3 chat template, higher `r=64` for broader coverage
- **SFTTrainer** — Hugging Face TRL with gradient accumulation and cosine LR schedule
- **JSONL dataset format** — plug in any enterprise instruction-output pairs
- Sample training data included in `data/train.jsonl`

---

## Project Structure

```
05_llm_finetuning_mistral_llama/
├── src/
│   ├── finetune_mistral.py       # QLoRA fine-tuning for Mistral-7B
│   └── finetune_llama_lora.py    # LoRA fine-tuning for LLaMA-3-8B
├── data/
│   └── train.jsonl               # Sample training data (instruction-output pairs)
├── requirements.txt
└── .env.example
```

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

> GPU with 16GB+ VRAM recommended (e.g. NVIDIA A10, A100, or RTX 4090).

### 2. Configure environment

```bash
cp .env.example .env
```

| Variable | Description |
|----------|-------------|
| `HF_TOKEN` | Hugging Face access token (required for LLaMA-3) |
| `BASE_MODEL_MISTRAL` | Mistral base model ID |
| `BASE_MODEL_LLAMA` | LLaMA-3 base model ID |
| `OUTPUT_DIR` | Directory to save fine-tuned adapters |
| `DATASET_PATH` | Path to JSONL training data |

### 3. Prepare training data

Add instruction-output pairs to `data/train.jsonl`:

```jsonl
{"instruction": "What is the leave policy?", "output": "Employees get 18 days paid leave per year..."}
{"instruction": "How do I reset my password?", "output": "Visit selfservice.company.com and click Forgot Password..."}
```

---

## Training

### Fine-tune Mistral-7B

```bash
python src/finetune_mistral.py
```

### Fine-tune LLaMA-3-8B

```bash
python src/finetune_llama_lora.py
```

Training checkpoints are saved to `OUTPUT_DIR` every 50–100 steps.

---

## LoRA Configuration

| Parameter | Mistral | LLaMA-3 |
|-----------|---------|---------|
| Rank (`r`) | 16 | 64 |
| Alpha | 32 | 16 |
| Dropout | 0.05 | 0.1 |
| Quantization | 4-bit NF4 | 4-bit NF4 |
| Target Modules | q/v/k/o proj | q/v/k/o/gate/up/down proj |

---

## Inference with Fine-tuned Adapter

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

base_model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")
model = PeftModel.from_pretrained(base_model, "./outputs/mistral-finetuned")
tokenizer = AutoTokenizer.from_pretrained("./outputs/mistral-finetuned")

inputs = tokenizer("<s>[INST] What is the expense policy? [/INST]", return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Base Models | Mistral-7B-Instruct-v0.2, LLaMA-3-8B-Instruct |
| PEFT | LoRA / QLoRA (PEFT library) |
| Training | TRL SFTTrainer |
| Quantization | bitsandbytes 4-bit NF4 |
| Framework | Hugging Face Transformers |
| Language | Python 3.12 |
