from flask import request, jsonify, Blueprint
import base64
from . import controller


bp = Blueprint('image_api', __name__, url_prefix='/')

@bp.route('/image', methods=['POST'])
def post_image():
    # Obtener el JSON del body y el query parameter
    image_data = request.json.get('data')
    min_confidence = request.args.get('min_confidence', 80)

    try:
        # Decodificar la imagen de Base64
        image_bytes = base64.b64decode(image_data)
        image_id = controller.generate_uuid_for_image()
        image_path = f'./images/{image_id}.jpg'

        # Guardar la imagen localmente para procesamiento posterior
        with open(image_path, 'wb') as img_file:
            img_file.write(image_bytes)

        # Subir la imagen a ImageKit y obtener la URL pública
        image_url = controller.upload_image_to_imagekit(image_path,image_id)

        # Obtener tags de Imagga usando la URL de la imagen
        tags = controller.get_tags_from_imagga(image_url, min_confidence)

        # Eliminar la imagen de ImageKit
        controller.delete_image_from_imagekit(image_url)

        # Almacenar información en la base de datos y en sistema local
        image_info = controller.process_image_upload(image_path, tags, image_id)

        return jsonify(image_info), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@bp.route('/listimages', methods=['GET'])
def listimages():
    min_date = request.args.get('min_date')
    max_date = request.args.get('max_date')
    tags = request.args.get('tags')

    try:
        images = controller.get_filtered_images(min_date, max_date, tags)
        return jsonify(images), 200
    except Exception as e:
        return jsonify({'error listimages': str(e)}), 500
    

@bp.route('/image/<image_id>', methods=['GET'])
def image(image_id):
    try:
        image_data = controller.get_image_details(image_id)
        if image_data:
            return jsonify(image_data), 200
        else:
            return jsonify({"error": "Image not found"}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

