# ./src

This is the `src` folder which contains all the mission-critical code to run EngineeringServicesApi

## About

### [./db](./db)

This directory contains database specific code such as connection managers and ORM models

### [./middlewares](./middlewares)

This directory contains middleware

### [./routes](./routes)

This directory contains the endpoints and services used in the application

### [./tasks](./tasks)

This is where I've been throwing things that need to run that aren't exactly middlewares

### [./\_\_init__.py](./__init__.py)

This Python file contains a lot of the start-up code for the application

### [./main.py](./main.py)

The main file for the application. Direct all routers to here to add them to the app