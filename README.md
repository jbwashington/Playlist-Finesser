# F1n35 Server

## Introduction
Generate playlists from any song ever.

## Quickstart
'python app.py'

## Contents
* app/app.py is the main entry point of the Flask application.
* app/config.py will be storing all the module configuration for different environments (local, staging and prod). You don't want to be messing with production data while developing locally! I'll talk more about how to setup different environment in later posts.
* app/extensions.py contains declaration of all the flask extensions
* app/static/ is the folder from which Flask will serve static files. If you want to use a different folder, see here
* app/common/ consists of common classes and functions that are useful for all the modules. Some examples are global constants, global helper functions.
* app/api/ contains all the controllers for every API endpoints, such as authentication (login/signup).
* app/frontend: as opposed to the API folder, the controllers here are serving non API endpoints. For example, it may define entry point to load the HTML file for your fully dynamic javascript application built in backbone, angular, react, or whatever fancy framework you indulge on.
* app/[module]/ represents a functional area in the application, such as users, posts, chat, and search.
* app/[module]/[moduleModels] : database models (tables) declaration with Flask-SQLAlchemy
* app/[module]/[moduleForms]: WTForm definition in Flask-WTF. Useful for form validation.
* app/[module]/[moduleConstants] and app/[module]/[moduleHelpers] defines the necessary helper functions and constants for this module.


## Installation
run: pip install -r requirements.txt in your shell.
