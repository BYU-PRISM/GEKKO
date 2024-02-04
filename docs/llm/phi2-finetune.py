import requests

url = 'https://raw.githubusercontent.com/BYU-PRISM/GEKKO/master/docs/llm/'
train = 'train.jsonl'
test = 'test.jsonl'

def download_file(url,filename):
    # Send a GET request to the URL
    response = requests.get(url+filename)

    # Check if the request was successful
    if response.status_code == 200:
        # Open the local file in write-binary mode
        with open(filename, 'wb') as file:
            file.write(response.content)
        print(f'Retrieved {filename}')
    else:
        print(f"Failed to download file. HTTP Status Code: {response.status_code}")

download_file(url,train)
download_file(url,test)

from datasets import load_dataset
train_dataset = load_dataset('json', data_files='train.jsonl', split='train')
eval_dataset = load_dataset('json', data_files='test.jsonl', split='train')

def formatting_func(example):
    text = f"### Question: {example['question']}\n ### Answer: {example['answer']}\n||||"
    return text

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

base_model_id = "microsoft/phi-2"
model = AutoModelForCausalLM.from_pretrained(base_model_id, trust_remote_code=True, torch_dtype=torch.float16, load_in_8bit=True)

tokenizer = AutoTokenizer.from_pretrained(
    base_model_id, padding_side="left",
    add_eos_token=True, add_bos_token=True,
    use_fast=False,)
tokenizer.pad_token = tokenizer.eos_token

def generate_and_tokenize_prompt(prompt):
    return tokenizer(formatting_func(prompt))

tokenized_train_dataset = train_dataset.map(generate_and_tokenize_prompt)
tokenized_val_dataset = eval_dataset.map(generate_and_tokenize_prompt)

import matplotlib.pyplot as plt

def plot_data_lengths(tokenized_train_dataset, tokenized_val_dataset):
    lengths = [len(x['input_ids']) for x in tokenized_train_dataset]
    lengths += [len(x['input_ids']) for x in tokenized_val_dataset]
    print(len(lengths))

    # Plotting the histogram
    plt.figure(figsize=(10, 6))
    plt.hist(lengths, bins=20, alpha=0.7, color='blue')
    plt.xlabel('Length of input_ids')
    plt.ylabel('Frequency')
    plt.title('Distribution of Lengths of input_ids')
    plt.savefig('token_length.png',dpi=300)
    #plt.show()

plot_data_lengths(tokenized_train_dataset, tokenized_val_dataset)

max_length = 750 # truncation max length

def generate_and_tokenize_prompt2(prompt):
    result = tokenizer(
        formatting_func(prompt),
        truncation=True,
        max_length=max_length,
        padding="max_length",
    )
    result["labels"] = result["input_ids"].copy()
    return result

tokenized_train_dataset = train_dataset.map(generate_and_tokenize_prompt2)
tokenized_val_dataset = eval_dataset.map(generate_and_tokenize_prompt2)

print(tokenized_train_dataset[1]['input_ids'])

eval_prompt = "### Question: How do you increase maximum iterations in Python Gekko?\n ### Answer: "

# Init an eval tokenizer so it doesn't add padding or eos token
eval_tokenizer = AutoTokenizer.from_pretrained(
    base_model_id,
    add_bos_token=True,
    use_fast=False,)

model_input = eval_tokenizer(eval_prompt, return_tensors="pt").to("cuda")

model.eval()
with torch.no_grad():
    print(eval_tokenizer.decode(model.generate(**model_input, max_new_tokens=256, repetition_penalty=1.15)[0], skip_special_tokens=True))

def print_trainable_parameters(model):
    trainable_params = 0
    all_param = 0
    for _, param in model.named_parameters():
        all_param += param.numel()
        if param.requires_grad:
            trainable_params += param.numel()
    print(
        f"trainable params: {trainable_params} || all params: {all_param} || trainable%: {100 * trainable_params / all_param}"
    )

from peft import LoraConfig, get_peft_model

config = LoraConfig(
    r=32, lora_alpha=64,
    target_modules=["Wqkv","fc1","fc2",],
    bias="none",
    lora_dropout=0.05,
    task_type="CAUSAL_LM")

model = get_peft_model(model, config)
print_trainable_parameters(model)

if torch.cuda.device_count() > 1:
    model.is_parallelizable = True
    model.model_parallel = True

import transformers
from datetime import datetime

project = "gekko"
base_model_name = "phi2"
run_name = base_model_name + "-" + project
output_dir = "./" + run_name

trainer = transformers.Trainer(
    model=model,
    train_dataset=tokenized_train_dataset,
    eval_dataset=tokenized_val_dataset,
    args=transformers.TrainingArguments(
        output_dir=output_dir,
        warmup_steps=1,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=1,
        max_steps=2000,
        learning_rate=2.5e-5, # Want a small lr for finetuning
        optim="paged_adamw_8bit",
        logging_steps=100,            # When to start reporting loss
        logging_dir="./logs",        # Directory for storing logs
        save_strategy="steps",       # Save the model checkpoint every logging step
        save_steps=100,               # Save checkpoints every 50 steps
        evaluation_strategy="steps", # Evaluate the model every logging step
        eval_steps=100,               # Evaluate and save checkpoints every 50 steps
        do_eval=True,                # Perform evaluation at the end of training
        run_name=f"{run_name}-{datetime.now().strftime('%Y-%m-%d-%H-%M')}"
    ),
    data_collator=transformers.DataCollatorForLanguageModeling(tokenizer, mlm=False),
)

model.config.use_cache = False  # silence the warnings. Please re-enable for inference!
trainer.train()
