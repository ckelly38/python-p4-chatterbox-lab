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

@app.route('/messages', methods=["GET", "POST"])
def messages():
    if (request.method == "GET"):
        msgs = Message.query.all();
        jmsgs = [msg.to_dict() for msg in msgs];
        return make_response(jmsgs, 200);
    elif (request.method == "POST"):
        msg = Message();
        
        #https://stackoverflow.com/questions/10999990/get-raw-post-body-in-python-flask-regardless-of-content-type-header
        #print(request.form);
        #print(request.get_data());
        #print(request.json);
        if (0 < len(request.form)):
            for attr in request.form:
                #print(f"attr = {attr}");
                #print(f"value = {request.form.get(attr)}");
                setattr(msg, attr, request.form.get(attr));
        else:
            mjson = request.json;
            #print(mjson);
            msg.body = mjson["body"];
            msg.username = mjson["username"];
        
        db.session.add(msg);
        db.session.commit();

        return make_response(msg.to_dict(), 201);
    else: return make_response("INVALID METHOD!", 500);

@app.route('/messages/<int:id>', methods=["GET", "PATCH", "DELETE"])
def messages_by_id(id):
    msg = Message.query.filter_by(id=id).first();
    if (msg == None):
        return make_response({"msg": f"Error message with id {id} not found!"}, 404);
    if (request.method == "GET"):
        return make_response(msg.to_dict(), 200);
    elif (request.method == "PATCH"):
        if (0 < len(request.form)):
            for attr in request.form:
                setattr(msg, attr, request.form.get(attr));
        else:
            mjson = request.json;
            print(mjson);
            #msg.body = mjson["body"];
            #msg.username = mjson["username"];
            for attr in mjson:
                setattr(msg, attr, mjson[attr]);
        
        db.session.add(msg);
        db.session.commit();

        return make_response(msg.to_dict(), 200);
    elif (request.method == "DELETE"):
        db.session.delete(msg);#cannot use this msg.delete();
        db.session.commit();

        return make_response({"Status": "Success", "msg": "Message deleted successfully!"}, 200);
    else: return make_response("INVALID METHOD!", 500);

if __name__ == '__main__':
    app.run(port=5555)
