import os
from PIL import Image
import cv2
from pyzbar.pyzbar import decode
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async


def read_qr_code(image_path):
    """This function allows you to decode a QR code from its image

    Args:
        image_path (String): Code QR image path

    Returns:
        String: QR code content from image.If the image is empty we return None
    """
    try:
        # Opening the QR image
        image = Image.open(image_path)

        # Decoding the image
        qr_codes = decode(image)

        if qr_codes:
            # qr code content recovery
            qr_code_content = qr_codes[0].data.decode('utf-8')
            return qr_code_content
        else:
            print("No QR code found in image")
            return None
    except Exception as e:
        print(f"An error occurred while reading the QR code: {str(e)}")
        return None 
    
@sync_to_async
def detect_qr_code(image_array):
    # Convertir le tableau NumPy en image OpenCV
    image = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)

    # Détecter les codes QR dans l'image
    decoded_objects = decode(image)

    # Si des codes QR sont détectés, retourner le premier code QR et True
    if decoded_objects:
        qr_content = decoded_objects[0].data.decode('utf-8')
        return True, qr_content
    else:
        # Sinon, retourner False et une chaîne vide
        return False, ''