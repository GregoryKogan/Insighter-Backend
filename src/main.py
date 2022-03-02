from flask import Flask
from flask_restful import Api, Resource

from apps.Ping.views import PingView


app = Flask(__name__)
api = Api(app)

api.add_resource(PingView, "/ping")


if __name__ == "__main__":
    app.run(debug=True)
