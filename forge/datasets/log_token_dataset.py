import torch
from torch.utils.data import Dataset

class LogTokenDataset(Dataset):
    """Tokenizes raw local Syslog strings into token ID sequences for Transformer tuning."""
    def __init__(self, log_lines, tokenizer=None, max_seq_length=64):
        self.log_lines = log_lines
        self.max_seq_length = max_seq_length
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.log_lines)

    def __getitem__(self, idx):
        line = self.log_lines[idx]
        if self.tokenizer:
            encoded = self.tokenizer(
                line,
                max_length=self.max_seq_length,
                padding="max_length",
                truncation=True,
                return_tensors="pt"
            )
            return encoded["input_ids"].squeeze(0), encoded["attention_mask"].squeeze(0)
        else:
            # Fallback character-level ASCII hashing representation
            tokens = [min(ord(c), 255) for c in line[:self.max_seq_length]]
            tokens += [0] * (self.max_seq_length - len(tokens))
            return torch.tensor(tokens, dtype=torch.long), torch.ones(self.max_seq_length, dtype=torch.long)