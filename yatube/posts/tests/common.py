from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


def image(name: str = "giffy.png") -> SimpleUploadedFile:
    file = BytesIO()
    Image.new("RGBA", size=(1, 1), color=(155, 0, 0)).save(file, "png")
    file.seek(0)
    return SimpleUploadedFile(
        name=name,
        content=file.read(),
        content_type="image/png",
    )
