# README.md for Fine-Tuning the phi2-microsoft LLM Model

## Introduction
This README outlines the process for fine-tuning the phi2-microsoft Large Language Model (LLM) using a specific Python script. The goal is to adapt the base model to better perform on a question-answering task related to Python Gekko queries.

## Prerequisites
- Python 3.x
- PyTorch
- Transformers library
- Datasets library
- Matplotlib for visualization
- Requests for data downloading
- PEFT library for efficient fine-tuning

## Installation
Ensure you have the necessary libraries installed:
```bash
pip install torch transformers datasets matplotlib requests
```

## Dataset Preparation
The script begins by downloading training and testing datasets using the `requests` library. The datasets are in JSON Lines format (`.jsonl`).

```python
import requests

# URLs for the datasets
url = 'https://raw.githubusercontent.com/BYU-PRISM/GEKKO/master/docs/llm/'
train = 'train.jsonl'
test = 'test.jsonl'

# Function to download files
def download_file(url, filename):
    ...
```

## Loading and Preprocessing Data
The script uses the `datasets` library to load and preprocess the data.

```python
from datasets import load_dataset

# Load datasets
train_dataset = load_dataset('json', data_files='train.jsonl', split='train')
eval_dataset = load_dataset('json', data_files='test.jsonl', split='train')

# Preprocessing function
def formatting_func(example):
    ...
```

## Model Preparation
The script fine-tunes the `microsoft/phi-2` model. It employs the `AutoModelForCausalLM` and `AutoTokenizer` from the `transformers` library.

```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Load base model and tokenizer
base_model_id = "microsoft/phi-2"
model = AutoModelForCausalLM.from_pretrained(base_model_id, ...)
tokenizer = AutoTokenizer.from_pretrained(base_model_id, ...)
```

## Tokenization and Dataset Preparation
The datasets are tokenized and prepared for training.

```python
# Tokenize datasets
def generate_and_tokenize_prompt(prompt):
    ...

tokenized_train_dataset = train_dataset.map(generate_and_tokenize_prompt)
tokenized_val_dataset = eval_dataset.map(generate_and_tokenize_prompt)
```

## Visualization of Token Lengths
A histogram is generated to visualize the distribution of token lengths in the datasets.

```python
import matplotlib.pyplot as plt

def plot_data_lengths(tokenized_train_dataset, tokenized_val_dataset):
    ...

plot_data_lengths(tokenized_train_dataset, tokenized_val_dataset)
```

## Training Setup
The script sets up the training parameters, including the learning rate, batch size, and other hyperparameters using the `transformers.Trainer` class.

```python
import transformers
from datetime import datetime

# Training configurations
trainer = transformers.Trainer(
    ...
)
```

## Model Training
Finally, the script trains the model with the specified parameters.

```python
# Start training
trainer.train()
```

## Conclusion
This README provides an overview of the process to fine-tune the phi2-microsoft LLM model on a specific dataset. Users can follow these steps to replicate the training process or adapt it for similar fine-tuning tasks.

For detailed usage, refer to the comments and documentation in the script.
