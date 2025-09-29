import requests

def send_graph_email(access_token, recipient_email, subject, body):
    url = 'https://graph.microsoft.com/v1.0/me/sendMail'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    email_msg = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "Text",
                "content": body
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": recipient_email
                    }
                }
            ]
        }
    }

    response = requests.post(url, headers=headers, json=email_msg)
    return response.status_code, response.text
