import logging
import os

from flask import Flask, send_from_directory
from PIL import Image
from werkzeug.utils import secure_filename

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

ASSETS_DIRECTORY = os.environ.get("ASSETS_DIRECTORY", "")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


@app.route("/<path:path>")
def send_assets(path):
    # remove /assets/ from start of path that is passed from nginx
    path = path.replace("/assets/", "")

    filename = secure_filename(path)
    original_filename = filename

    full_path = os.path.abspath(os.path.join(ASSETS_DIRECTORY, filename))

    if not full_path.startswith(os.path.abspath(ASSETS_DIRECTORY)):
        return 400

    extension = os.path.splitext(filename)[1].lower()
    filename_without_extension = os.path.splitext(filename)[0]

    if filename.startswith("."):
        return 400

    if extension not in ALLOWED_EXTENSIONS:
        return send_from_directory(ASSETS_DIRECTORY, filename)

    if extension != ".webp":
        filename_with_webp = original_filename.replace(extension, ".webp")
    else:
        filename_with_webp = original_filename

    if not os.path.exists(os.path.join(ASSETS_DIRECTORY, filename_with_webp)):
        image = Image.open(os.path.join(ASSETS_DIRECTORY, filename))

        image.save(os.path.join(ASSETS_DIRECTORY, filename_with_webp), "webp", exif=b"")

    return send_from_directory(
        ASSETS_DIRECTORY, filename_with_webp, as_attachment=False, mimetype="image/webp"
    )


if __name__ == "__main__":
    app.run(debug=True, port=5005)
