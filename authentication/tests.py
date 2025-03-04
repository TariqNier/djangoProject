import os

import boto3
from PIL import Image
from io import BytesIO

from botocore.config import Config

from photographer.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_ENDPOINT_URL, AWS_STORAGE_BUCKET_NAME

AWS_S3_REGION_NAME = "eu2"

AWS_S3_ENDPOINT = f'{AWS_S3_REGION_NAME}.contabostorage.com'

# إعداد العميل لـ S3
s3 = boto3.client(
    's3',
    aws_access_key_id="6fc7b3f732b855d29ee3d0b6e0a6a3ce",
    aws_secret_access_key="53e3e111e79c5cea4382fda3374733da",
    region_name="eu2",
    endpoint_url=f"https://{AWS_S3_ENDPOINT}"

)


def download_and_compress_image(event, context):
    original_image_key = event.get("image_key")
    # تحميل الصورة من S3
    response = s3.get_object(Bucket="tosandev", Key=original_image_key)
    image_data = response['Body'].read()

    # فتح الصورة باستخدام Pillow
    image = Image.open(BytesIO(image_data))
    for size in [700, 400, 50]:

        image = image.resize((size, size))

        # استخراج نوع الملف من امتداد الصورة الأصلية
        file_extension = os.path.splitext(original_image_key)[1].lower()
        if file_extension == ".jpg" or file_extension == ".jpeg":
            image_format = "JPEG"
        elif file_extension == ".png":
            image_format = "PNG"
        else:
            raise ValueError("Unsupported image format")

        # ضغط الصورة بعد تغيير حجمها
        compressed_image_io = BytesIO()
        image.save(compressed_image_io, format=image_format, quality=85)
        compressed_image_io.seek(0)

        # رفع الصورة المضغوطة والمعدلة إلى S3
        s3.put_object(Bucket="tosandev", Key=f"{size}/{original_image_key}", Body=compressed_image_io)
        print(f"Uploaded {size}/{original_image_key}")
    return {
        'statusCode': 200
    }


def get_image_url():
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        config=Config(region_name=AWS_S3_REGION_NAME),
        endpoint_url=AWS_S3_ENDPOINT_URL
    )

    bucket_name = AWS_STORAGE_BUCKET_NAME
    objects = s3.list_objects_v2(Bucket=bucket_name, Prefix="sameh")
    urls = []

    for obj in objects.get('Contents', []):
        file_key = obj['Key']

        # توليد رابط pre-signed لكل ملف
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': file_key},
            ExpiresIn=3600
        )

        urls.append(url)
    return urls


print(get_image_url())
