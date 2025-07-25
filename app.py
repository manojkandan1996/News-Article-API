from flask import Flask, request
from flask_restful import Resource, Api
from werkzeug.exceptions import BadRequest, NotFound
from datetime import datetime

app = Flask(__name__)
api = Api(app)

articles = []
article_id_counter = 1

def validate_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

class ArticleListResource(Resource):
    def get(self):
        category = request.args.get('category')
        date = request.args.get('date')

        filtered = articles
        if category:
            filtered = [a for a in filtered if a['category'].lower() == category.lower()]
        if date:
            filtered = [a for a in filtered if a['published_date'] == date]

        return {'articles': filtered}, 200

    def post(self):
        global article_id_counter
        data = request.get_json()

        if not data or 'headline' not in data or 'category' not in data or 'published_date' not in data:
            raise BadRequest("Fields 'headline', 'category', and 'published_date' are required.")

        if not validate_date(data['published_date']):
            raise BadRequest("Published date must be in YYYY-MM-DD format.")

        new_article = {
            'id': article_id_counter,
            'headline': data['headline'],
            'category': data['category'],
            'published_date': data['published_date']
        }
        articles.append(new_article)
        article_id_counter += 1
        return new_article, 201

class ArticleResource(Resource):
    def get(self, id):
        article = next((a for a in articles if a['id'] == id), None)
        if not article:
            raise NotFound("Article not found.")
        return article, 200

    def put(self, id):
        data = request.get_json()
        article = next((a for a in articles if a['id'] == id), None)
        if not article:
            raise NotFound("Article not found.")

        if 'headline' in data:
            article['headline'] = data['headline']
        if 'category' in data:
            article['category'] = data['category']
        if 'published_date' in data:
            if not validate_date(data['published_date']):
                raise BadRequest("Published date must be in YYYY-MM-DD format.")
            article['published_date'] = data['published_date']

        return article, 200

    def delete(self, id):
        global articles
        article = next((a for a in articles if a['id'] == id), None)
        if not article:
            raise NotFound("Article not found.")
        articles = [a for a in articles if a['id'] != id]
        return {'message': f'Article with id {id} deleted.'}, 200

# Register routes
api.add_resource(ArticleListResource, '/articles')
api.add_resource(ArticleResource, '/articles/<int:id>')

if __name__ == '__main__':
    app.run(debug=True)
