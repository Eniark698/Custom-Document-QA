FROM nvidia/cuda:12.4.0-devel-ubuntu22.04
# FROM pytorch/pytorch:2.3.1-cuda12.1-cudnn8-devel
ENV DEBIAN_FRONTEND noninteractive



# Install Tesseract OCR, the Ukrainian language pack, and additional tools
RUN apt-get update && apt-get install -y \
    git \
    nano \
    ntfs-3g \
    cifs-utils \
    nfs-common \
    pkg-config \
    build-essential \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libssl-dev \
    libreadline-dev \
    libffi-dev \
    libsqlite3-dev \
    wget \
    libbz2-dev \
    software-properties-common \ 
    pip \
    && apt-get clean && rm -rf /var/lib/{apt,dpkg,cache,log}/

RUN wget https://www.python.org/ftp/python/3.12.4/Python-3.12.4.tgz && tar -xf Python-3.12.4.tgz
WORKDIR /Python-3.12.4/
RUN ./configure --enable-optimizations && make -j 20 && make altinstall

# Set the working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/requirements.txt

RUN python3.12 -m pip install wheel packaging ninja 
RUN python3.12 -m pip install -r /app/requirements.txt

# Copy the scripts for running Tesseract OCR and processing the image
COPY . .
RUN MKDIR /app/shared/

# Define the entry point for the container
#ENTRYPOINT ["./startup.sh"]
# CMD ["/bin/sh", "-c", "python main.py"]
CMD ["/bin/sh", "-c", "sleep infinity"]