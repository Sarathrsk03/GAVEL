import os
import torch
import numpy as np
from tqdm.auto import tqdm
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from transformers import (
    DistilBertTokenizer,
    DistilBertForSequenceClassification,
    Trainer,
    TrainingArguments
)
from torch.utils.data import Dataset
from transformers import DistilBertTokenizerFast


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------
REAL_DATA_PATH = "dataset/real_data"
FAKE_DATA_PATH = "dataset/fake_data"
MODEL_NAME = "distilbert-base-uncased"
MAX_LENGTH = 512
BATCH_SIZE = 8
EPOCHS = 3


# ------------------------------------------------------------
# Dataset Class
# ------------------------------------------------------------
class ForgeryDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)


# ------------------------------------------------------------
# Data Loading
# ------------------------------------------------------------
def load_data():
    print("\n[STEP] Loading dataset files...")
    texts = []
    labels = []

    real_files = [f for f in os.listdir(REAL_DATA_PATH) if f.endswith(".txt")]
    fake_files = [f for f in os.listdir(FAKE_DATA_PATH) if f.endswith(".txt")]

    print(f"[INFO] Found {len(real_files)} REAL files")
    print(f"[INFO] Found {len(fake_files)} FAKE files")

    print("\n[STEP] Reading REAL documents...")
    for filename in tqdm(real_files, desc="Real Docs", unit="file"):
        with open(os.path.join(REAL_DATA_PATH, filename), "r", encoding="utf-8", errors="ignore") as f:
            texts.append(f.read())
            labels.append(0)

    print("[DONE] REAL documents loaded")

    print("\n[STEP] Reading FAKE documents...")
    for filename in tqdm(fake_files, desc="Fake Docs", unit="file"):
        with open(os.path.join(FAKE_DATA_PATH, filename), "r", encoding="utf-8", errors="ignore") as f:
            texts.append(f.read())
            labels.append(1)

    print("[DONE] FAKE documents loaded")
    print("[SUCCESS] Dataset loading completed\n")

    return texts, labels


# ------------------------------------------------------------
# Metrics
# ------------------------------------------------------------
def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)

    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, preds, average="binary"
    )
    acc = accuracy_score(labels, preds)

    return {
        "accuracy": acc,
        "f1": f1,
        "precision": precision,
        "recall": recall
    }


# ------------------------------------------------------------
# Training
# ------------------------------------------------------------

def batch_tokenize_with_progress(tokenizer, texts, batch_size=512):
    encodings = {"input_ids": [], "attention_mask": []}

    for i in tqdm(range(0, len(texts), batch_size), desc="Tokenizing", unit="batch"):
        batch_texts = texts[i:i + batch_size]
        batch_enc = tokenizer(
            batch_texts,
            truncation=True,
            padding=True,
            max_length=MAX_LENGTH
        )

        encodings["input_ids"].extend(batch_enc["input_ids"])
        encodings["attention_mask"].extend(batch_enc["attention_mask"])

    return encodings


def train_model():
    print("\n================ TRAINING STARTED ================\n")

    print("[STEP] Loading data...")
    texts, labels = load_data()

    print(f"[INFO] Total samples: {len(texts)}")
    print(f"[INFO] Real: {labels.count(0)} | Fake: {labels.count(1)}")

    print("\n[STEP] Splitting train / validation data...")
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        texts, labels, test_size=0.2, random_state=42
    )
    print("[DONE] Data split completed")

    print("\n[STEP] Loading tokenizer...")
    tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_NAME)
    print("[DONE] Tokenizer loaded")


    embedding_path = "cached_embeddings/train_embeddings.pt"

    if os.path.exists(embedding_path):
        print("\n[STEP] Loading cached training tokenization...")
        cached = torch.load(embedding_path)

        train_encodings = {
            "input_ids": cached["input_ids"],
            "attention_mask": cached["attention_mask"]
        }
        train_labels = cached["labels"]

        print("[SUCCESS] Cached training tokenization loaded")

    else:
        print("\n[STEP] Tokenizing training data with progress bar...")
        train_encodings = batch_tokenize_with_progress(
            tokenizer,
            train_texts,
            batch_size=512
        )

        os.makedirs("cached_embeddings", exist_ok=True)
        torch.save(
            {
                "input_ids": train_encodings["input_ids"],
                "attention_mask": train_encodings["attention_mask"],
                "labels": train_labels
            },
            embedding_path
        )

        print("[SUCCESS] Training tokenization saved")



    print("\n[STEP] Tokenizing validation data...")
    print("\n[STEP] Tokenizing validation data with progress bar...")
    val_encodings = batch_tokenize_with_progress(
        tokenizer,
        val_texts,
        batch_size=512
    )
    os.makedirs("cached_embeddings", exist_ok=True)
    torch.save(
        {
            "input_ids": val_encodings["input_ids"],
            "attention_mask": val_encodings["attention_mask"],
            "labels": val_labels
        },
        "cached_embeddings/val_embeddings.pt"
    )
    print("[DONE] Validation data tokenized")

    print("\n[STEP] Creating dataset objects...")
    train_dataset = ForgeryDataset(train_encodings, train_labels)
    val_dataset = ForgeryDataset(val_encodings, val_labels)
    print("[DONE] Dataset objects created")

    print("\n[STEP] Initializing model...")
    model = DistilBertForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=2
    )
    print("[DONE] Model initialized")

    print("\n[STEP] Setting up training arguments...")
    training_args = TrainingArguments(
        output_dir="./results",
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        warmup_steps=50,
        weight_decay=0.01,
        logging_dir="./logs",
        logging_steps=10,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        disable_tqdm=False,
        report_to="none"
    )
    print("[DONE] Training arguments set")

    print("\n[STEP] Initializing Trainer...")
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics
    )
    print("[DONE] Trainer initialized")

    print("\n================ TRAINING IN PROGRESS ================\n")
    trainer.train()
    print("\n================ TRAINING COMPLETED ================\n")

    print("[STEP] Saving model and tokenizer...")
    model.save_pretrained("./forgery_detector_model")
    tokenizer.save_pretrained("./forgery_detector_model")
    print("[SUCCESS] Model saved to ./forgery_detector_model\n")


# ------------------------------------------------------------
# Prediction
# ------------------------------------------------------------
def predict(file_path):
    print("\n================ PREDICTION STARTED ================\n")
    print(f"[INFO] Input file: {file_path}")

    if not os.path.exists("./forgery_detector_model"):
        print("[ERROR] Model not found. Please train the model first.")
        return

    print("[STEP] Loading tokenizer and model...")
    # Load from the saved directory
    try:
        tokenizer = DistilBertTokenizer.from_pretrained("./forgery_detector_model")
        model = DistilBertForSequenceClassification.from_pretrained("./forgery_detector_model")
    except OSError:
        print("[ERROR] Could not load model from ./forgery_detector_model. Ensure you have trained it.")
        return

    print("[STEP] Processing input file...")
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
    except Exception as e:
        print(f"[ERROR] Could not read file: {e}")
        return

    inputs = tokenizer(
        text, 
        return_tensors="pt", 
        truncation=True, 
        padding=True, 
        max_length=MAX_LENGTH
    )

    print("[STEP] Running inference...")
    model.eval()
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=1).tolist()[0]
        prediction_id = torch.argmax(logits, dim=1).item()

    result = "FAKE" if prediction_id == 1 else "REAL"
    confidence = probabilities[prediction_id]

    print(f"\n[RESULT] Document is: {result}")
    print(f"[INFO] Confidence: {confidence:.4f}")
    print("\n================ PREDICTION COMPLETED ================\n")
    
    return {
        "is_fake": prediction_id == 1,
        "confidence": confidence,
        "label": result
    }

if __name__ == "__main__":
    # If a file argument is provided, predict. Otherwise train.
    import sys
    if len(sys.argv) > 1 and sys.argv[1] != "train":
        predict(sys.argv[1])
    else:
        train_model()
