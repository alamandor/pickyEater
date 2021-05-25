FROM google/cloud-sdk 

MAINTAINER Alec Greenaway "aag3@pdx.edu" 

COPY . /app 

WORKDIR /app 

RUN apt update -y && apt install -y python3-pip && pip3 install -r requirements.txt

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app
