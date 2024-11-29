# Running Out of a Docker Container
I'll explain the `./Dockerfile` line by line, so you know what to do:

```dockerfile
FROM winexusreposrv.williams-int.com:8083/python:3.12
```

This pulls Python 3.12 from the Nexus Repository

```dockerfile
WORKDIR /code
```

Create a working directory called `code` inside of the container

```dockerfile
COPY ./certs/nexus.pem /usr/local/share/ca-certificates/nexus.pem
```

This is important, make sure you have the `./certs/nexus.pem` file in your directory. You need the certificate to handle the SSL with the Nexus Server 

```dockerfile
RUN update-ca-certificates
```

This is the command for adding a certificate to linux's trusted authorities

```dockerfile
COPY ./pip.conf /etc/pip.conf
```

This is important, you need to create a `pip.conf` file in your root directory `./` that has the following format:

```text
[global]
index-url = https://[insert nexus user token]:[insert nexus pass token]@winexusreposrv.williams-int.com/repository/pypi-group/simple
trusted-host = winexusreposrv.williams-int.com
```

```dockerfile
COPY ./requirements.txt /code/requirements.txt
```

This copies the `requirements.txt` from the project into the container

```dockerfile
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
```

This installs the requirements into the container that were in the `requirements.txt`

```dockerfile
COPY ./src /code/src
```

This copies all of your code from `./src` into the container

```dockerfile
CMD ["fastapi", "run", "src/main.py", "--port", "8000"]
```

This is how you run a FastAPI production deployment using Uvicorn out of the box