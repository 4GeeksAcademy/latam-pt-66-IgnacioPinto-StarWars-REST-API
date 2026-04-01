"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

#Endpoint para obtener todos los planetas
@app.route('/planets', methods=['GET'])
def get_all_planets():
    #consultamos todos los planetas en la base de datos
    planets = Planet.query.all()

    planets_serialized = [planet.serialize() for planet in planets]

    return jsonify(planets_serialized), 200

#Endpoint para obtener todos los personsajes
@app.route('/people', methods=['GET'])
def get_all_people():
    #consultamos todos los people en la base de datos
    people = People.query.all()

    people_serialized = [character.serialize() for character in people]

    return jsonify(people_serialized), 200

#Endpoint para obtener un SOLO planeta
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_single_planet(planet_id):
    #se busca el planeta en la base de datos usando el ID
    planet = Planet.query.get(planet_id)

    #manejo de errores
    if planet is None:
        return jsonify({"Error": "El planeta no existe"}), 404

    return jsonify(planet.serialize()), 200

#Endpoint para obtener un SOLO personaje o character
@app.route('/people/<int:people_id>', methods=['GET'])
def get_single_people(people_id):
    #se busca el planeta en la base de datos usando el ID
    people = People.query.get(people_id)

    #manejo de errores
    if people is None:
        return jsonify({"Error": "El personaje no existe"}), 404

    return jsonify(people.serialize()), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
