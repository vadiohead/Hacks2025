# Use Python 3.7 as the base image
FROM python:3.7

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libboost-all-dev \
    cmake \
    libopencv-dev \
    && rm -rf /var/lib/apt/lists/*


# Install Python dependencies
RUN pip install --no-cache-dir cmake dlib
RUN pip install --no-cache-dir flask opencv-python face_recognition


# Copy the application files into the container
COPY . /app

# Define the command to run the application
CMD ["python", "app.py"]
