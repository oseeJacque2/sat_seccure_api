import os
from face_detection import convert_image_to_numpy_array, detect_face
import cv2

def save_user(name, image):
    """Saves the user's image in a folder with the given name.

    Args:
        name (str): Unique name for the user.
        image (numpy.array): User's image.

    Returns:
        bool: True if the image is successfully saved, False otherwise.
        
    NB:For using this function,you call the function convert_image_to_numpy_array(image_path) witch return numpy.array from the Image
    """
    image_detect = detect_face(image)
    if image_detect is None:
        return False
    #create a directory with given name
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    user_image_dir = os.path.join(BASE_DIR, "user_images")
    directory = os.path.join(user_image_dir, name)
    
    os.makedirs(directory, exist_ok=True)
    
    #Generate a unique filename for the image 
    filename = f"profile_{name}.jpg"
    filepath = os.path.join(directory, filename)
    #Save the image 
    try:
        cv2.imwrite(filepath, image_detect)
        print("Image saved successfully")
    except Exception as e:
        print("Error saving image", (e))
        return False 
    

save_user("emilia-clarke", convert_image_to_numpy_array("./person/emilia-clarke/1.jpg"))
save_user("kit-harington", convert_image_to_numpy_array("./person/kit-harington/1.jpg"))
save_user("nikolaj-coster-waldau", convert_image_to_numpy_array("./person/nikolaj-coster-waldau/1.jpg"))
save_user("jacques", convert_image_to_numpy_array("./person/jacques/4.jpg"))

    