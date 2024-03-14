import os

import cv2
import face_recognition
from entreprise.models import Face

from swan_project.src.face_detection import detect_face, detect_face2


#from swan_project.swan_project.src.face_detection import detect_face


def verify_face(employee, image):
    """Verifies if the person in the image is the same as the person with the given name.

    Args:
        employee (str): Employee .
        image (numpy.array): Image to verify.

    Returns:
        float: Probability of similarity between the image and the person's images.

    NB:For using this function,you call the function convert_image_to_numpy_array(image_path) witch return numpy.array from the Image
    """
    #Get all faces for employee
    employee_face = Face.objects.filter(employee=employee)
    if len(employee_face) == 0:
        return 100
    else:
        #Verify if we are a face in the image

        face_dect =  detect_face(image)

        if face_dect is None:
            print("No face detected in the image")
            return 0.0
        else:
            knows_images = []
            for face in employee_face:
                know_image = face_recognition.load_image_file(face.face_file)
                print(know_image)
                # Encoding the know image and the image to verify
                face_encodings = face_recognition.face_encodings(know_image)

                if len(face_encodings) > 0:
                    knows_images.append(face_encodings)

            # Encoding the know image and the image to verify
            known_encodings = knows_images

            # Convert the image to RGB

            print(face_dect)
            rgb_image = cv2.cvtColor(face_dect, cv2.COLOR_BGR2RGB)

            image_encodings = face_recognition.face_encodings(rgb_image)

            if len(image_encodings) == 0:
                return 0.0  # Return 0 similarity if no face is detected in the image
            image_encoding = image_encodings[0]  # Get the first face encoding

            # Compare the encodings and calculate similarity scores

            face_distances = []
            for face_encoding in known_encodings:
                face_distance = face_recognition.face_distance(face_encoding, image_encoding)
                face_distances.append(face_distance)

            print(face_distances)

            similarity_scores = 1 - (sum(face_distances) / len(face_distances))

            # Calculate the average similarity score
            average_similarity = sum(similarity_scores) / len(similarity_scores)

            return average_similarity
    
    
    #Load all images of the person in the directory
    knows_images = []
    for filename in os.listdir(directory):
        #verify if file has .jpg or .png extension
        if filename.endswith(".jpg") or filename.endswith(".png"):
            filepath = os.path.join(directory, filename)
            know_image = face_recognition.load_image_file(filepath)

            # Encoding the know image and the image to verify
            face_encodings = face_recognition.face_encodings(know_image)
            if len(face_encodings) > 0:
                knows_images.append(face_encodings)

    #Encoding the know image and the image to verify
    known_encodings = knows_images

    # Convert the image to RGB
    rgb_image = cv2.cvtColor(face_dect, cv2.COLOR_BGR2RGB)
    image_encodings = face_recognition.face_encodings(rgb_image)
    if len(image_encodings) == 0:
        return 0.0  # Return 0 similarity if no face is detected in the image
    image_encoding = image_encodings[0]  # Get the first face encoding

    #Compare the encodings and calculate similarity scores

    face_distances = []
    for face_encoding in known_encodings:
        face_distance = face_recognition.face_distance(face_encoding, image_encoding)
        face_distances.append(face_distance)

    #print(face_distances)

    similarity_scores = 1 - (sum(face_distances) / len(face_distances))

    # Calculate the average similarity score
    average_similarity = sum(similarity_scores) / len(similarity_scores)

    return average_similarity 


#print("Voici le resultat", verify_face("emilia-clarke", convert_image_to_numpy_array("./person/emilia-clarke/5.jpg")))
#print(verify_face("kit-harington", convert_image_to_numpy_array("./person/kit-harington/1.jpg")))
#print(verify_face("nikolaj-coster-waldau", convert_image_to_numpy_array("./person/nikolaj-coster-waldau/5.jpg")))
#print(verify_face("jacques", convert_image_to_numpy_array("./person/jacques/5.jpg")))


