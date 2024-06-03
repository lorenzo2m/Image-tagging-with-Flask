from . import models
from datetime import datetime
from imagekitio import ImageKit
import requests, os, base64, json, uuid
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_credentials():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    credentials_path = os.path.join(base_dir, 'credentials.json')
    with open(credentials_path, 'r') as file:
        return json.load(file)

def generate_uuid_for_image():
    return str(uuid.uuid4())

def process_image_upload(image_path, tags, image_id):
    date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Genera el ID de la imagen y almacena la información básica de la imagen
    image_id, image_date = models.insert_picture(image_path, image_id, date_now)

    # Añade información de etiquetas a la base de datos
    for tag in tags:
        tag['date'] = image_date  # Asegurar que la fecha de la etiqueta sea la misma que la de la imagen
    models.insert_tags(image_id, tags)

    # Preparar la respuesta
    image_size = os.path.getsize(image_path) / 1024  # size in KB
    image_data = base64.b64encode(open(image_path, 'rb').read()).decode('utf-8')

    return {
        'id': image_id,
        'size': image_size,
        'date': date_now,
        'tags': tags,
        'data': image_data
    }

def upload_image_to_imagekit(image_path, image_id):

    credentials = load_credentials()
    
    imagekit = ImageKit(
        public_key=credentials["ImageKit"]["public_key"],
        private_key=credentials["ImageKit"]["private_key"],
        url_endpoint = credentials["ImageKit"]["url_endpoint"]
    )

    with open(image_path, mode="rb") as img:
        imgstr = base64.b64encode(img.read())

    # upload an image
    upload_info = imagekit.upload(file=imgstr, file_name=image_id)
    # la url es accesible mediante `upload_info.url`
    return upload_info


def get_tags_from_imagga(image_url, min_confidence):

    credentials = load_credentials()

    api_key = credentials["Imagga"]["api_key"]
    api_secret = credentials["Imagga"]["api_secret"]

    response = requests.get(f"https://api.imagga.com/v2/tags?image_url={image_url.url}", auth=(api_key, api_secret))

    tags = [
        {
            "tag": t["tag"]["en"],
            "confidence": t["confidence"]
        }
        for t in response.json()["result"]["tags"]
        if t["confidence"] > min_confidence
    ]
    return tags

def delete_image_from_imagekit(image_url):
    credentials = load_credentials()
    
    imagekit = ImageKit(
        public_key=credentials["ImageKit"]["public_key"],
        private_key=credentials["ImageKit"]["private_key"],
        url_endpoint = credentials["ImageKit"]["url_endpoint"]
    )
    # delete an image
    delete = imagekit.delete_file(file_id=image_url.file_id)



def get_filtered_images(min_date, max_date, tags):
    images = models.fetch_images(min_date, max_date, tags)

    for img in images:
        # Cálculo del size en Kb
        if img["path"]:
            image_path = img['path']
            img['size'] = os.path.getsize(image_path) / 1024  # Convertir tamaño a KB
            # Eliminamo path del resultado
            del(img["path"])
    return images


def get_image_details(image_id):
    image_record = models.fetch_image_by_id(image_id)
    if not image_record:
        return None
    
    logger.info(f"Imge Record in Controller: {image_record}")

    # Asignar el path del archivo de imagen
    image_path = image_record['path']
    size = os.path.getsize(image_path) / 1024  # Convertir tamaño a KB

    # Codificar la imagen en base64
    with open(image_path, 'rb') as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

    return {
        'id': image_record['id'],
        'size': size,
        'date': image_record['date'],
        'tags': [{'tag': tag['tag'], 'confidence': tag['confidence']} for tag in image_record['tags']],
        'data': encoded_image
    }