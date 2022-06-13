from flask import jsonify
from flask_jwt_extended import (
    current_user,
    jwt_required,
)
from app import app, db
from apps.GeoObjects.Scraping.scraper import scrape
from apps.GeoObjects.models import GeoObject
import json
from sqlalchemy import func
import datetime


@app.route("/geoObjects/syncOSM", methods=["POST"])
@jwt_required()
def sync_OSM():
    if current_user.rank != "Admin":
        return jsonify({"msg": "Not allowed"}), 403

    try:
        new_objects, errors = scrape()
        return (
            jsonify(
                {
                    "errors": errors,
                    "total": len(new_objects),
                    "new_objects": [new_object.serialize for new_object in new_objects],
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/geoObjects/lastSync", methods=["POST"])
@jwt_required()
def last_sync():
    if current_user.rank != "Admin":
        return jsonify({"msg": "Not allowed"}), 403

    last_sync_timestamp = db.session.query(func.max(GeoObject.updated_at)).scalar()
    if last_sync_timestamp is None:
        return jsonify({"msg": "There aren't any GeoObjects"})

    time_delta = datetime.datetime.now(datetime.timezone.utc) - last_sync_timestamp
    return jsonify(
        {
            "LastSync": last_sync_timestamp.isoformat(),
            "DaysSinceLastSync": time_delta.days,
            "SecondsSinceLastSync": time_delta.seconds,
        }
    )


@app.route("/geoObjects/fetchAll", methods=["POST"])
@jwt_required()
def fetch_all_objects():
    if current_user.rank != "Admin":
        return jsonify({"msg": "Not allowed"}), 403

    geo_objects = GeoObject.query.all()
    serialized_objects = [geo_object.serialize for geo_object in geo_objects]
    return (
        jsonify(
            {
                "total": len(serialized_objects),
                "GeoObjects": serialized_objects,
            }
        ),
        200,
    )


@app.route("/geoObjects/dumpToFile", methods=["POST"])
@jwt_required()
def dump_to_file():
    if current_user.rank != "Admin":
        return jsonify({"msg": "Not allowed"}), 403

    geo_objects = GeoObject.query.all()
    serialized_objects = [geo_object.serialize for geo_object in geo_objects]
    data = {
        "total": len(serialized_objects),
        "GeoObjects": serialized_objects,
    }

    with open("GeoObjects.json", "w") as json_file:
        json.dump(data, json_file, indent=2)

    return jsonify({"msg": "GeoObjects loaded to JSON successfully"}), 200


@app.route("/geoObjects/loadFromFile", methods=["POST"])
@jwt_required()
def load_from_file():
    if current_user.rank != "Admin":
        return jsonify({"msg": "Not allowed"}), 403

    try:
        with open("GeoObjects.json") as json_file:
            data = json.load(json_file)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    GeoObject.query.delete()
    for json_object in data["GeoObjects"]:
        db.session.add(GeoObject.deserialize(json_object))
    db.session.commit()

    return jsonify({"msg": "GeoObjects loaded from JSON successfully"}), 200


@app.route("/geoObjects/deleteAll", methods=["POST"])
@jwt_required()
def delete_all():
    if current_user.rank != "Admin":
        return jsonify({"msg": "Not allowed"}), 403

    num_rows_deleted = db.session.query(GeoObject).delete()
    db.session.commit()

    return jsonify({"msg": f"{num_rows_deleted} GeoObjects successfully deleted"}), 200


@app.route("/geoObjects/<id>", methods=["GET"])
def fetchOne(id):
    geo_object = GeoObject.query.get(id)
    if geo_object is None:
        return jsonify({"error": f"GeoObject with id={id} does not exist"}), 404
    return jsonify(geo_object.serialize), 200


@app.route("/geoObjects/syncUser", methods=["GET"])
def syncUser():
    geo_objects = GeoObject.query.all()
    short_objects = [
        {
            "id": geo_object.id,
            "lat": geo_object.latitude,
            "lon": geo_object.longitude,
        }
        for geo_object in geo_objects
    ]
    return jsonify({"total": len(short_objects), "GeoObjects": short_objects}), 200
