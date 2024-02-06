import json

def read_questions(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return [json.loads(line) for line in lines]

def save_questions(questions, file_path):
    with open(file_path, 'w') as file:
        for question in questions:
            file.write(json.dumps(question) + '\n')

def main():
    input_file = 'train.jsonl'  # Path to the file with questions and answers
    output_file = 'saved.json'  # Path to save accepted questions and answers

    questions = read_questions(input_file)
    accepted_questions = []

    for q in questions:
        print('-'*40)
        print("Question:", q["question"])
        print("Answer:", q["answer"])
        print('-'*40)
        print("Press enter to keep, spacebar+enter to discard.")
        choice = input()
        if choice == '':
            accepted_questions.append(q)

    save_questions(accepted_questions, output_file)
    print("Selected questions saved to", output_file)

if __name__ == "__main__":
    main()
