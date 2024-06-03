FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copiar solo el archivo de requerimientos primero
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Make port 80 available to the world outside this container
EXPOSE 80

ENV PYTHONPATH "${PYTHONPATH}:/app"

# Command to run the application
CMD ["waitress-serve", "--host=0.0.0.0", "--port=80", "--call", "image_tags_app:create_app"]
