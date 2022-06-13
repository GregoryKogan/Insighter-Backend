from app import db
import datetime


class GeoObject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(30), default="unknown")
    image = db.Column(db.String(256))
    latitude = db.Column(db.Float(), nullable=False)
    longitude = db.Column(db.Float(), nullable=False)
    name_en = db.Column(db.String(85))
    name_ru = db.Column(db.String(85), nullable=False)
    opening_hours = db.Column(db.String(256))
    osm_id = db.Column(db.Integer, nullable=False)
    osm_type = db.Column(db.String(32))
    phone = db.Column(db.String(32))
    website = db.Column(db.String(128))
    wikidata = db.Column(db.String(32), nullable=False)
    wikipedia = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return "<GeoObject %>" % self.id

    @property
    def serialize(self):
        return {
            "id": self.id,
            "category": self.category,
            "image": self.image,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "name_en": self.name_en,
            "name_ru": self.name_ru,
            "meta": {
                "opening_hours": self.opening_hours,
                "phone": self.phone,
                "website": self.website,
                "wiki": {"wikidata": self.wikidata, "wikipedia": self.wikipedia},
                "osm": {"osm_id": self.osm_id, "osm_type": self.osm_type},
            },
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @staticmethod
    def deserialize(json: dict) -> object:
        db_object = GeoObject(
            category=json["category"],
            image=json["image"],
            latitude=json["latitude"],
            longitude=json["longitude"],
            name_en=json["name_en"],
            name_ru=json["name_ru"],
            opening_hours=json["meta"]["opening_hours"],
            osm_id=json["meta"]["osm"]["osm_id"],
            osm_type=json["meta"]["osm"]["osm_type"],
            phone=json["meta"]["phone"],
            website=json["meta"]["website"],
            wikidata=json["meta"]["wiki"]["wikidata"],
            wikipedia=json["meta"]["wiki"]["wikipedia"],
        )

        if "created_at" in json:
            db_object.created_at = datetime.datetime.fromisoformat(json["created_at"])
        if "updated_at" in json:
            db_object.updated_at = datetime.datetime.fromisoformat(json["updated_at"])

        return db_object
