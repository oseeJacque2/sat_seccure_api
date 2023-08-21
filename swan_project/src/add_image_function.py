import os

from verify_face import verify_face
from face_detection import convert_image_to_numpy_array, detect_face
import cv2

def add_face(name,image):
    """Adds a new face image to the person with the given name.

    Args:
        name (str): Name of the person.
        image (numpy.array): Face image to add.

    Returns:
        bool: True if the face image is successfully added, False otherwise.
    """
    probability = verify_face(name, image)

    if probability < 0.50:
        print("Le pourcentage d'appartenance est", probability)
        return False
    else:

        #Get the directory for the name
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        #Get the directory from the user by his/her name
        directory = os.path.join(os.path.join(BASE_DIR, "user_images"), name)

        #Generate a unique filename for the new image face
        filename = f'profile_{len(os.listdir(directory))+1}.jpg'
        filepath = os.path.join(directory, filename)

        #Get only the face of in  the image
        image_detect = detect_face(image)

        #Let's save the new image
        try:
            cv2.imwrite(filepath, image_detect)
            print("New face image added successfully.")
            return True
        except Exception as e:
            print("Error adding new face image:", str(e))
            return False


print(add_face("emilia-clarke", convert_image_to_numpy_array("./person/emilia-clarke/2.jpg")))
print(add_face("kit-harington", convert_image_to_numpy_array("./person/kit-harington/2.jpg")))
print(add_face("nikolaj-coster-waldau",convert_image_to_numpy_array("./person/nikolaj-coster-waldau/2.jpg")))
print(add_face("jacques", convert_image_to_numpy_array("./person/jacques/2.jpg")))


