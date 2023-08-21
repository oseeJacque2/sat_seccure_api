
import os

def delete_face(name):
    """Deletes the images of a person from the collection.

    Args:
        name (str): Name of the person.

    Returns:
        bool: True if the images are successfully deleted, False otherwise.
    """
    # Get the directory path for the person's images
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Verify if the user exist
    if name not in os.listdir(os.path.join(BASE_DIR, "user_images")):
        print("This user is not in the database")
        return 0.0
    directory = os.path.join(os.path.join(BASE_DIR, "user_images"), name)

    # Check if the directory exists
    if not os.path.exists(directory):
        print("Person not found.")
        return False

    # Get the list of image filenames for the person
    image_filenames = [filename for filename in os.listdir(directory) if filename.endswith((".jpg", ".png"))]

    # Check if there are images for the person
    if len(image_filenames) == 0:
        print("No images found for the person.")
        return False

    # Display the list of images for the person
    print("Images for", name)
    for i, filename in enumerate(image_filenames):
        print(f"{i+1}. {filename}")

    # Ask the user to select the images to delete
    selections = input("Enter the numbers of the images to delete (separated by comma): ").strip().split(",")
    selections = [int(selection.strip()) for selection in selections if selection.strip().isdigit()]

    # Delete the selected images
    deleted_count = 0
    for selection in selections:
        if 1 <= selection <= len(image_filenames):
            filename = image_filenames[selection-1]
            filepath = os.path.join(directory, filename)
            os.remove(filepath)
            deleted_count += 1

    print(f"{deleted_count} image(s) deleted.")
    return True
delete_face("jacques")