# EngineeringServicesApi

Welcome to the Engineering Services API, right now this is built on the FastAPI Python Web Framework

Python Version: 3.12

FastAPI Version: 0.104.1

## About

### [./alembic](./alembic)

This directory manages schema migrations using alembic and the `--autogenerate` command that leverages the SQLAlchemy
ORM

### [./certs](./certs)

Put any certificates needed for authentication in this directory

### [./docs](./docs)

This directory contains markdown files for extended documentation on important subject matters

### [./src](./src)

This directory manages the app

### [./tests](./tests)

This directory contains automated testing leveraging the pytest module

### [./debug.log](./debug.log)

I was getting an error like:

```text
AttributeError: '_WindowsSelectorEventLoop' object has no attribute '_ssock'
INFO:     Stopping reloader process [8304]
```

And from what I can tell the `logger.setLevel(logging.DEBUG)` throws like a billion messages a second which was causing
the maximum recursion depth to be exceeded which indicates that there are conflicts with how the event loop and logging
are being handled. I believe it's because I overwrote the emit functionality to be async and there's too much traffic
writing to the db or something. So now I just filter `root - DEBUG` into this file

## Links to Important Things

* [Running EngineeringServicesApi out of a Docker Container](./docs/Running%20out%20of%20a%20Docker%20Container.md)