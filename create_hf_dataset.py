from datasets import Dataset, DatasetDict
import os
import pandas as pd

# Hugging Face Token
HF_TOKEN = os.getenv("HF_TOKEN")
HF_DATASET_REPO = "cvelist/cvelist/vuln-list"  # Replace with your dataset repo

def create_dataset():
    # Example data
    data = {
        "id": [1, 2, 3],
        "text": ["Hello world!", "Hugging Face is awesome!", "GitHub Actions FTW!"],
        "label": [0, 1, 0]
    }
    
    # Create a Pandas DataFrame
    df = pd.DataFrame(data)

    # Convert to Hugging Face Dataset
    hf_dataset = Dataset.from_pandas(df)

    # Save locally
    hf_dataset.save_to_disk("dataset")

    # Push to Hugging Face Hub
    hf_dataset.push_to_hub(HF_DATASET_REPO, token=HF_TOKEN)

if __name__ == "__main__":
    create_dataset()
