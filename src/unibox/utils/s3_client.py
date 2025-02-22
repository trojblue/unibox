import logging
import os
from pathlib import Path
from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError
from tqdm.auto import tqdm


def parse_s3_url(url: str):
    parsed_url = urlparse(url)
    if parsed_url.scheme != "s3":
        raise ValueError(
            f"Expecting 's3' scheme, got: {parsed_url.scheme} in {url}.",
        )
    return parsed_url.netloc, parsed_url.path.lstrip("/")


class S3Client:
    def __init__(self) -> None:
        # Simple S3 client init; if you need custom credentials or region,
        # pass them directly via environment variables or create a custom session.
        self.s3 = boto3.client("s3")

    def download(self, s3_uri: str, target_dir: str | Path) -> str:
        """Download a file from S3 to a local directory.
        :param s3_uri: S3 URI (e.g. s3://bucket/key)
        :param target_dir: Local directory path
        :return: Local file path
        """
        bucket, key = parse_s3_url(s3_uri)
        filename = os.path.basename(s3_uri)
        path = os.path.join(target_dir, filename)
        self.s3.download_file(bucket, key, path)
        return path

    def upload(self, file_path: str, s3_uri: str) -> None:
        """Upload a local file to S3.
        :param file_path: Local file path
        :param s3_uri: S3 URI (e.g. s3://bucket/key)
        """
        bucket, key = parse_s3_url(s3_uri)
        self.s3.upload_file(file_path, bucket, key)

    def exists(self, s3_uri: str) -> bool:
        """Check if a file exists in S3 at the given URI.
        :param s3_uri: S3 URI
        :return: True if object exists, False otherwise.
        """
        bucket, key = parse_s3_url(s3_uri)
        try:
            self.s3.head_object(Bucket=bucket, Key=key)
            return True
        except self.s3.exceptions.ClientError:
            return False

    def walk(self, s3_uri: str):
        """Generator that walks all objects under the given S3 URI.
        Yields metadata dictionaries for each object.
        """
        bucket, key = parse_s3_url(s3_uri)
        paginator = self.s3.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=bucket, Prefix=key)
        for page in pages:
            for obj in page["Contents"]:
                yield {
                    "key": obj["Key"],
                    "size": obj["Size"],
                    "last_modified": obj["LastModified"],
                    "etag": obj["ETag"],
                    "storage_class": obj["StorageClass"],
                }

    def traverse(
        self,
        s3_uri: str,
        include_extensions=None,
        exclude_extensions=None,
        relative_unix=False,
        debug_print=True,
    ):
        """Traverse through an S3 "directory" and return entries under it.

        :param include_extensions: list of file extensions to include (e.g. ['.jpg', '.png']).
        :param exclude_extensions: list of file extensions to exclude (e.g. ['.txt', '.json']).
        :param relative_unix: return relative paths or full s3:// URIs.
        :param debug_print: whether to show a tqdm progress bar.
        :return: list of keys or URIs.
        """
        bucket, prefix = parse_s3_url(s3_uri)

        if not prefix.endswith("/"):
            prefix += "/"

        paginator = self.s3.get_paginator("list_objects_v2")
        response_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix, Delimiter="/")

        all_entries = []

        if debug_print:
            response_iterator = tqdm(response_iterator, desc="Traversing S3", unit="page")

        for page in response_iterator:
            # Subdirectories
            for d in page.get("CommonPrefixes", []):
                dir_key = d["Prefix"]
                dir_entry = dir_key if relative_unix else f"s3://{bucket}/{dir_key}"
                all_entries.append(dir_entry)

            # Files
            for obj in page.get("Contents", []):
                file_key = obj["Key"]
                if file_key == prefix:
                    continue  # skip the directory itself

                # Check include/exclude
                if (include_extensions is None or any(file_key.endswith(ext) for ext in include_extensions)) and (
                    exclude_extensions is None or not any(file_key.endswith(ext) for ext in exclude_extensions)
                ):
                    file_entry = file_key[len(prefix) :] if relative_unix else f"s3://{bucket}/{file_key}"
                    all_entries.append(file_entry)

        return all_entries

    def generate_presigned_uri(self, s3_uri: str, expiration: int = 604800) -> str:
        """Generate a presigned URL from a given S3 URI with a default expiration of 7 days.

        :param s3_uri: S3 URI (e.g., 's3://bucket-name/object-key')
        :param expiration: Time in seconds for the presigned URL to remain valid (default 7 days).
        :return: Presigned URL as a string. If error, returns None.
        """
        bucket, key = parse_s3_url(s3_uri)

        # Constrain expiration to AWS max if needed.
        expiration = min(expiration, 604800)

        try:
            response = self.s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket, "Key": key},
                ExpiresIn=expiration,
            )
            return response
        except ClientError as e:
            logging.exception(f"Failed to generate presigned URL for {s3_uri}: {e}")
            return None


if __name__ == "__main__":
    client = S3Client()
    s3_uri = "s3://dataset-ingested/gallery-dl/_todo_lists/"
    res = client.traverse(s3_uri)
    print(res)
    print("Done.")
