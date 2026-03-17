import io
import piexif
from PIL import Image
from PIL.ExifTags import TAGS


def extract_exif(image_bytes: bytes) -> tuple[str, bool]:
    """Extract EXIF metadata from image bytes.
    Returns (summary_string, has_exif_bool).
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
    except Exception:
        return "Could not open image for EXIF extraction", False

    exif_data = {}

    # JPEG path
    if hasattr(img, "_getexif") and img._getexif():
        raw = img._getexif()
        for tag_id, value in raw.items():
            tag = TAGS.get(tag_id, tag_id)
            exif_data[tag] = value

    # PNG / other path
    if not exif_data and "exif" in img.info:
        try:
            piexif_data = piexif.load(img.info["exif"])
            ifd_map = {
                "0th": piexif.ImageIFD,
                "Exif": piexif.ExifIFD,
                "GPS": piexif.GPSIFD,
            }
            for ifd_name, ifd in ifd_map.items():
                for tag_id, value in piexif_data.get(ifd_name, {}).items():
                    tag = piexif.TAGS.get(ifd_name, {}).get(tag_id, {}).get("name", tag_id)
                    exif_data[tag] = value
        except Exception:
            pass

    if not exif_data:
        return "No EXIF data present", False

    parts = []

    make = exif_data.get("Make") or exif_data.get(271)
    model = exif_data.get("Model") or exif_data.get(272)
    if make or model:
        camera = " ".join(filter(None, [
            make.decode() if isinstance(make, bytes) else str(make),
            model.decode() if isinstance(model, bytes) else str(model),
        ]))
        parts.append(f"Camera: {camera}")

    software = exif_data.get("Software") or exif_data.get(305)
    if software:
        sw = software.decode() if isinstance(software, bytes) else str(software)
        parts.append(f"Software: {sw.strip()}")

    dt = exif_data.get("DateTimeOriginal") or exif_data.get(36867)
    if dt:
        d = dt.decode() if isinstance(dt, bytes) else str(dt)
        parts.append(f"Datetime: {d}")

    gps = exif_data.get("GPSInfo") or exif_data.get(34853)
    parts.append(f"GPS: {'present' if gps else 'absent'}")

    flash = exif_data.get("Flash") or exif_data.get(37385)
    if flash is not None:
        parts.append(f"Flash: {'fired' if flash else 'no flash'}")

    return ", ".join(parts) if parts else "EXIF present but no readable fields", True
