import os
from PIL import Image
from pyzbar.pyzbar import decode



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