import cv2
import numpy as np
from PIL import Image
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async


#Detect face from image function
@sync_to_async
def detect_face(image):
    """Detects a face in an image and returns the grayscale face image.

    Args:
        image (numpy.array): Input image

    Returns:
        numpy.array: Grayscale face image
    """
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml')
    faces = face_cascade.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) == 0:
        return None
    elif len(faces) > 1:
        return []
    else:
        (x, y, w, h) = faces[0]
        face_roi = image[y:y + h, x:x + w]
        # Convertir l'image en niveaux de gris
        face_gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        return face_gray 
    

def detect_face2(image):
    """Detects a face in an image and returns the grayscale face image.

    Args:
        image (numpy.array): Input image

    Returns:
        numpy.array: Grayscale face image
    """

    # Charger le classificateur en cascade Haar pour la détection de visage
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml')
    # Effectuer la détection de visage
    faces = face_cascade.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    if len(faces) == 0:
        return None
    elif len(faces) > 1:
        return []
    else:
        (x, y, w, h) = faces[0]
        face_roi = image[y:y + h, x:x + w]
        # Convertir l'image en niveaux de gris
        face_gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        return face_gray



  
    
#Emotion detector 
def get_emotion(image):
    """This function allow to get emotion from image

    Args:
        image (numpy.array): Image whixch will be analyze

    Returns:
        _type_: _description_
    """
    detected_face = detect_face(image)

    if detected_face is None:
        return None

    face_roi = cv2.resize(detected_face, (48, 48))
    face_roi = np.expand_dims(face_roi, axis=0)
    face_roi = np.expand_dims(face_roi, axis=-1)

    emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']

    model = cv2.dnn.readNetFromTensorflow('emotion_detection_model.pb')

    model.setInput(face_roi)
    emotion_predictions = model.forward()

    emotion_index = np.argmax(emotion_predictions)
    emotion_label = emotion_labels[emotion_index]

    return emotion_label


#Convert image to Numpy _array
def convert_image_to_numpy_array(image_path):
    """This function allows converting an image to a numpy array.

    Args:
        image_path (str): The path of the image.

    Returns:
        numpy.array: Numpy array representing the grayscale image.
    """
    # Ouvrir l'image en niveaux de gris
    pil_image = Image.open(image_path).convert("L")

    # Transformer l'image en tableau numpy
    image_array = np.array(pil_image, dtype=np.uint8)

    return image_array


#print(get_emotion(convert_image_to_numpy_array("./person/colere.jpg")))

#print(detect_face(convert_image_to_numpy_array("./person/jacques/2.jpg")))