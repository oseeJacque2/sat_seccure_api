import asyncio
import os
import tempfile
import cv2
import json
import base64
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from entreprise.models import AccesModel, Employee, EmployeeRoom, Enterprise, Face, Qr, Room
from entreprise.serializers import AccesModelSerializer
from swan_project.src.code_qr import detect_qr_code

from swan_project.src.face_detection import detect_face
from swan_project.src.utils_fonctions import compare_faces, compare_images, compare_images2 
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
                temp_dir = tempfile.mkdtemp()
                face_image = await detect_face(frame)
                new_access = None
                if face_image is not None:
                    #Enregistrer l'image temporairement 
                    temp_image_path = os.path.join(temp_dir, 'temp_image.jpg')
                    cv2.imwrite(temp_image_path, face_image)
                    
                    similarity_threshold = 0.75 
                    faces = Face.objects.all() 
                    for stored_face in faces :
                        #stored_image_array = cv2.imread(str(stored_face.face_file.path), cv2.IMREAD_GRAYSCALE) 
                        similarity_prob = await compare_faces(temp_image_path, stored_face.face_file.path)
                        print(f"Face similarity {similarity_prob}")
                        if similarity_prob > similarity_threshold: 
                            employeerooms = await get_employeeroom_for_employee(stored_face.employee.id) 
                            
                            if len(employeerooms) >= 1:
                                # Create and save a new AccessModel instance
                                room = await get_room(employeerooms[0].room.id)
                                enterprise = employeerooms[0].employee.enterprise
                                new_access = AccesModel(
                                    employee=stored_face.employee,
                                    room = room,
                                    enterprise=enterprise,
                                    access_mode='Visage'
                                ) 
                                print("New access created")
                                new_access.save()
                                await self.send(text_data=json.dumps({"Similar Face": str(stored_face.face_file.url),"access": AccesModelSerializer(new_access).data}))
                                break
                            else:
                                await self.send(text_data=json.dumps({"Similar Face": str(stored_face.face_file.url),"access": "no access"}))
                                break
                            
                else:
                    has_qr, content = await detect_qr_code(frame) 
                    if has_qr:
                        qr_match = await get_qr_objects(content) 

                        if qr_match:
                            employeerooms = await get_employeeroom_for_employee(qr_match.id)
                            if len(employeerooms) >= 1:
                                # Create and save a new AccessModel instance
                                
                                room = await get_room(employeerooms[0].room.id)
                                enterprise = employeerooms[0].employee.enterprise
                                new_access = AccesModel(
                                    employee=qr_match,
                                    room = room,
                                    enterprise=enterprise,
                                    access_mode='Qr code'
                                )
                                new_access.save()
                            print(new_access)
                            await self.send(text_data=json.dumps({"Matched Qr": str(qr_match),"access": AccesModelSerializer(new_access).data}))
                        else:
                            await self.send(text_data=json.dumps({"No Match": "Aucun code QR correspondant n'a été trouvé"}))

                    else:
                        
                        await self.send(text_data=json.dumps({"Qr content": "No face and Qr code not detect"}))

                await asyncio.sleep(0.1)  # Add a short sleep

            except Exception as e:
                await self.send(text_data=json.dumps({'error': str(e)}))  
                
            finally: 
                cap.release()
                

@sync_to_async
def get_qr_objects(content):
    try:
        qr_objects = Qr.objects.filter(qr_code=content)
        if qr_objects.exists():
            return qr_objects.first().employee
        else:
            return None
    except Qr.DoesNotExist:
        return None


@sync_to_async
def get_employeeroom_for_employee(employee_id):
    try:
        employee_rooms = EmployeeRoom.objects.filter(employee=employee_id)
        return list(employee_rooms)
    except EmployeeRoom.DoesNotExist:
        return []   
    
@sync_to_async
def get_room(room_id): 
    try:
        room = Room.objects.filter(id=room_id)
        return room.first()
    except Room.DoesNotExist:
        return None    
    
@sync_to_async 
def get_employee_enterprise(enterprise_id):
    try:
        enterprise = Enterprise.objects.filter(id = enterprise_id) 
        return enterprise.first() 
    except Enterprise.DoesNotExist :   
        return None   
