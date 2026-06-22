from pathlib import Path
from uuid import uuid4

from flask import current_app
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
}


class UploadError(Exception):
    def __init__(self, error_code, message, status_code=400):
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.status_code = status_code


def _detect_image_type(content):
    if content.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if content.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if len(content) >= 12 and content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        return "image/webp"
    return None


def save_uploaded_images(files):
    if not files:
        raise UploadError("VALIDATION_ERROR", "请选择要上传的图片", 400)
    if len(files) > 9:
        raise UploadError("VALIDATION_ERROR", "一次最多上传 9 张图片", 400)

    upload_dir = Path(current_app.config["UPLOAD_FOLDER"]) / "images"
    upload_dir.mkdir(parents=True, exist_ok=True)
    max_bytes = current_app.config["UPLOAD_IMAGE_MAX_BYTES"]

    urls = []
    for file_storage in files:
        filename = secure_filename(file_storage.filename or "")
        extension = Path(filename).suffix.lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise UploadError("VALIDATION_ERROR", "仅支持 JPG、PNG、GIF 和 WEBP 图片", 400)

        content = file_storage.read()
        if not content:
            raise UploadError("VALIDATION_ERROR", "图片内容不能为空", 400)
        if len(content) > max_bytes:
            raise UploadError("VALIDATION_ERROR", "单张图片不能超过 5MB", 400)

        detected_mime = _detect_image_type(content)
        if detected_mime != ALLOWED_EXTENSIONS[extension]:
            raise UploadError("VALIDATION_ERROR", "图片文件类型与扩展名不匹配", 400)
        if file_storage.mimetype and file_storage.mimetype != detected_mime:
            raise UploadError("VALIDATION_ERROR", "图片 MIME 类型无效", 400)

        stored_name = f"{uuid4().hex}{extension}"
        target = upload_dir / stored_name
        target.write_bytes(content)
        urls.append(f"/uploads/images/{stored_name}")

    return urls
