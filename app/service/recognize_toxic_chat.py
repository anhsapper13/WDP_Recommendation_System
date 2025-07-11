from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer

model_name = "Anhsapper/toxic-chat-model"
fine_tuned_model = AutoModelForSequenceClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
toxic_chat_pipeline = pipeline("text-classification", model=fine_tuned_model, tokenizer=tokenizer)

def recognize_toxic_chat(message: str) -> dict:
    result = toxic_chat_pipeline(message)[0]
    return {
        "is_toxic": result['label'] == 'LABEL_1', 
        "score": result['score']
    }
