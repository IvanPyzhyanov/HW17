# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")

class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    director = fields.Str()
    genre = fields.Str()

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)

@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        req = Movie.query
        if director_id is not None:
            req = req.filter(Movie.director_id == director_id)
        if genre_id is not None:
            req = req.filter(Movie.genre_id == genre_id)
        if director_id is not None and genre_id is not None:
            req = req.filter(Movie.director_id == director_id, Movie.genre_id == genre_id)
        res = req.all()
        return movies_schema.dump(res), 200

    def post(self):
        req = request.json
        new_movie = Movie(**req)
        with db.session.begin():
            db.session.add(new_movie)
        return "", 201


@movie_ns.route('/<id>')
class MovieView(Resource):
    def get(self, id):
        req = Movie.query.get(id)
        return movie_schema.dump(req), 200

    def delete(self, id):
        req = Movie.query.get(id)
        db.session.delete(req)
        db.session.commit()
        return "", 204


@genre_ns.route('/<id>')
class GenreView(Resource):
    def get(self, id):
        req = Genre.query.get(id)
        return genre_schema.dump(req), 200

    def delete(self, id):
        req = Genre.query.get(id)
        db.session.delete(req)
        db.session.commit()
        return "", 204

    def put(self, id):
        req = Genre.query.get(id)
        req_put = request.json
        req.name = req_put.get("name")
        db.session.add(req)
        db.session.commit()
        return "", 204


@director_ns.route('/<id>')
class DirectorView(Resource):
    def get(self, id):
        req = Director.query.get(id)
        return director_schema.dump(req), 200

    def delete(self, id):
        req = Director.query.get(id)
        db.session.delete(req)
        db.session.commit()
        return "", 204

    def put(self, id):
        req = Director.query.get(id)
        req_put = request.json
        req.name = req_put.get("name")
        db.session.add(req)
        db.session.commit()
        return "", 204


if __name__ == '__main__':
    app.run(debug=True)
