import boto3
import mimetypes
from tqdm import tqdm

bucket = "bucket-name"  # replace with your S3 bucket name
s3 = boto3.client("s3")

# List all objects
paginator = s3.get_paginator("list_objects_v2")
pages = paginator.paginate(Bucket=bucket)

total_fixed = 0

for page in pages:
    for obj in tqdm(page.get("Contents", []), desc="Patching Content-Type"):
        key = obj["Key"]

        # Guess content type
        content_type = mimetypes.guess_type(key)[0] or "binary/octet-stream"

        # Copy object to itself with new metadata
        s3.copy_object(
            Bucket=bucket,
            Key=key,
            CopySource={"Bucket": bucket, "Key": key},
            MetadataDirective="REPLACE",
            ContentType=content_type
        )
        total_fixed += 1

print(f"✅ Content-Type fixed for {total_fixed} objects in {bucket}")
