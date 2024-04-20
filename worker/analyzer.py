import contextlib
import json
import logging
import lzma
import os
import sqlite3
import subprocess
import threading
from datetime import datetime
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf
from scipy import signal
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from birdnetlib.watcher import DirectoryWatcher


log_level = os.environ.get("LOG_LEVEL", "INFO")
logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.getLevelName(log_level))
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(handler)


def save_spectrogram_json(path):
    y, _ = librosa.load(path)
    hop_length = 4096

    D = librosa.amplitude_to_db(
        np.abs(librosa.stft(y, hop_length=hop_length)), ref=np.max
    )
    data = []
    for y, values in enumerate(D):
        for x, value in enumerate(values):
            data.append({"x": x, "y": y, "fill": round(float(value), 1)})

    filename = os.path.basename(path)
    json_path = Path("/recorder", filename + ".json.xz")
    with lzma.open(json_path, "wt", encoding="UTF-8") as f:
        json.dump(data, f)

    return json_path


def add_detection_to_database(path, highest_confidence):
    # Connect to the database and create a cursor
    conn = sqlite3.connect("/database/birds.db")
    c = conn.cursor()

    filename = os.path.basename(path)
    recording_date = os.path.splitext(filename)[0]
    date_time = datetime.strptime(recording_date, "%Y-%m-%d_%H-%M-%S")
    timestamp = int(date_time.timestamp())

    # Check if the table exists, if not create it
    c.execute(
        """
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='birds';"""
    )
    if not c.fetchone():
        c.execute(
            "CREATE TABLE birds (id INTEGER PRIMARY KEY, recording_date DATETIME, filename TEXT, confidence REAL, common_name TEXT, scientific_name TEXT);"
        )

    # if highest_confidence["is_predicted_for_location_and_date"]:
    c.execute(
        "INSERT INTO birds VALUES (?, ?, ?, ?, ?, ?)",
        (
            None,
            timestamp,
            filename,
            highest_confidence["confidence"],
            highest_confidence["common_name"],
            highest_confidence["scientific_name"],
        ),
    )
    # else:
    #     logger.info(
    #         f"Detection not expected for location and/or date: {highest_confidence}"
    #     )

    # Commit the changes and close the cursor
    conn.commit()
    c.close()


def extract_highest_confidence(recording):
    return max(recording.detections, key=lambda x: x["confidence"])


def make_species_folder(species: str):
    species_path = Path(f"/database/{species}")
    os.makedirs(species_path, exist_ok=True)


def delete_old_files(directory, extension=None):
    p = Path(directory)
    pattern = "**/*"
    if extension:
        pattern += extension
    file_list = list(p.glob(pattern))

    # Sort the filtered files by creation date
    sorted_file_list = sorted(file_list, key=os.path.getctime)

    # Delete all files except for the newest 5
    if len(sorted_file_list) > 5:
        for i in range(len(sorted_file_list) - 5, len(sorted_file_list)):
            os.remove(os.path.join(directory, sorted_file_list[i]))


def on_analyze_complete(recording):
    logger.info(recording.path)
    if recording.detections:
        highest_confidence = extract_highest_confidence(recording)
        species = highest_confidence["scientific_name"].replace(" ", "_")
        make_species_folder(species)
        logger.info(highest_confidence)
        logger.info("Writing to database.")
        add_detection_to_database(recording.path, highest_confidence)
        logger.info("Generating spectrogram data.")
        save_spectrogram_json(recording.path)
        logger.info("Moving file from recorder to database folder.")
        species_database_dir = f"/database/{species}"
        subprocess.run(["mv", recording.path, species_database_dir + "/."])
        subprocess.run(["mv", recording.path + ".json.xz", species_database_dir + "/."])
        delete_old_files(species_database_dir, "mp3")
        delete_old_files(species_database_dir, "xz")
    else:
        logger.info("No detections, removing file.")
        subprocess.run(["rm", "-f", recording.path])


def on_analyze_complete_thread(recording):
    thread = threading.Thread(target=on_analyze_complete, args=(recording,))
    thread.start()


def on_error(recording, error):
    logger.error(f"Error while analyzing {recording.path}: {error}")
    file_name = os.path.basename(recording.path)
    subprocess.run(["mv", recording.path, f"/tmp/error_recording_{file_name}"])


class OutputLogger:
    def __init__(self, logger):
        self.logger = logger
        self._redirector = contextlib.redirect_stdout(self)

    def write(self, msg):
        if msg and not msg.isspace():
            self.logger.info(msg)

    def flush(self):
        pass

    def __enter__(self):
        self._redirector.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # let contextlib do any exception handling here
        self._redirector.__exit__(exc_type, exc_value, traceback)


class CustomDirectoryWatcher(DirectoryWatcher):
    def __init__(self, *args, is_predicted_for_location_and_date=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_predicted_for_location_and_date = is_predicted_for_location_and_date

    def recording_preanalyze(self, recording):
        logger.info("Low-pass filtering recording.")
        y, sr = librosa.load(recording.path)
        y = librosa.util.normalize(y)

        cutoff_high = 500  # Hz
        order = 2

        # Create a Filter using SciPy's Signal module
        b1, a1 = signal.butter(order, cutoff_high / (sr / 2), "high")

        # Apply the filter to the audio signal
        y = signal.lfilter(b1, a1, y)
        sf.write(recording.path, y, sr, format="mp3")

    def _on_closed(self, event):
        # Detect for this file.
        print(f"New file created: {event.src_path}")
        recordings = []
        for analyzer in self.analyzers:
            try:
                recording = Recording(
                    analyzer,
                    event.src_path,
                    week_48=self.week_48,
                    date=self.date,
                    sensitivity=self.sensitivity,
                    lat=self.lat,
                    lon=self.lon,
                    min_conf=self.min_conf,
                    overlap=self.overlap,
                    return_all_detections=self.is_predicted_for_location_and_date,
                )
                # Preparse if method is available.
                self.recording_preanalyze(recording)
                recording.analyze()
                recordings.append(recording)
                self.on_analyze_complete(recording)
            except BaseException as error:
                self.on_error(recording, error)
        self.on_analyze_file_complete(recordings)


if __name__ == "__main__":
    with contextlib.redirect_stdout(OutputLogger(logger=logger)):
        # Load and initialize the BirdNET-Analyzer models.
        custom_model_path = "model.tflite"
        custom_labels_path = "labels.txt"

        analyzer = Analyzer(
            classifier_labels_path=custom_labels_path,
            classifier_model_path=custom_model_path,
        )

        directory = "/recorder"
        watcher = CustomDirectoryWatcher(
            directory,
            analyzers=[analyzer],
            lat=50.0543,
            lon=7.7453,
            date=datetime.today(),
            min_conf=0.3,
            use_polling=True,
            is_predicted_for_location_and_date=True,
        )
        watcher.on_analyze_complete = on_analyze_complete_thread
        watcher.on_error = on_error
        watcher.watch()
