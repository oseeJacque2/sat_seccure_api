
import cv2
import numpy as np
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async

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
    # Assurez-vous que les tableaux ont la même forme
    if image1_array.shape != image2_array.shape:
        # Redimensionner les images pour avoir la même forme
        image1_array = cv2.resize(image1_array, (image2_array.shape[1], image2_array.shape[0]))
    
    # Calculez la différence absolue entre les pixels
    abs_diff = np.abs(image1_array - image2_array)

    # Calculez la moyenne de la différence absolue
    mean_diff = np.mean(abs_diff)

    # Normalisez la différence moyenne pour obtenir une probabilité de similitude
    similarity_prob = mean_diff / 255.0  # 255 car les pixels sont généralement dans la plage 0-255

    return similarity_prob
