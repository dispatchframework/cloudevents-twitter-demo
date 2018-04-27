import io
import json
import requests
import sys
import traceback

from twython import Twython
from PIL import Image


watermark = None
watermark_url = "https://github.com/vmware/dispatch/raw/master/docs/assets/images/logo-small-200.png"  # noqa


def get_image(url):
    r = requests.get(url)
    if r.status_code == 200:
        return Image.open(io.BytesIO(r.content))


def get_watermark_image():
    return get_image(watermark_url)


def handle(ctx, payload):
    try:
        return handle2(ctx, payload)
    except Exception:
        exc_type, exc_value, exc_tb = sys.exc_info()
        return json.dumps({
            'traceback': ''.join(
                traceback.format_exception(exc_type, exc_value, exc_tb))})


def handle2(ctx, payload):
    global watermark

    if ctx is not None:
        secrets = ctx["secrets"]

        if secrets is None:
            raise Exception("Requires twitter secrets")

        appKey = secrets["appKey"]
        appSecret = secrets["appSecret"]
        oathToken = secrets["oathToken"]
        oathTokenSecret = secrets["oathTokenSecret"]

    if 'cloudEventsVersion' not in payload:
        return {"status": 422}

    if payload['cloudEventsVersion'] != "0.1":
        return {"status": 422}

    if payload['eventType'] == "Microsoft.Storage.BlobCreated":
        img = get_image(payload['data']['url'])
    elif payload['eventType'] == "aws.s3.object.created":
        bucket = payload['data']['bucket']['name']
        key = payload['data']['object']['key']
        url = "https://s3.amazonaws.com/%s/%s" % (bucket, key)
        img = get_image(url)
    else:
        return {"status": 422}

    # Cache watermark
    if watermark is None:
        watermark = get_watermark_image()

    # Watermark and thumbnail the image
    img.paste(watermark, (10, 10), watermark)
    img.thumbnail((1024, 512), Image.ANTIALIAS)

    # Save into a byte stream to send to twitter
    final_image = io.BytesIO()
    img.save(final_image, format="PNG")
    final_image.seek(0)

    # Send to twitter, first upload media and then update status
    twitter = Twython(appKey, appSecret, oathToken, oathTokenSecret)
    response = twitter.upload_media(media=final_image)
    twitter.update_status(status='Upload from VMware Dispatch',
                          media_ids=[response['media_id']])
    return {"status": 200}
