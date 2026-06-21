from tinydb import Query, TinyDB
from logging import getLogger
from base64 import b64encode
from requests import post, get, RequestException
import subprocess
import time
from os import listdir, path
from re import search


logger = getLogger("hairloss")

OLLAMA_URL = "http://localhost:11434"

PROMPT = """
Think
You are a visual estimator of scalp hair density.

You will be given:

an image
an angle label: "top", "lateral", or "face"

Angle meaning:

top: evaluate crown/vertex only
lateral: evaluate temple recession and side density
face: evaluate frontal hairline and symmetry

Task:
Estimate hair loss severity as a continuous value between 0.0 and 1.0.

Scoring meaning:

0.0 → full dense hair
0.5 → moderate thinning / visible scalp
1.0 → severe hair loss

Guidelines:

Use only visible evidence in the image.
Be robust to lighting and hairstyle, but consider scalp visibility.
Only evaluate regions that are visible from the given angle.
If a region is not visible, do not infer it.

If image quality is unclear:

use a neutral estimate based on visible areas (do not guess extremes)

Output:
Return ONLY a single float between 0.0 and 1.0.
No text, no explanation, no punctuation.
"""

def prepareModel(timeout: int = 15):
    try:
        get(f"{OLLAMA_URL}/api/tags", timeout=2)
        logger.info("Ollama already running")
        return
    except RequestException:
        logger.info("Ollama not running, starting server...")

    subprocess.Popen(
        ["ollama", "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    start = time.time()
    while time.time() - start < timeout:
        try:
            get(f"{OLLAMA_URL}/api/tags", timeout=2)
            logger.info("Ollama server started")
            return
        except RequestException:
            time.sleep(1)

    raise RuntimeError("Failed to start Ollama server")

def evaluate(image_path: str, model: str, repetitions: int = 10, timeOut: int = 10):
    db = TinyDB(path.abspath(path.join(image_path, "../hairlineResults.json")))
    q = Query()
    prepareModel()

    for image in listdir(image_path):
        oldInfo = db.get(q.filename == image)
        if model in oldInfo.keys():
            logger.info(f"Skipping evaluation {image} with {model}...")
            continue
        logger.info(f"Evaluating {image} with model {model} {repetitions} times.")
        with open(path.join(image_path, image), "rb") as f:
            imageb64 = b64encode(f.read()).decode("utf-8")
        average = 0
        averageWithoutUnsure = 0
        averageWithoutUnsureCount = 0
        if "f" in image:
            angle = "face"
        elif "l" in image:
            angle = "lateral"
        elif "t" in image:
            angle = "top"
        else:
            raise ValueError(f"no angle information in filename {image}")
        imagePrompt = PROMPT + f"\nlabel:\"{angle}\""
        for i in range(repetitions): # we ask multiple times and get the average response
            response = post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": model,
                    "prompt": imagePrompt,
                    "images": [imageb64],
                    "stream": False,
                    "thinking": model != "qwen3-vl:8b" # for some reason this model thinkgs so much, that it spends all it's tokens on thinking and None in output...
                },
                timeout=timeOut,
                )

            response.raise_for_status()
            logger.debug(response.json())
            result = search(r"^(0(?:\.\d+)?|1(?:\.0+)?)$", response.json()["response"].strip())
            logger.debug(result)
            if result == None:
                result = 0.5
            else:
                data = float(search(r"^(0(?:\.\d+)?|1(?:\.0+)?)$", response.json()["response"].strip()).group(1)) # extract the float in case it outputed some text

            if data != 0.5: # if the model is uncertain it should return 0.5
                averageWithoutUnsure += data
                averageWithoutUnsureCount += 1
            average += data
        average /= repetitions
        if averageWithoutUnsureCount != 0: # avoids case where all repetitions are unsure
            averageWithoutUnsure /= averageWithoutUnsureCount
        else:
            averageWithoutUnsure = 0.5

        if db.contains(q.filename == image): # we add the result to a database. It allows to do everything in multiple runs and combine results from multiple models
            imageResult = db.get(q.filename == image)
            imageResult[model] = average
            imageResult[model+"WithoutUnsure"] = averageWithoutUnsure
            db.upsert(imageResult, q.filename == image)
        else:
            imageResult = {
                "filename": image,
                model: average,
                model + "WithoutUnsure": averageWithoutUnsure
            }
            db.upsert(imageResult, q.filename == image)

    logger.info("Normalizing values ...")
    # normalise values
    maxValue = max(image[model + "WithoutUnsure"] for image in db)
    minValue = min(image[model + "WithoutUnsure"] for image in db)
    for image in listdir(image_path):
        unnormalizedValues = db.get(q.filename == image)
        unnormalizedValues[model+"Normalized"] = (unnormalizedValues[model+"WithoutUnsure"] - minValue)/(maxValue - minValue)
        db.upsert(unnormalizedValues, q.filename == image)
    logger.info("Stopping model...")
    subprocess.Popen(
        ["ollama", "stop", model],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
