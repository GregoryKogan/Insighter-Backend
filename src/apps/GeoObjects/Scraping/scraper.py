import requests
import json
import os
import concurrent.futures


OVERPASS_URL = "http://overpass-api.de/api/interpreter"
WIKIDATA_IMAGE_URL = "https://www.wikidata.org/w/api.php?format=json&action=wbgetclaims&property=P18&entity="
WIKIMEDIA_URL = "https://commons.wikimedia.org/w/thumb.php?width=500&f="


def get_image_url(wikidata: str) -> str or None:
    try:
        response = requests.get(WIKIDATA_IMAGE_URL + wikidata).json()
    except Exception as e:
        print("STRANGE ERROR")
        print(e)
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
    image_url = WIKIMEDIA_URL + image_name
    return image_url


def parse_category(geo_object: dict) -> str or None:
    search_line = ""
    for tag in geo_object["tags"]:
        search_line += str(tag) + "/" + str(geo_object["tags"][tag]) + "/"
    search_line = search_line.lower()

    with open(os.path.join(os.path.dirname(__file__), "categoryTriggers.json")) as f:
        category_triggers = json.load(f)

    best_category = None
    max_matches = 0
    for category in category_triggers:
        matches = 0
        for trigger in category_triggers[category]:
            matches += trigger in search_line
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
        "osm_id": geo_object["id"],
        "osm_type": geo_object["type"],
        "latitude": lat,
        "longitude": lon,
        "name_ru": geo_object["tags"]["name"],
        "name_en": geo_object["tags"]["name:en"]
        if "name:en" in geo_object["tags"]
        else None,
        "category": go_category,
        "wikipedia": geo_object["tags"]["wikipedia"],
        "wikidata": geo_object["tags"]["wikidata"],
        "image": get_image_url(geo_object["tags"]["wikidata"]),
        "phone": geo_object["tags"]["contact:phone"]
        if "contact:phone" in geo_object["tags"]
        else (geo_object["tags"]["phone"] if "phone" in geo_object["tags"] else None),
        "website": geo_object["tags"]["contact:website"]
        if "contact:website" in geo_object["tags"]
        else None,
        "opening_hours": geo_object["tags"]["opening_hours"]
        if "opening_hours" in geo_object["tags"]
        else None,
    }


def main():
    geo_objects = []

    with open(os.path.join(os.path.dirname(__file__), "query.txt")) as query:
        query_response = requests.get(
            OVERPASS_URL, params={"data": query.read()}
        ).json()

    processes = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for index, element in enumerate(query_response["elements"]):
            if "tags" in element and "name" in element["tags"]:
                processes.append(executor.submit(get_info, element))

        wiki_articles = set()
        for f in concurrent.futures.as_completed(processes):
            result = f.result()
            if result is not None and result["wikipedia"] not in wiki_articles:
                wiki_articles.add(result["wikipedia"])
                geo_objects.append(result)
                print(len(geo_objects))

    print(f"TOTAL: {len(geo_objects)}")
    
    with open(os.path.join(os.path.dirname(__file__),"Moscow.json"), "w") as file:
        json.dump(geo_objects, file, ensure_ascii=False, sort_keys=True, indent=2)


if __name__ == "__main__":
    main()
