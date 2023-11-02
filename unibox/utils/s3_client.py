import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial
from urllib.parse import urlparse

import boto3
from omegaconf import OmegaConf
from tqdm.auto import tqdm


def parse_s3_url(url: str):
    parsed_url = urlparse(url)
    if parsed_url.scheme != "s3":
        raise ValueError(
            "Expecting 's3' scheme, got: {} in {}.".format(parsed_url.scheme, url)
        )
    return parsed_url.netloc, parsed_url.path.lstrip("/")


def parse_config():
    # change config.yaml with "scripts/config.yaml"
    # if you want to run this script locally
    config = OmegaConf.load("config.yaml")
    return config


class S3Client:
    def __init__(self) -> None:
        # config = parse_config()
        self.s3 = boto3.client(
            "s3",
            # aws_access_key_id=config.aws_access_key_id,
            # aws_secret_access_key=config.aws_secret_access_key,
            # region_name=config.aws_region_name,
        )

    def download(self, s3_uri, target_dir):
        bucket, key = parse_s3_url(s3_uri)
        filename = os.path.basename(s3_uri)
        path = os.path.join(target_dir, filename)
        self.s3.download_file(bucket, key, path)
        return path

    def upload(self, file_path, s3_dir):
        filename = os.path.basename(file_path)
        s3_dir = os.path.join(s3_dir, filename)
        bucket, key = parse_s3_url(s3_dir)
        self.s3.upload_file(file_path, bucket, key)

    def download_parallel(self, s3_uri_list, target_dir):
        failed_downloads = []

        def download_one(target_dir, s3_uri):
            self.download(s3_uri, target_dir)

        func = partial(download_one, target_dir)
        with tqdm(desc="Downloading images from S3", total=len(s3_uri_list)) as bar:
            with ThreadPoolExecutor(max_workers=32) as executor:
                # Using a dict for preserving the downloaded file for each future,
                # to store it as a failure if we need that
                futures = {
                    executor.submit(func, file_to_download): file_to_download
                    for file_to_download in s3_uri_list
                }
                for future in as_completed(futures):
                    if future.exception():
                        failed_downloads.append(futures[future])
                    bar.update(1)

        return failed_downloads

    def upload_parallel(self, file_list, target_s3_uri):
        failed_uploads = []

        def upload_one(s3_uri, file_path):
            self.upload(file_path, s3_uri)

        func = partial(upload_one, target_s3_uri)
        with tqdm(desc="Uploading images to S3", total=len(file_list)) as bar:
            with ThreadPoolExecutor(max_workers=32) as executor:
                futures = {
                    executor.submit(func, file_to_upload): file_to_upload
                    for file_to_upload in file_list
                }
                for future in as_completed(futures):
                    if future.exception():
                        failed_uploads.append(futures[future])
                    bar.update(1)

        return failed_uploads

    def walk(self, dir):
        bucket, key = parse_s3_url(dir)
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