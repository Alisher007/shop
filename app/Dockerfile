# pull official base image
FROM python:3.13.4-slim-bookworm

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# install system dependencies
RUN apt-get update && apt-get install -y \
    ### C extensions
    gcc \
    build-essential \
    python3-dev \
    ### Pillow
    libjpeg-dev \
    zlib1g-dev \
    ### WeasyPrint 
    libcairo2 \
    libglib2.0-0 \
    libpangoft2-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libpango-1.0-0 \
    ### cryptographic 
    libffi-dev \
    libssl-dev \ 
    libxml2-dev \
    libxslt1-dev \
    # libxml2 \
    # libxslt1.1 \
    ### For wait-for-it.sh
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# install dependencies
RUN pip install --upgrade pip setuptools wheel
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

# copy project
COPY . .

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
