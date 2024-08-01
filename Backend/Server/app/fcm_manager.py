
from flask import jsonify

import firebase_admin
from firebase_admin import credentials, messaging

cred = credentials.Certificate("fcm_prk.json")
firebase_admin.initialize_app(cred)


def pushToClient(client_registration_id, data):
    message = messaging.Message(
        data={
            'reply': str(data),
        },
        token=client_registration_id,
    )
    response = messaging.send(message)
