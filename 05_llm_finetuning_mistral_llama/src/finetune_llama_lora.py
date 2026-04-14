"""
Fine-tune LLaMA-3-8B with LoRA for enterprise RAG use cases.
"""

import os
from dotenv import load_dotenv
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig, get_peft_model, TaskType
from trl import SFTTrainer

load_dotenv()

BASE_MODEL = os.getenv("BASE_MODEL_LLAMA", "meta-llama/Meta-Llama-3-8B-Instruct")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./outputs/llama3-lora-finetuned")
DATASET_PATH = os.getenv("DATASET_PATH", "./data/train.jsonl")

LLAMA3_SYSTEM = "You are an enterprise AI assistant specialized in answering questions from internal documents."


def format_llama3_prompt(example: dict) -> str:
    """Format using LLaMA-3 chat template."""
    return (
        f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n"
        f"{LLAMA3_SYSTEM}<|eot_id|>"
        f"<|start_header_id|>user<|end_header_id|>\n{example['instruction']}<|eot_id|>"
        f"<|start_header_id|>assistant<|end_header_id|>\n{example['output']}<|eot_id|>"
    )


def load_model_and_tokenizer():
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype="float16",
        bnb_4bit_use_double_quant=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=bnb_config,
        device_map="auto",
    )
    model.config.use_cache = False
    return model, tokenizer


def run_finetune():
    print(f"Loading base model: {BASE_MODEL}")
    model, tokenizer = load_model_and_tokenizer()

    lora_config = LoraConfig(
        r=64,
        lora_alpha=16,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.1,
        bias="none",
        task_type=TaskType.CAUSAL_LM,
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    dataset = load_dataset("json", data_files=DATASET_PATH, split="train")

    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=3,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=8,
        learning_rate=1e-4,
        fp16=True,
        logging_steps=10,
        save_steps=50,
        warmup_steps=50,
        report_to="none",
    )

    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        tokenizer=tokenizer,
        args=training_args,
        formatting_func=format_llama3_prompt,
        max_seq_length=4096,
    )

    print("Starting LoRA fine-tuning...")
    trainer.train()
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print(f"LoRA adapter saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    run_finetune()
