# ABC Book Web Services

Web services for the management of ABC Book Club, as part of an assessment for GovTech's MOL-VICA TAP Application 2022.

This project is entirely written in Python. REST APIs have been built with Flask, with integrations from Flask-RestX and PyMongo.

## Installation Of Requirements

Install with pip:

```
$ pip install -r requirements.txt
```

## Flask Application Structure 
    .
    ├── backend/                # Contains all codes relating to the backend
        ├── endpoints/          # Contains all the code relating to endpoints
        ├── common/             # Contains config and mongodb management codes
        ├── bootstrap/          # Contains json files to bootstrap a mongodb instance
        ├── app.py              # The main python program to run the entire backend
    └── README.md

## Run Flask Application

```
$ python backend/app.py
```
Default port is set to `5010`

Swagger document page for all endpoints:  `http://0.0.0.0:5010/docs`

## API Design/Implementation/Scalability
- The services are grouped based on their use cases ie. 1) Book Management, 2) User Management, 3) Borrowing/Returning of Books.
- Each service is stored as a _flask_restx.namespace_ object. The _namespace_ objects are built in the `backend/endpoints` folder. `backend/endpoints/__init.py__` will initialize them into a _flask.restx.Api_ object. The _flask.restx.Api_ object will then be used to initialized with the main Flask object. Hence allowing all endpoints to be initilized when _backend/app.py_ is runned. This allows for scalability so that new services can be developed easily by creating another _namespace_ without interfering with the other services.
- JWT Authentication Tokens are also used to authenticate users to ensure authorized access to the services. The User Authentication feature is works by first letting the user request a Bearer token based on the user's username and password (salt+hashed in database). Depending on his/her role, a Bearer token will be returned to the user that allows the user to use the protected endpoints. Hence, unauthorized users will not be able to use the protected services. Eg. Member isn't able to call endpoints to delete/add/change another user's details in the database.
- The APIs/JWT Authentication can be tested in the Swagger document page: `http://0.0.0.0:5010/docs`
- Commonly used variables are stored in the such as config variables and mongodb management variables will be stored in `backend/common` folder. This allows for a central location of initializng these variables, so that minimal changes will be required if they have to be changed in the future.
