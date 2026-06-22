from flask import Blueprint, current_app, request, send_from_directory

from app.middleware.auth import require_auth
from app.services.uploads import UploadError, save_uploaded_images
from app.utils.response import error_response, success_response


uploads_bp = Blueprint("uploads", __name__)


def _uploaded_files():
    files = []
    for field_name in ("images", "file"):
        files.extend(request.files.getlist(field_name))
    if not files:
        files.extend(request.files.values())
    return files


@uploads_bp.post("/api/v1/uploads/images")
@require_auth
def upload_images():
    try:
        urls = save_uploaded_images(_uploaded_files())
    except UploadError as error:
        return error_response(error.error_code, error.message, error.status_code)

    return success_response(data={"urls": urls}, message="图片已上传", status_code=201)


@uploads_bp.get("/uploads/images/<path:filename>")
def uploaded_image(filename):
    return send_from_directory(
        f"{current_app.config['UPLOAD_FOLDER']}/images",
        filename,
    )
