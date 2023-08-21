import os, face_recognition
from face_detection import convert_image_to_numpy_array

def verify_face(name,image):
    """Verifies if the person in the image is the same as the person with the given name.

    Args:
        name (str): Name of the person.
        image (numpy.array): Image to verify.

    Returns:
        float: Probability of similarity between the image and the person's images.
        
    NB:For using this function,you call the function convert_image_to_numpy_array(image_path) witch return numpy.array from the Image
    """  
    #Let's get the directory path for  the user's images 
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    directory = os.path.join(os.path.join(BASE_DIR,"user_images"),name)
    
    #Load all images of the person in the directory 
    knows_images=[]
    for filename in os.listdir(directory):
        #verify if file has .jpg or .png extension
        if filename.endswith(".jpg") or filename.endswith(".png"):
            filepath=os.path.join(directory,filename)
            know_image=face_recognition.load_image_file(filepath)
            knows_images.append(know_image) 
            
    #Encoding the know image and the image to verify 
    known_encodings=[face_recognition.face_encodings(img)[0] for img in knows_images] 
    image_encoding=face_recognition.face_encodings(image)[0 ]
    
    #Compare the encodings and calculate similarity scores
    face_distances = face_recognition.face_distance(known_encodings, image_encoding)
    similarity_scores = 1 - face_distances

    # Calculate the average similarity score
    average_similarity = sum(similarity_scores) / len(similarity_scores)

    return average_similarity  

print(verify_face("emilia-clarke",convert_image_to_numpy_array("./person/emilia-clarke/1.jpg")))
print(verify_face("kit-harington",convert_image_to_numpy_array("./person/kit-harington/1.jpg")))
print(verify_face("nikolaj-coster-waldau",convert_image_to_numpy_array("./person/nikolaj-coster-waldau/1.jpg")))
print(verify_face("jacques",convert_image_to_numpy_array("./person/jacques/1.jpg")))


