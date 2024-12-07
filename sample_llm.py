from openai import OpenAI
from benchmarking import bench
sanity_check_predictions = []

# model = "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF"

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
prompt_type_to_question = {
        "(Paraph)": "paraphrases",
        "(Ex. Same Content)": "expressing the same content",
        "(Sem Equiv)": "semantically equivalent",
    }

def content_from_sentences(s1,s2):
    prompt_type = "(Paraph)"
    question = prompt_type_to_question[prompt_type]
    return f"Are the following sentences {question}?\n\nSentence 1: {s1}\nSentence 2: {s2}\n\nAnswer with 'Yes' or 'No'"



def predict_llama3_8b_ins_4bit(batch):
    model = "meta-llama-3-8b-instruct"
    prompt_type = "(Paraph)"
    question = prompt_type_to_question[prompt_type]
    return predict_paraphrases_in_batches_lmstudio(model, batch, question)

def predict_llama3_8b_ins_8bit(batch):
    model = "llama-3-8b-instruct-1048k"
    prompt_type = "(Paraph)"
    question = prompt_type_to_question[prompt_type]
    return predict_paraphrases_in_batches_lmstudio(model, batch, question)

def predict_paraphrases_in_batches_lmstudio(
    model, batch, question
):
    """
    Predicts if sentence pairs in a batch are paraphrases using the OpenAI API with optional ICL.

    Parameters:
        batch (list of tuples): List of sentence pairs.
        question: The phrasing of paraphrase for the question

    Returns:
        list: Predictions indicating if each pair is a paraphrase.
    """
    paraphrase_predictions = []
    for sentence1, sentence2 in batch:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful Assistant."},
                {
                    "role": "user",
                    "content": f"Are the following sentences {question}?\n\nSentence 1: {sentence1}\nSentence 2: {sentence2}\n\nAnswer with 'Yes' or 'No'",
                },
            ],
            max_tokens=3,
        )

        answer = completion.choices[0].message.content
        sanity_check_predictions.append(answer[:3])
        paraphrase_predictions.append(answer[:3].lower() == "yes")
    # print(sum(paraphrase_predictions))
    return paraphrase_predictions

if __name__ == '__main__':
    bench(
        methods={
            "llama_3_8b_ins_q4_k_m": predict_llama3_8b_ins_4bit,
        # "llama3_8b_ins_8bit": predict_llama3_8b_ins_8bit,
    },
    bench_id="initial",
    batch_size=10
    )