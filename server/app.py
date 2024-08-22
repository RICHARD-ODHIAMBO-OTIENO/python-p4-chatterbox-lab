from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        # Retrieve all messages ordered by 'created_at'
        messages = Message.query.order_by('created_at').all()

        # Create a response object
        response = make_response(
            jsonify([message.to_dict() for message in messages]),
            200
        )
    elif request.method == 'POST':
        # Get the data from the request
        data = request.get_json()

        # Create a new Message object
        message = Message(
            body=data['body'],
            username=data['username']
        )

        # Add and commit the new message to the database
        db.session.add(message)
        db.session.commit()

        # Create a response object
        response = make_response(
            jsonify(message.to_dict()),
            201  # Status code 201 indicates resource creation
        )

    return response

@app.route('/messages/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def messages_by_id(id):
    # Retrieve a specific message by ID
    message = Message.query.filter_by(id=id).first()

    if not message:
        return make_response(jsonify({"error": "Message not found"}), 404)

    if request.method == 'GET':
        # Create a response for the GET request
        response = make_response(
            jsonify(message.to_dict()),
            200
        )
    elif request.method == 'PATCH':
        # Update the message with the provided data
        data = request.get_json()
        for attr in data:
            setattr(message, attr, data[attr])

        db.session.add(message)
        db.session.commit()

        response = make_response(
            jsonify(message.to_dict()),
            200
        )
    elif request.method == 'DELETE':
        # Delete the message
        db.session.delete(message)
        db.session.commit()

        response = make_response(
            jsonify({'delete': True}),
            200
        )

    return response

if __name__ == '__main__':
    app.run(port=5555)
