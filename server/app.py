#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

# ----------------------------
# Resource: Login
# ----------------------------
class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get("username")

        user = User.query.filter_by(username=username).first()

        if not user:
            return {"error": "Unauthorized"}, 401

        session["user_id"] = user.id

        return user.to_dict(), 200

# ----------------------------
# Resource: Clear Session
# ----------------------------
class ClearSession(Resource):
    def delete(self):
        session['page_views'] = None
        session['user_id'] = None
        return {}, 204

# ----------------------------
# Resource: Index Article
# ----------------------------
class IndexArticle(Resource):
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

# ----------------------------
# Resource: Show Article
# ----------------------------
class ShowArticle(Resource):
    def get(self, id):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:
            article = Article.query.filter(Article.id == id).first()
            article_json = jsonify(article.to_dict())
            return make_response(article_json, 200)

        return {'message': 'Maximum pageview limit reached'}, 401

# ----------------------------
# Register routes
# ----------------------------
api.add_resource(Login, '/login')
api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')

# ----------------------------
# Run app
# ----------------------------
if __name__ == '__main__':
    app.run(port=5555, debug=True)
