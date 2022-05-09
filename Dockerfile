# pull official base image
FROM debian:bullseye

#### Prepare the OS base setup ###
RUN echo 'deb-src http://deb.debian.org/debian bullseye main' >> /etc/apt/sources.list.d/srcpkg.list && \
    echo 'deb-src http://security.debian.org/debian-security bullseye-security main' >> /etc/apt/sources.list.d/srcpkg.list
RUN apt-get update && \
    apt-get -y --no-install-recommends install sudo python3-dev python3-pip

# set work directory
WORKDIR /home/root/project

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

EXPOSE 8000

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]