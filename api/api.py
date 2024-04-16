import json
import logging
import lzma
import os
from pathlib import Path
from urllib.parse import quote_plus
from datetime import datetime

import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from sqlalchemy import create_engine, text


log_level = os.environ.get("LOG_LEVEL", "INFO")
logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.getLevelName(log_level))
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(handler)

api_root = os.environ.get("API_ROOT_PATH")
app = FastAPI(root_path=api_root)
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://birdpihinterweg.stevenpilger.com",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_engine = create_engine("sqlite:////database/birds.db")


@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend())


NOT_BIRDS = [
    "Acris crepitans_Northern Cricket Frog",
    "Acris gryllus_Southern Cricket Frog",
    "Allonemobius allardi_Allard's Ground Cricket",
    "Allonemobius tinnulus_Tinkling Ground Cricket",
    "Allonemobius walkeri_Walker's Ground Cricket",
    "Alouatta pigra_Mexican Black Howler Monkey",
    "Amblycorypha alexanderi_Clicker Round-winged Katydid",
    "Amblycorypha longinicta_Common Virtuoso Katydid",
    "Amblycorypha oblongifolia_Oblong-winged Katydid",
    "Amblycorypha rotundifolia_Rattler Round-winged Katydid",
    "Anaxipha exigua_Say's Trig",
    "Anaxyrus americanus_American Toad",
    "Anaxyrus canorus_Yosemite Toad",
    "Anaxyrus cognatus_Great Plains Toad",
    "Anaxyrus fowleri_Fowler's Toad",
    "Anaxyrus houstonensis_Houston Toad",
    "Anaxyrus microscaphus_Arizona Toad",
    "Anaxyrus quercicus_Oak Toad",
    "Anaxyrus speciosus_Texas Toad",
    "Anaxyrus terrestris_Southern Toad",
    "Anaxyrus woodhousii_Woodhouse's Toad",
    "Apis mellifera_Honey Bee",
    "Atlanticus testaceus_Protean Shieldback",
    "Canis latrans_Coyote",
    "Canis lupus_Gray Wolf",
    "Conocephalus brevipennis_Short-winged Meadow Katydid",
    "Conocephalus fasciatus_Slender Meadow Katydid",
    "Cyrtoxipha columbiana_Columbian Trig",
    "Dryophytes andersonii_Pine Barrens Treefrog",
    "Dryophytes arenicolor_Canyon Treefrog",
    "Dryophytes avivoca_Bird-voiced Treefrog",
    "Dryophytes chrysoscelis_Cope's Gray Treefrog",
    "Dryophytes cinereus_Green Treefrog",
    "Dryophytes femoralis_Pine Woods Treefrog",
    "Dryophytes gratiosus_Barking Treefrog",
    "Dryophytes squirellus_Squirrel Treefrog",
    "Dryophytes versicolor_Gray Treefrog",
    "Eleutherodactylus planirostris_Greenhouse Frog",
    "Eunemobius carolinus_Carolina Ground Cricket",
    "Eunemobius confusus_Confused Ground Cricket",
    "Gastrophryne carolinensis_Eastern Narrow-mouthed Toad",
    "Gastrophryne olivacea_Great Plains Narrow-mouthed Toad",
    "Gryllus assimilis_Gryllus assimilis",
    "Gryllus fultoni_Southern Wood Cricket",
    "Gryllus pennsylvanicus_Fall Field Cricket",
    "Gryllus rubens_Southeastern Field Cricket",
    "Hyliola regilla_Pacific Chorus Frog",
    "Incilius valliceps_Gulf Coast Toad",
    "Lithobates catesbeianus_American Bullfrog",
    "Lithobates clamitans_Green Frog",
    "Lithobates palustris_Pickerel Frog",
    "Lithobates sylvaticus_Wood Frog",
    "Microcentrum rhombifolium_Greater Angle-wing",
    "Miogryllus saussurei_Miogryllus saussurei",
    "Neoconocephalus bivocatus_False Robust Conehead",
    "Neoconocephalus ensiger_Sword-bearing Conehead",
    "Neoconocephalus retusus_Round-tipped Conehead",
    "Neoconocephalus robustus_Robust Conehead",
    "Neonemobius cubensis_Cuban Ground Cricket",
    "Odocoileus virginianus_White-tailed Deer",
    "Oecanthus celerinictus_Fast-calling Tree Cricket",
    "Oecanthus exclamationis_Davis's Tree Cricket",
    "Oecanthus fultoni_Snowy Tree Cricket",
    "Oecanthus nigricornis_Blackhorned Tree Cricket",
    "Oecanthus niveus_Narrow-winged Tree Cricket",
    "Oecanthus pini_Pine Tree Cricket",
    "Oecanthus quadripunctatus_Four-spotted Tree Cricket",
    "Orchelimum agile_Agile Meadow Katydid",
    "Orchelimum concinnum_Stripe-faced Meadow Katydid",
    "Orchelimum pulchellum_Handsome Meadow Katydid",
    "Orocharis saltator_Jumping Bush Cricket",
    "Phyllopalpus pulchellus_Handsome Trig",
    "Pseudacris brimleyi_Brimley's Chorus Frog",
    "Pseudacris clarkii_Spotted Chorus Frog",
    "Pseudacris crucifer_Spring Peeper",
    "Pseudacris feriarum_Upland Chorus Frog",
    "Pseudacris nigrita_Southern Chorus Frog",
    "Pseudacris ocularis_Little Grass Frog",
    "Pseudacris ornata_Ornate Chorus Frog",
    "Pseudacris streckeri_Strecker's Chorus Frog",
    "Pseudacris triseriata_Striped Chorus Frog",
    "Pterophylla camellifolia_Common True Katydid",
    "Scaphiopus couchii_Couch's Spadefoot",
    "Sciurus carolinensis_Eastern Gray Squirrel",
    "Scudderia curvicauda_Curve-tailed Bush Katydid",
    "Scudderia furcata_Fork-tailed Bush Katydid",
    "Scudderia texensis_Texas Bush Katydid",
    "Spea bombifrons_Plains Spadefoot",
    "Tamias striatus_Eastern Chipmunk",
    "Tamiasciurus hudsonicus_Red Squirrel",
    "Human vocal_Human vocal",
    "Human non-vocal_Human non-vocal",
    "Human whistle_Human whistle",
    "Dog_Dog",
    "Power tools_Power tools",
    "Siren_Siren",
    "Engine_Engine",
    "Gun_Gun",
    "Fireworks_Fireworks",
    "Environmental_Environmental",
    "Noise_Noise",
]
NOT_BIRDS_SCIENTIFIC = [not_bird.split("_")[0] for not_bird in NOT_BIRDS]
NOT_BIRDS_COMMON = [not_bird.split("_")[1] for not_bird in NOT_BIRDS]


@app.get("/stats")
async def get_stats() -> JSONResponse:
    date = datetime.now().strftime("%Y-%m-%d")
    where_date_today = (
        f"WHERE strftime('%Y-%m-%d', datetime(recording_date, 'unixepoch')) = '{date}'"
    )

    with db_engine.connect() as conn:
        query = text(
            f"SELECT COUNT(*) FROM birds {where_date_today} AND confidence >= 0.7"
        )
        count_today = conn.execute(query).fetchone()[0]

        query = text(
            "SELECT COUNT(*) FROM birds WHERE datetime(recording_date, 'unixepoch') >= datetime('now', '-1 hour') AND confidence >= 0.7"
        )
        count_last_hour = conn.execute(query).fetchone()[0]

        query = text(
            "SELECT COUNT(DISTINCT scientific_name) FROM birds WHERE confidence >= 0.7"
        )
        count_unique_species = conn.execute(query).fetchone()[0]

        query = text(
            f"SELECT COUNT(DISTINCT scientific_name) FROM birds {where_date_today} AND confidence >= 0.7"
        )
        count_unique_species_today = conn.execute(query).fetchone()[0]

        # Create a JSON response with the row count
        return JSONResponse(
            {
                "today": count_today,
                "last_hour": count_last_hour,
                "total_unique_species": count_unique_species,
                "total_unique_species_today": count_unique_species_today,
            }
        )


@app.get("/detections")
async def get_detections(date=False) -> JSONResponse:
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    else:
        year, month, day = [int(x) for x in date.split("-")]
        date = datetime(year, month, day)
        date = date.strftime("%Y-%m-%d")
    date_select = (
        f"strftime('%Y-%m-%d', datetime(recording_date, 'unixepoch')) = '{date}'"
    )
    print(date_select)

    with db_engine.connect() as conn:
        scientific_names_str = ", ".join([f'"{name}"' for name in NOT_BIRDS_SCIENTIFIC])
        query_text = f"""
        SELECT
            scientific_name,
            common_name,
            strftime('%Y-%m-%dT%H:%M:%SZ', datetime(recording_date, 'unixepoch')) AS hour,
            COUNT(*) AS recordings_count
        FROM
            birds
        WHERE
            {date_select}
            AND confidence >= 0.7
            AND scientific_name IN (
                SELECT scientific_name
                FROM birds
                WHERE {date_select}
                    AND confidence >= 0.7
                    AND scientific_name NOT IN ({scientific_names_str})
                GROUP BY scientific_name
                ORDER BY COUNT(*) DESC
                LIMIT 10
            )
        GROUP BY
            scientific_name, strftime('%Y-%m-%d%H', datetime(recording_date, 'unixepoch'))
        ORDER BY
            recordings_count DESC;
        """
        query = text(query_text)
        detections = conn.execute(query).fetchall()
        detections_response = [
            {
                "scientific_name": row[0],
                "common_name": row[1],
                "datetime": row[2],
                "count": row[3],
            }
            for row in detections
        ]
        return JSONResponse(detections_response)


@app.get("/most_recent")
async def get_most_recent(n: int = 1) -> JSONResponse:
    with db_engine.connect() as conn:
        scientific_names_str = ", ".join([f'"{name}"' for name in NOT_BIRDS_SCIENTIFIC])
        query = text(
            f"SELECT * FROM birds WHERE scientific_name NOT IN ({scientific_names_str}) AND confidence >= 0.7 ORDER BY id DESC LIMIT {n};"
        )
        if n > 1:
            most_recent = conn.execute(query).fetchall()
        else:
            most_recent = [conn.execute(query).fetchone()]

        response = []
        for i in most_recent:
            response.append(
                {
                    "id": i[0],
                    "recording_date": i[1],
                    "file_name": i[2],
                    "confidence": i[3],
                    "common_name": i[4],
                    "scientific_name": i[5],
                }
            )

        return JSONResponse(response)


@app.get("/spectrogram")
@cache(expire=15)
async def get_spectrogram(id: int = 1) -> JSONResponse:
    with db_engine.connect() as conn:
        query = text(f"SELECT * FROM birds WHERE id = {id}")
        file_name = conn.execute(query).fetchone()[2]
        file_name += ".json.xz"
        file_path = Path("/database", file_name)

        try:
            with lzma.open(file_path, "rt", encoding="UTF-8") as f:
                data = json.load(f)
            return JSONResponse(data)
        except FileNotFoundError:
            logger.warning(f"{file_path} was not found on disk.")


@app.get("/birdimage")
@cache(expire=3600)
async def get_bird_image(scientific_name) -> JSONResponse:
    token = os.environ.get("FLICKR_API_TOKEN")
    URL_SEARCH = f"https://www.flickr.com/services/rest/?method=flickr.photos.search&api_key={token}&text={quote_plus(scientific_name)}&safe_search=&format=json&nojsoncallback=1&extras=url_sq"
    search_response = requests.get(URL_SEARCH)
    if search_response.ok:
        data = search_response.json()
        image_url = data["photos"]["photo"][0]["url_sq"]
        return JSONResponse(image_url)
