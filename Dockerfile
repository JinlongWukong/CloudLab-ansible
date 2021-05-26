# pull official base image
FROM python:3.9.5-slim-buster

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

RUN set -eux; \
	apt-get update; \
	apt-get install -y --no-install-recommends \
		sshpass \
		openssh-client \
	; \
	rm -rf /var/lib/apt/lists/*

# copy project
COPY . /app

EXPOSE 9134
# run entrypoint.sh
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:9134", "ansible_api:app"]
