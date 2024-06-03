from sqlalchemy import create_engine, text
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_engine():
    return create_engine("mysql+pymysql://mbit:mbit@db:3306/Pictures")

def create_tables():
    # Configura aquí la cadena de conexión a tu base de datos MySQL
    # Asegúrate de que los detalles de usuario, contraseña y host sean correctos y seguros.
    engine = get_engine()

    # Comandos SQL para crear las tablas
    sql_commands = [
        """
        CREATE TABLE IF NOT EXISTS pictures (
            id CHAR(36) PRIMARY KEY,
            path VARCHAR(255) NOT NULL,
            date CHAR(36) NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS tags (
            tag VARCHAR(32),
            picture_id CHAR(36),
            confidence INT,
            date CHAR(36) NOT NULL,
            PRIMARY KEY (tag, picture_id),
            FOREIGN KEY (picture_id) REFERENCES pictures(id) ON DELETE CASCADE
        );
        """
    ]

    with engine.connect() as conn:
        for command in sql_commands:
            conn.execute(text(command))


def insert_picture(path, image_id, date_now):
    engine = get_engine()
    try:
        print(image_id, path, date_now)
        print(type(image_id), type(path), type(date_now))
        with engine.connect() as conn:
            query = text("INSERT INTO pictures (id, path, date) VALUES (:id, :path, :date)")
            conn.execute(query, {'id': image_id, 'path': path, 'date': date_now})
            conn.commit()
        return image_id, date_now
    except Exception as e:
        print(f"Error occurred: {e}")
        raise





def insert_tags(image_id, tags):
    engine = get_engine()
    with engine.connect() as conn:
        for tag in tags:
            conn.execute(text("""INSERT INTO tags (tag, picture_id, confidence, date)
                VALUES (:tag, :picture_id, :confidence, :date)
            """), {'tag': tag['tag'], 'picture_id': image_id, 'confidence': tag['confidence'], 'date': tag['date']})
            conn.commit()


def fetch_images(min_date, max_date, tags_string):
    engine = get_engine()
    # Iniciar la consulta SQL base
    sql_query = """
        SELECT p.id, p.path, p.date, 
               t.tag, t.confidence
        FROM pictures p
        LEFT JOIN tags t ON p.id = t.picture_id
        WHERE 1=1
    """

    # Filtros de fecha
    if min_date:
        min_date = datetime.strptime(min_date, "%Y-%m-%d %H:%M:%S")
        sql_query += " AND p.date >= :min_date"
    if max_date:
        max_date = datetime.strptime(max_date, "%Y-%m-%d %H:%M:%S")
        sql_query += " AND p.date <= :max_date"

    # Filtro de tags, si se especifica
    if tags_string!="":
        tags = tags_string.split(',')
        tags_filters = " AND " + " AND ".join(f"EXISTS (SELECT 1 FROM tags t WHERE t.picture_id = p.id AND t.tag = '{tag}')" for tag in tags)
        sql_query += tags_filters

    # Ejecutar la consulta
    with engine.connect() as connection:
        result = connection.execute(text(sql_query), {'min_date': min_date, 'max_date': max_date}).fetchall()
        connection.commit()

    logger.info(f"List Images Result {result}")

  
    # Transformar los resultados en un formato adecuado
    images = []
    last_id = None
    image_data = None

    for row in result:
        if last_id != row[0]:
            if image_data:
                images.append(image_data)
            image_data = {
                'id': row[0],
                'path':row[1],
                'size': 0,  
                'date': row[2],
                'tags': []
            }
            last_id = row[0]
        if row[3]:
            image_data["tags"].append({'tag': row[3], 'confidence': row[4]})

    if image_data:
        images.append(image_data)

    logger.info(f"Return from Models to Controlller: {images}")

    return images



def fetch_image_by_id(image_id):
    engine = get_engine()
    logger.info(f"Fetching image by ID: {image_id}")
    with engine.connect() as connection:
        image_result = connection.execute(text("""
            SELECT id, path, date FROM pictures WHERE id = :id
        """), {'id': image_id}).fetchone()
        
        logger.info(f"Image result for ID {image_id}: {image_result}")

        if not image_result:
            return None

        tags_result = connection.execute(text("""
            SELECT tag, confidence FROM tags WHERE picture_id = :id
        """), {'id': image_id}).fetchall()
        
        logger.info(f"Tags associated with image ID {image_id}: {tags_result}")

        return {
            'id': image_result[0],
            'path': image_result[1],
            'date': image_result[2],
            'tags': [{'tag': row[0], 'confidence': row[1]} for row in tags_result]
        }