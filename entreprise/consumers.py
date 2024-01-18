import asyncio
import cv2
import json
import base64
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from swan_project.src.code_qr import detect_qr_code

from swan_project.src.face_detection import detect_face

class CameraConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()
        self.camera_on = True
        await self.send(text_data=json.dumps({'message': 'Server connected'}))
        #await self.capture_and_send_image()

    async def disconnect(self, close_code):
        self.camera_on = False
        await self.send(text_data=json.dumps({'message': 'Server disconnected'}))


    async def receive(self, text_data):
        data = json.loads(text_data) 
        command = data.get("command","") 
        print(command) 
        
        if command == "capture_image":
            
           await self.capture_and_send_image() 
        else:
            await self.send(text_data=json.dumps({'message': 'Server connected'}))
       
    
    
    async def capture_and_send_image(self):
        
        while self.camera_on:
            try:
                cap = cv2.VideoCapture(0)
                _, frame = cap.read()
                cap.release()

                face_image = detect_face(frame)
                if face_image is not None:
                    await self.send(text_data=json.dumps({"Faces": face_image}))
                else:
                    has_qr, content = detect_qr_code(frame)
                    if has_qr:
                        await self.send(text_data=json.dumps({"Qr content": content}))
                    else:
                        await self.send(text_data=json.dumps({"Qr content": "No face and Qr code not detect"}))

                await asyncio.sleep(0.1)  # Add a short sleep

            except Exception as e:
                await self.send(text_data=json.dumps({'error': str(e)}))
            
