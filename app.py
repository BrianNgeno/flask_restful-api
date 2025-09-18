from flask import Flask, request, make_response, jsonify,json,session
from flask_migrate import Migrate
from models import db, Trainer,User
from flask_restful import Resource,Api
from werkzeug.exceptions import HTTPException
from flask_bcrypt import Bcrypt

# add the sqlalchemy database configurtion to our app
# initialize our sqlalchemy instance with our app
# initialize our migrate instance with both our app and our DB
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gym.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False
app.secret_key = 'qwerty'
db.init_app(app)
migrate = Migrate(app, db,render_as_batch=True)
api=Api(app)
bcrypt = Bcrypt(app)


@app.before_request
def check_authorized():
    if 'user_id' not in session\
        and request.endpoint not in ("login","signup"):
        return {"error":"401:unauthorised"}

class Welcome(Resource):
    def get(self):
        
        resp_body={
            "message":"<h1>Flask App Running Smoothly.....</h1>"
        }
        
     
        response = make_response(
            resp_body,
            200
        )
        return response




class Login(Resource):
    def post(self):
        data = request.get_json()

        username = data.get("username")
        password = data.get("password")

        # Find user
        user = User.query.filter_by(username=username).first()

        if user and user.authenticate(password):
            session["user_id"] = user.id
            return user.to_dict(), 200

        return {"error": "username or password is incorrect"}, 401

class Register(Resource):
    def post(self):
        user_data = request.json
        # print(trainer_data)
        # Add this new resource to your database, and ensure it’s saved. i.e create an instance of the trainer class, add it to the session and commit the session
        new_user = User(username=user_data['username'], password_hash=user_data['password'])
        db.session.add(new_user)
        db.session.commit()
        resp = make_response({'success':'user Created'}, 201)
        return resp

api.add_resource(Register,'/signup',endpoint='signup')


class CheckSession(Resource):
    def get(self):
        user= User.query.filter(User.id==session.get("user_id")).first()
        if user:
            return  user.to_dict()
        else:
            return {"message":"401:unauthorised access"},401

class Logout(Resource):
    def delete(self):
        session['user_id']=None
        return {"message":"logout success"}

api.add_resource(Logout,'/logout', endpoint="logout")
api.add_resource(CheckSession,'/check',endpoint="check")
api.add_resource(Login,'/login',endpoint="login")

class Trainers(Resource):
    def get(self):
        trainers = [trainer.to_dict() for trainer in Trainer.query.all()]
        response = make_response(
            trainers,
            200
        )

        return response
            
    def post(self):
        # access trainer data that was sent from client through request
        trainer_data = request.json
        # print(trainer_data)
        # Add this new resource to your database, and ensure it’s saved. i.e create an instance of the trainer class, add it to the session and commit the session
        new_trainer = Trainer(name=trainer_data['name'], bio=trainer_data['bio'], specialization = trainer_data['specialization'], phone_number=trainer_data['phone_number'])
        db.session.add(new_trainer)
        db.session.commit()
        resp = make_response({'success':'Trainer Created'}, 201)
        return resp



class TrainerById(Resource):
    def get(self,id):
        trainer = db.session.query(Trainer).get(trainer_id)
        resp = make_response(trainer.to_dict(), 200)
        return resp

    def patch(self,id):
        trainer = db.session.query(Trainer).get(trainer_id)
        for attr in request.json:
            setattr(trainer,attr,request.json.get(attr))

        db.session.add(trainer)
        db.session.commit()

        resp_dict = trainer.to_dict()
        response = make_response(
            resp_dict,
            201
        )
        return response

    def delete(self,id):
        trainer = db.session.query(Trainer).get(id)
        db.session.delete(trainer)
        db.session.commit()

        resp_body = {"message":"trainer deleted successfully" }

        response = make_response(
            resp_body,
            200
        )
        return response

@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response

api.add_resource(Welcome, '/')
api.add_resource(Trainers,'/trainers')
api.add_resource(TrainerById,"/get_trainer_by_id/<int:id>")

