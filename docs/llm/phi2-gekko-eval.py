import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

base_model_id = "microsoft/phi-2"

tokenizer = AutoTokenizer.from_pretrained(
    base_model_id,padding_side="left",
    add_eos_token=True,add_bos_token=True,
    use_fast=False,)
tokenizer.pad_token = tokenizer.eos_token

base_model = AutoModelForCausalLM.from_pretrained(
    base_model_id, device_map="auto",
    trust_remote_code=True, load_in_8bit=True,
    torch_dtype=torch.float16,)

eval_tokenizer = AutoTokenizer.from_pretrained(base_model_id, add_bos_token=True, trust_remote_code=True, use_fast=False)
eval_tokenizer.pad_token = eval_tokenizer.eos_token

from peft import PeftModel

# select the checkpoint
ft_model = PeftModel.from_pretrained(base_model, "phi2-gekko/checkpoint-2000")

eval_prompts = ["### Question: Who are you and what were you trained to do?\n ### Answer: ",
                "### Question: How do you increase the maximum iterations in Gekko?\n ### Answer: ",
                "### Question: How do you define an Intermediate variable in Gekko?\n ### Answer: ",
                "### Question: How to create a logical condition (if3) statement with Python Gekko?\n ### Answer: "]

for ep in eval_prompts:
    model_input = eval_tokenizer(ep, return_tensors="pt").to("cuda")

    ft_model.eval()
    with torch.no_grad():
        print(eval_tokenizer.decode(ft_model.generate(**model_input, max_new_tokens=150, repetition_penalty=1.11)[0], skip_special_tokens=True))
