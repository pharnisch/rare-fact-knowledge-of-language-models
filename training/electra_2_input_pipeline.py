from transformers import ElectraTokenizer

# initialize the tokenizer using the tokenizer we initialized and saved to file
tokenizer = ElectraTokenizer.from_pretrained('bert_test_tokenizer', max_len=512)


with open('data/text/wiki_en/text_0.txt', 'r', encoding='utf-8') as fp:
    lines = fp.read().split('\n')[:10]

    batch = tokenizer(lines,add_special_tokens=True, max_length=512, padding='max_length', truncation=True)


    import torch


    labels = torch.tensor(batch["input_ids"])
    mask = torch.tensor(batch["attention_mask"])

    # make copy of labels tensor, this will be input_ids
    input_ids = labels.detach().clone()
    # create random array of floats with equal dims to input_ids
    rand = torch.rand(input_ids.shape)
    # mask random 15% where token is not 0 [PAD], 1 [CLS], or 2 [SEP]
    mask_arr = (rand < .15) * (input_ids != 0) * (input_ids != 1) * (input_ids != 2)
    # loop through each row in input_ids tensor (cannot do in parallel)
    for i in range(input_ids.shape[0]):
        # get indices of mask positions from mask array
        selection = torch.flatten(mask_arr[i].nonzero()).tolist()
        # mask input_ids
        input_ids[i, selection] = 4  # our custom [MASK] token == 3





encodings = {'input_ids': input_ids, 'attention_mask': mask, 'labels': labels}
class Dataset(torch.utils.data.Dataset):
    def __init__(self, encodings):
        # store encodings internally
        self.encodings = encodings

    def __len__(self):
        # return the number of samples
        return self.encodings['input_ids'].shape[0]

    def __getitem__(self, i):
        # return dictionary of input_ids, attention_mask, and labels for index i
        return {key: tensor[i] for key, tensor in self.encodings.items()}

dataset = Dataset(encodings)
loader = torch.utils.data.DataLoader(dataset, batch_size=16, shuffle=True)


from transformers import ElectraConfig
config = ElectraConfig(
    vocab_size=30_522,  # we align this to the tokenizer vocab_size
    max_position_embeddings=513,
    hidden_size=256,
    num_attention_heads=4,
    num_hidden_layers=6, # this change is only because of computational reduction in prototype
    type_vocab_size=1 # this change makes sense (?)
)
from transformers import RobertaForMaskedLM
model = RobertaForMaskedLM(config)

device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
# and move our model over to the selected device
model.to(device)

from transformers import AdamW
# activate training mode
model.train()
# initialize optimizer
optim = AdamW(model.parameters(), lr=1e-4)

from tqdm.auto import tqdm
epochs = 2
for epoch in range(epochs):
    # setup loop with TQDM and dataloader
    loop = tqdm(loader, leave=True)
    for batch in loop:
        # initialize calculated gradients (from prev step)
        optim.zero_grad()
        # pull all tensor batches required for training
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)
        # process
        outputs = model(input_ids, attention_mask=attention_mask,
                        labels=labels)

        # extract loss
        loss = outputs[0]
        # calculate loss for every parameter that needs grad update
        loss.backward()
        # update parameters
        optim.step()
        # print relevant info to progress bar
        loop.set_description(f'Epoch {epoch}')
        loop.set_postfix(loss=loss.item())

model.save_pretrained('./electra_test_model')  # and don't forget to save