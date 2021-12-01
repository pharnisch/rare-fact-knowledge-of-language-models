import sys
from pathlib import Path
import os
from tokenizers import BertWordPieceTokenizer
import training

mod_path = Path(training.__file__).parent.parent
absolute_path = str(os.path.join(str(mod_path), "training", "data", "wikipedia", "20200501.en"))
paths = [str(x) for x in Path(absolute_path).glob('**/*.txt')]
sys.path.append(f"{mod_path}")

tokenizer = BertWordPieceTokenizer(
    clean_text=True,
    handle_chinese_chars=False,
    strip_accents=False,
    lowercase=False
)

tokenizer.train(files=paths[:5], vocab_size=30_522, min_frequency=2,
                limit_alphabet=1000, wordpieces_prefix='##',
                special_tokens=[
                    '[PAD]', '[UNK]', '[CLS]', '[SEP]', '[MASK]'])

name = str(os.path.join(str(mod_path), "models", "word_piece_tokenizer"))
os.mkdir(name)
tokenizer.save_model(name)