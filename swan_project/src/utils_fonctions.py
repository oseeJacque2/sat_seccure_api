
import cv2
import numpy as np
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
import face_recognition

from PIL import Image
import imagehash


@sync_to_async
def compare_images(image1_array, image2_array):
    """
    Compare deux images en niveaux de gris représentées en tant que tableaux NumPy.
    Redimensionne les images si elles n'ont pas la même forme.

    Args:
        image1_array (numpy.array): Tableau NumPy de la première image.
        image2_array (numpy.array): Tableau NumPy de la deuxième image.

    Returns:
        float: Probabilité de similitude entre 0 et 1.
    """
    if image1_array.shape != image2_array.shape:
        image1_array = cv2.resize(image1_array, (image2_array.shape[1], image2_array.shape[0]))
    
    abs_diff = np.abs(image1_array - image2_array)

    mean_diff = np.mean(abs_diff)

    similarity_prob = mean_diff / 255.0  # 255 car les pixels sont généralement dans la plage 0-255

    return similarity_prob 


@sync_to_async
def compare_images2(image_path1, image_path2):
    # Chargez les images
    img1 = Image.open(image_path1)
    img2 = Image.open(image_path2)

    # Obtenez les hachages d'images
    hash1 = imagehash.average_hash(img1)
    hash2 = imagehash.average_hash(img2)

    # Comparez les hachages
    precision = 100 - (hash1 - hash2) / len(hash1.hash) * 100

    return precision


@sync_to_async
def compare_faces(image_path1, image_path2):
    image1 = face_recognition.load_image_file(image_path1)
    image2 = face_recognition.load_image_file(image_path2)

    face_encodings_image1 = face_recognition.face_encodings(image1)
    face_encodings_image2 = face_recognition.face_encodings(image2)

    if len(face_encodings_image1) == 0 or len(face_encodings_image2) == 0:
        return 0  

    face_encoding1 = face_encodings_image1[0]
    face_encoding2 = face_encodings_image2[0]

    face_distance = face_recognition.face_distance([face_encoding1], face_encoding2)
    
    similarity = 1 - face_distance[0]

    return similarity


@sync_to_async
def compare_recognition(image_path1, image_path2):
    # Chargez les images
    image1 = face_recognition.load_image_file(image_path1)
    image2 = face_recognition.load_image_file(image_path2)

    # Obtenez les encodages (embeddings) des visages dans chaque image
    face_encodings_image1 = face_recognition.face_encodings(image1)
    face_encodings_image2 = face_recognition.face_encodings(image2)

    # Vérifiez s'il y a au moins un visage dans chaque image
    if len(face_encodings_image1) == 0 or len(face_encodings_image2) == 0:
        return 0  # Aucun visage trouvé dans au moins l'une des images

    # Comparez les encodages des visages (utilisez le premier visage trouvé dans chaque image)
    face_encoding1 = face_encodings_image1[0]
    face_encoding2 = face_encodings_image2[0]

    # Utilisez la distance euclidienne pour mesurer la similitude
    face_distance = face_recognition.face_distance([face_encoding1], face_encoding2)

    # La distance est inversément proportionnelle à la similitude
    # Plus la distance est petite, plus les visages sont similaires
    similarity = 1 - face_distance[0]

    return similarity


