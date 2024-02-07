import asyncio
import cv2
import json
import base64
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from entreprise.models import AccesModel, Employee, EmployeeRoom, Face, Qr
from entreprise.serializers import AccesModelSerializer
from swan_project.src.code_qr import detect_qr_code

from swan_project.src.face_detection import detect_face
from swan_project.src.utils_fonctions import compare_images 
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async

class CameraConsumer(AsyncWebsocketConsumer):
    serializer_class = AccesModelSerializer
    #permission_classes = [IsAuthenticated]
    #parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser) 
    queryset = AccesModel.objects.all()
    
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
                cap = cv2.VideoCapture('http://192.168.100.3:8080/video')
                _, frame = cap.read()
                cap.release()
                face_image = await detect_face(frame)
                if face_image is not None:
                    similarity_threshold = 0.7
                    for stored_face in Face.objects.all():
                        stored_image_array = cv2.imread(str(stored_face.face_file.path), cv2.IMREAD_GRAYSCALE)
                        similarity_prob = await compare_images(face_image, stored_image_array)
                        if similarity_prob > similarity_threshold: 
                            
                            employeerooms = EmployeeRoom.objects.filter(employee=stored_face.employee.id)
                            if employeerooms.exists():
                                # Create and save a new AccessModel instance
                                new_access = AccesModel(
                                    employee=stored_face.employee,
                                    room = employeerooms.first().room,
                                    enterprise=stored_face.employee.enterprises.first(),
                                    access_mode='Visage'
                                )
                                new_access.save()
                            await self.send(text_data=json.dumps({"Similar Face": str(stored_face),"access": new_access}))
                            break 
                else:
                    has_qr, content = await detect_qr_code(frame)

                    if has_qr:
                        print("we are here")
                        print(f"the content is {content}")
                        print(f"the has qr is {has_qr}")
                        qr_match = await get_qr_objects(content) 
                        if qr_match:
                            print("I'm here  ooh")
                            print(qr_match.employee)
                            employeerooms = await get_employeeroom_for_employee(qr_match.employee.id)
                            print("I'm here  ooh 222")
                            print(employeerooms)
                            if employeerooms:
                                # Create and save a new AccessModel instance
                                new_access = AccesModel(
                                    employee=stored_face.employee,
                                    room = employeerooms.first().room,
                                    enterprise=stored_face.employee.enterprises.first(),
                                    access_mode='Qr code'
                                )
                                new_access.save()
                            print(new_access)
                            await self.send(text_data=json.dumps({"Matched Qr": str(qr_match),"access": new_access}))
                        else:
                            await self.send(text_data=json.dumps({"No Match": "Aucun code QR correspondant n'a été trouvé"}))

                    else:
                        
                        await self.send(text_data=json.dumps({"Qr content": "No face and Qr code not detect"}))

                await asyncio.sleep(0.1)  # Add a short sleep

            except Exception as e:
                await self.send(text_data=json.dumps({'error': str(e)})) 
                

@sync_to_async
def get_qr_objects(content):
    qr_object = Qr.objects.get(qr_code=content)
    #print("*"*10)
    #print(qr_object.employee)
    #print("a"*10)
    return qr_object

@sync_to_async
def get_employeeroom_for_employee(employee_id):
    return EmployeeRoom.objects.filter(employee=employee_id)
            
