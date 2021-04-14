import datetime
import sys
from flask import Flask, abort
from flask_restful import Api, Resource, reqparse, inputs, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
db = SQLAlchemy(app)
api = Api(app)
parser = reqparse.RequestParser()
date_parser = reqparse.RequestParser()

# date parser & its args
date_parser.add_argument(
    'start_time',
    type=inputs.date,
    help="The event date with the correct format is required! "
         "The correct format is YYYY-MM-DD!",
    required=True
)
date_parser.add_argument(
    'end_time',
    type=inputs.date,
    help="The event date with the correct format is required! "
         "The correct format is YYYY-MM-DD!",
    required=True
)

parser.add_argument(
    'date',
    type=inputs.date,
    help="The event date with the correct format is required! "
         "The correct format is YYYY-MM-DD!",
    required=True
)
parser.add_argument(
    "event",
    type=str,
    help="The event name is required!",
    required=True
)

resource_fields = {
    'id': fields.Integer,
    'event': fields.String,
    'date': fields.DateTime(dt_format='iso8601')
}


class Events(db.Model):
    __tablename__ = 'Events'
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date, nullable=False)


class TodayEvents(Resource):

    @marshal_with(resource_fields)
    def get(self):
        return Events.query.filter(Events.date == datetime.date.today()).all()


class PostEvent(Resource):

    @marshal_with(resource_fields)
    def get(self):
        try:
            args = date_parser.parse_args()
            return Events.query.filter(Events.date > args['start_time'], Events.date < args['end_time']).all()

        except Exception:
            return Events.query.all()

    def post(self):
        args = parser.parse_args()
        event = Events(date=args['date'], event=args['event'])
        db.session.add(event)
        db.session.commit()
        return {
            'message': 'The event has been added!',
            'event': args['event'],
            'date': str(args['date'].date())
        }

class EventByID(Resource):

    @marshal_with(resource_fields)
    def get(self, event_id):
        event = Events.query.filter(Events.id == event_id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        return event

    def delete(self, event_id):
        event = Events.query.filter(Events.id == event_id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        db.session.delete(event)
        db.session.commit()
        return {
            "message": "The event has been deleted!"
        }


db.create_all()
api.add_resource(TodayEvents, '/event/today')
api.add_resource(PostEvent, '/event')
api.add_resource(EventByID, '/event/<int:event_id>')

# do not change the way you run the program
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
