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
from models import db, User, Planet, People, Favorite
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

#Endpoint para obtener todos los usuarios
@app.route('/users', methods=['GET'])
def get_all_users():
    #consultamos todos los people en la base de datos
    users = User.query.all()

    user_serialized = [user.serialize() for user in users]

    return jsonify(user_serialized), 200


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
    #se busca el personaje en la base de datos usando el ID
    people = People.query.get(people_id)

    #manejo de errores
    if people is None:
        return jsonify({"Error": "El personaje no existe"}), 404

    return jsonify(people.serialize()), 200

#Endpoint para obtener un SOLO usuario
@app.route('/users/<int:user_id>', methods=['GET'])
def get_single_user(user_id):
    #se busca el personaje en la base de datos usando el ID
    user = User.query.get(user_id)

    #manejo de errores
    if user is None:
        return jsonify({"Error": "El usuario no existe"}), 404

    return jsonify(user.serialize()), 200


#End point para agregar favorito planeta
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    current_user_id = 1

    # Verificar que el planeta realmente exista
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"Error": "El planeta que intentas guardar no existe"}), 404

    #verificar si ya esta en la lista de favoritos
    existing_favorite = Favorite.query.filter_by(user_id=current_user_id, planet_id=planet_id).first()
    if existing_favorite:
        return jsonify({"msg": f"El planeta: {planet.name} ya esta en tus favoritos"}), 400

    # crear el nuevo registro
    new_favorite = Favorite(user_id=current_user_id, planet_id=planet_id)

    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({"msg": f"El Planeta {planet.name} agregado a favoritos con exito"}), 201 # 201 significa creado

#End point para agregar favorito personaje
@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    current_user_id = 1

    # Verificar que el planeta realmente exista
    people = People.query.get(people_id)
    if people is None:
        return jsonify({"Error": "El personaje que intentas guardar no existe"}), 404

    #verificar si ya esta en la lista de favoritos
    existing_favorite = Favorite.query.filter_by(user_id=current_user_id, people_id=people_id).first()
    if existing_favorite:
        return jsonify({"msg": f"Este personaje: {people.name} ya esta en tus favoritos"}), 400

    # crear el nuevo registro
    new_favorite = Favorite(user_id=current_user_id, people_id=people_id)

    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({"msg": "Personaje agregado a favoritos con exito"}), 201 # 201 significa creado


####### ENDPOINTS PARA DELETE #######
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    current_user_id = 1
    
    #Buscamos el favorito especifico de este usuario y este planeta
    favorite_to_delete = Favorite.query.filter_by(user_id=current_user_id, planet_id=planet_id).first()

    #Si registro no existe no se puede borrar (manejo de errores)
    if favorite_to_delete is None:
        return jsonify({"Error": "El planeta no esta en tus favoritos"}), 404
    
    #Si existe lo eliminamos de la zona de espera
    db.session.delete(favorite_to_delete)

    # guardamos los cambios
    db.session.commit()

    return jsonify({"message": f"El planeta con ID {planet_id} fue eliminado de favoritos con exito"}), 200



####### ENDPOINTS PARA DELETE los personajes #######

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    current_user_id = 1
    
    #Buscamos el favorito especifico de este usuario y este planeta
    favorite_to_delete = Favorite.query.filter_by(user_id=current_user_id, people_id=people_id).first()

    #Si registro no existe no se puede borrar (manejo de errores)
    if favorite_to_delete is None:
        return jsonify({"Error": "El personaje no esta en tus favoritos"}), 404
    
    #Si existe lo eliminamos de la zona de espera
    db.session.delete(favorite_to_delete)

    # guardamos los cambios
    db.session.commit()

    return jsonify({"message": f"El personaje con ID {people_id} eliminado de favoritos con exito"}), 200

# Endpoint para obtener todo los favoritos
@app.route('/users/favorites', methods=['GET'])
def get_all_favorites():
    current_user_id = 1

    get_favorites = Favorite.query.filter_by(user_id=current_user_id).all()

    user_favorites = [favorite.serialize() for favorite in get_favorites]

    return jsonify(user_favorites), 200

# Endpoint para agregar planetas
@app.route('/planets', methods=['POST'])
def create_planet():
    # recibir los datos que vienen el body al hacer el POST con postman
    body = request.get_json()

    # 2 validar que el usuario si haya enviado el nombre del planeta y q no este vacio
    if "name" not in body:
        return jsonify({"Error": "El campo 'name' es obligatorio"}), 400

    # 3 creacion del nuevo planeta con los datos recibidos
    new_planet = Planet(
        name=body["name"],
        climate=body.get("climate", "Desconocido"),
        population=body.get("population", "Desconocido")
    )

    # guardar en la base de datos
    db.session.add(new_planet)
    db.session.commit()

    return jsonify({"msg": f"Planeta: {new_planet.name} creado exitosamente", "planet": new_planet.serialize()}), 201  

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
