import boto3
from PIL import Image
import io

s3 = boto3.client("s3")

def lambda_handler(event, context):

    # --- Get bucket + key from the S3 event ---
    # record = event["Records"][0]
    # source_bucket = record["s3"]["bucket"]["name"]
    # source_key = record["s3"]["object"]["key"]

    if "Records" in event:
        record = event["Records"][0]
        source_bucket = record["s3"]["bucket"]["name"]
        source_key = record["s3"]["object"]["key"]
    else:
        source_bucket = "chels-original-images"
        source_key = "input/test.jpg"


    # --- Download the file from S3 ---
    obj = s3.get_object(Bucket=source_bucket, Key=source_key)
    img_data = obj["Body"].read()

    print("HEAD:", img_data[:20])  # Debug line

    # --- Safe image load for ALL formats ---
    stream = io.BytesIO(img_data)
    stream.seek(0)
    img = Image.open(stream)
    img.load()
    img = img.convert("RGB")

    # --- Resize while preserving aspect ratio ---
    new_width = 500
    width_percent = (new_width / float(img.size[0]))
    new_height = int(float(img.size[1]) * float(width_percent))

    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # --- Save resized image to memory buffer ---
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    buffer.seek(0)

    # --- Build output filename ---
    filename = source_key.split("/")[-1]
    resized_key = "output/resized-" + filename

    # --- Output bucket ---
    destination_bucket = "chels-resized-images"

    # --- Upload resized image to output bucket ---
    s3.put_object(
        Bucket=destination_bucket,
        Key=resized_key,
        Body=buffer,
        ContentType="image/jpeg"
    )

    print("SUCCESS:", resized_key)

    return {
        "status": "SUCCESS",
        "source": f"{source_bucket}/{source_key}",
        "destination": f"{destination_bucket}/{resized_key}"
    }
