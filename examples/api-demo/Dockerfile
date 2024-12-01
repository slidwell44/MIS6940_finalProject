FROM winexusreposrv.williams-int.com:8083/python:3.12

WORKDIR /code

COPY ./certs/nexus.pem /usr/local/share/ca-certificates/nexus.pem

RUN update-ca-certificates

COPY ./pip.conf /etc/pip.conf

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./src /code/src

CMD ["python", "-m", "src.main"]