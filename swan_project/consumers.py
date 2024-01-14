import json
import cv2
import base64
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
import cv2
import base64
import json

class CameraConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({'message': 'Server connected'}))

    async def disconnect(self, close_code):
        await self.send(text_data=json.dumps({'message': 'Server disconnected'}))

    async def receive(self, text_data):
        # Allumer la caméra, prendre une image et l'envoyer en temps réel
        cap = cv2.VideoCapture(0)
        _, frame = cap.read()
        cap.release()

        _, img_encoded = cv2.imencode('.png', frame)
        data = base64.b64encode(img_encoded.tobytes()).decode('utf-8')

        # Envoyer l'image en temps réel à tous les clients connectés
        await self.send(text_data=json.dumps({'image': data}))
