FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app

# Update pip and setuptools
RUN pip3 install --upgrade pip setuptools

# Install the OpenGL libraries needed by OpenCV
RUN apt-get update && apt-get install -y libgl1-mesa-glx

# Install the Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of your application into the container
COPY . /app

EXPOSE 1234

# Set the default command to execute when the container starts
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=1234"]