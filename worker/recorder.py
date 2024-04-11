import logging
import os
import subprocess
import sys
import threading
from datetime import datetime
from time import sleep


log_level = os.environ.get("LOG_LEVEL", "INFO")
logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.getLevelName(log_level))
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(handler)


def log_subprocess_output(pipe):
    for line in iter(pipe.readline, b""):  # b'\n'-separated lines
        logger.info(line)


def run_recording():
    file_name = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mp3"
    tmp_path = f"/tmp/{file_name}"
    fin_path = f"/recorder/{file_name}"
    logger.info(f"Recording: {file_name}")
    command = f"arecord -D hw:1 -f S16_LE -c1 -r44100 -d 15 {tmp_path}".split(' ')
    # command = [
    #     "ffmpeg",
    #     "-hide_banner",
    #     "-f",
    #     "alsa",
    #     "-i",
    #     "default",
    #     "-t",
    #     "15",
    #     "-c",
    #     "libmp3lame",
    #     "-q:a",
    #     "4",
    #     "-loglevel",
    #     "panic",
    #     tmp_path,
    # ]
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    with process.stdout:
        log_subprocess_output(process.stdout)
    exitcode = process.wait()
    subprocess.run(["mv", tmp_path, fin_path])
    sys.exit(exitcode)

# Sleep initially to wait for the analyzer to come up.
sleep(30)

# Main loop, where recording is done.
while True:
    logger.info("Starting thread.")
    thread = threading.Thread(target=run_recording)
    thread.start()
    logger.info("Sleeping...")
    
    # Sleep one second longer than recording to ensure the audio device is free.
    sleep(16)
