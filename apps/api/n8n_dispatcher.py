import requests
from pydantic import BaseModel

class WebhookPayload(BaseModel):
    action: str
    email: str
    subject: str
    content: str

def dispatch_to_n8n(payload: WebhookPayload) -> bool:
    """Sends a payload to the n8n webhook dispatcher."""
    webhook_url = "http://localhost:5678/webhook/karvion-dispatcher"
    headers = {
        "Content-Type": "application/json",
        "X-KARVION-API-KEY": "sk_n8n_secure_token_9x!" 
    }
    try:
        response = requests.post(webhook_url, headers=headers, json=payload.model_dump(), timeout=5)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error dispatching to n8n: {str(e)}")
        return False
