from datasets import load_dataset
from tqdm.auto import tqdm
import re
from pathlib import Path


dataset_name = "wikipedia"
dataset_version = "20200501.en"
dataset = load_dataset(dataset_name, dataset_version)

path = f"./{dataset_name}/{dataset_version}/"
Path(path).mkdir(parents=True, exist_ok=True)

text_data = []
file_count = 0
for sample in tqdm(dataset['train']):
    sample = sample['text'].replace('\n', ' ')  # "\n" -> " "
    #sample = sample.replace("  "," ")

    words = sample.split(" ")
    new_words = []
    for idx, word in enumerate(words):
        if ":" in word:
            continue
        new_words.append(word)
    sample = " ".join(new_words)

    sample = sample.replace("()", " ")  # "()" -> " "
    sample = re.sub("( +)", " ", sample)  # "( )", "(  )", ... -> " "
    nonBreakSpace = u'\xa0'
    sample = sample.replace(nonBreakSpace, " ")  # "[NBSP]" -> " "
    sample = re.sub(" +", " ", sample)  # " ", "  ", ... -> " "

    text_data.append(sample)
    if len(text_data) == 10_000:
        # once we git the 10K mark, save to file
        with open(f'{path}text_{file_count}.txt', 'w', encoding='utf-8') as fp:
            fp.write('\n'.join(text_data))
        text_data = []
        file_count += 1
# after saving in 10K chunks, we will have leftover samples, we save those now too
with open(f'{path}/text_{file_count}.txt', 'w', encoding='utf-8') as fp:
    fp.write('\n'.join(text_data))