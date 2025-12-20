
import os
import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

def detect_forgery_with_ml(doc_content: str) -> dict:
    """
    Detects if a document is a forgery using a fine-tuned ML model.
    
    Args:
        doc_content: The full text content of the document.
        
    Returns:
        A dictionary containing the label (AUTHENTIC/FAKE) and the confidence score.
    """
    # Define model path - explicitly pointing to the results directory as requested
    model_path = os.path.join(os.path.dirname(__file__), "results")
    
    # Check if model path exists (or simple check)
    if not os.path.exists(model_path):
        return {"error": "ML model directory 'results' not found."}

    try:
        # Load tokenizer from the directory (saved via save_pretrained)
        tokenizer = DistilBertTokenizer.from_pretrained(model_path)
        
        # Load the state dict from .pth
        weights_path = os.path.join(model_path, "forgery_model.pth")
        if not os.path.exists(weights_path):
             return {"error": f"Model weights not found at {weights_path}"}
        
        state_dict = torch.load(weights_path, map_location=torch.device('cpu'))
        
        # Load model using local config but overriding weights with our .pth
        model = DistilBertForSequenceClassification.from_pretrained(model_path, state_dict=state_dict)
    except Exception as e:
        return {"error": f"Warning: Could not load ML model from '{model_path}'. Check if model files exist. Error: {str(e)}"}

    # Use provided content directly
    text = doc_content

    # Preprocess
    max_length = 512
    inputs = tokenizer(
        text, 
        return_tensors="pt", 
        truncation=True, 
        padding=True, 
        max_length=max_length
    )

    # Inference
    model.eval()
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=1).tolist()[0]
        prediction_id = torch.argmax(logits, dim=1).item()

    # label_id 1 is FAKE, 0 is REAL (based on ml_model.py logic)
    result_label = "FAKE" if prediction_id == 1 else "AUTHENTIC"
    confidence = probabilities[prediction_id]

    return {
        "label": result_label,
        "score": confidence
    }
