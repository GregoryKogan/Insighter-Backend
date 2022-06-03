import requests
import json
import os
import concurrent.futures
from apps.GeoObjects.models import GeoObject
from app import db


# TODO: Strange number of new objects


OVERPASS_URL = "http://overpass-api.de/api/interpreter"
WIKIDATA_IMAGE_URL = "https://www.wikidata.org/w/api.php?format=json&action=wbgetclaims&property=P18&entity="
WIKIMEDIA_URL = "https://commons.wikimedia.org/w/thumb.php?width=500&f="

errors = []


def get_image_url(wikidata: str) -> str or None:
    try:
        response = requests.get(WIKIDATA_IMAGE_URL + wikidata).json()
    except Exception as e:
        errors.append(str(e))
        return None
    if (
        "claims" not in response
        or "P18" not in response["claims"]
        or len(response["claims"]["P18"]) == 0
        or "mainsnak" not in response["claims"]["P18"][0]
        or "datavalue" not in response["claims"]["P18"][0]["mainsnak"]
        or "value" not in response["claims"]["P18"][0]["mainsnak"]["datavalue"]
    ):
        return None
    image_name = response["claims"]["P18"][0]["mainsnak"]["datavalue"]["value"]
    return WIKIMEDIA_URL + image_name


def parse_category(geo_object: dict) -> str or None:
    search_line = "".join(
        f"{str(tag)}/" + str(geo_object["tags"][tag]) + "/"
        for tag in geo_object["tags"]
    )
    search_line = search_line.lower()
    with open(os.path.join(os.path.dirname(__file__), "categoryTriggers.json")) as f:
        category_triggers = json.load(f)

    best_category = None
    max_matches = 0
    for category in category_triggers:
        matches = sum(trigger in search_line for trigger in category_triggers[category])
        if matches > max_matches:
            max_matches = matches
            best_category = category

    return best_category


def get_info(geo_object: dict) -> dict or None:
    go_category = parse_category(geo_object)
    if go_category == "ban":
        return None

    if "lat" in geo_object and "lon" in geo_object:
        lat, lon = geo_object["lat"], geo_object["lon"]
    else:
        lat, lon = geo_object["center"]["lat"], geo_object["center"]["lon"]

    return {
        "latitude": lat,
        "longitude": lon,
        "name_ru": geo_object["tags"]["name"],
        "name_en": geo_object["tags"]["name:en"]
        if "name:en" in geo_object["tags"]
        else None,
        "category": go_category,
        "image": get_image_url(geo_object["tags"]["wikidata"]),
        "meta": {
            "phone": geo_object["tags"]["contact:phone"]
            if "contact:phone" in geo_object["tags"]
            else (
                geo_object["tags"]["phone"] if "phone" in geo_object["tags"] else None
            ),
            "website": geo_object["tags"]["contact:website"]
            if "contact:website" in geo_object["tags"]
            else None,
            "opening_hours": geo_object["tags"]["opening_hours"]
            if "opening_hours" in geo_object["tags"]
            else None,
            "wiki": {
                "wikipedia": geo_object["tags"]["wikipedia"],
                "wikidata": geo_object["tags"]["wikidata"],
            },
            "osm": {
                "osm_id": geo_object["id"],
                "osm_type": geo_object["type"],
            },
        },
    }


def scrape() -> int:
    errors = []
    geo_objects = []

    print("Fetching API...")

    with open(os.path.join(os.path.dirname(__file__), "query.txt")) as query:
        query_response = requests.get(
            OVERPASS_URL, params={"data": query.read()}
        ).json()

    print("Got API response")

    processes = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        processes.extend(
            executor.submit(get_info, element)
            for element in query_response["elements"]
            if "tags" in element
            and "name" in element["tags"]
            and (GeoObject.query.filter_by(osm_id=element["id"]).one_or_none() is None)
            and (
                GeoObject.query.filter_by(
                    wikipedia=element["tags"]["wikipedia"]
                ).one_or_none()
                is None
            )
        )

        wiki_articles = set()
        for f in concurrent.futures.as_completed(processes):
            result = f.result()
            if (
                result is not None
                and result["meta"]["wiki"]["wikipedia"] not in wiki_articles
            ):
                wiki_articles.add(result["meta"]["wiki"]["wikipedia"])
                geo_objects.append(result)

                print(f"{len(geo_objects)} GeoObjects processed")

    print("Writing to DB...")

    db_objects = []
    for item in geo_objects:
        db_object = GeoObject.deserialize(item)
        db_objects.append(db_object)
        db.session.add(db_object)
    db.session.commit()

    print("Scraping done!")

    return db_objects, errors


if __name__ == "__main__":
    scrape()
