from flask_restful import Resource


class PingView(Resource):
    def get(self):
        return {"message": "pong"}
