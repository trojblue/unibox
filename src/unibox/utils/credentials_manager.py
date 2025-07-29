#!/usr/bin/env python
"""Utility functions for execlib, including AWS and Hugging Face credential management."""

import hashlib
import os
import shutil
import uuid
from pathlib import Path


def get_machine_hash(salt: str = "some_random_salt") -> str:
    machine_id = uuid.getnode()
    return hashlib.sha256(f"{machine_id}{salt}".encode()).hexdigest()


def get_hidden_base_dir() -> Path:
    return Path.home() / f".{get_machine_hash()}"


class CredentialManager:
    def __init__(self):
        self.hidden_base = get_hidden_base_dir()

        self.aws_dir = Path.home() / ".aws"
        self.hidden_aws_dir = self.hidden_base / ".aws"

        self.hf_dir = Path.home() / ".cache" / "huggingface"
        self.hidden_hf_dir = self.hidden_base / ".huggingface"

    def _hide_directory(self, src: Path, dst: Path, label: str) -> bool:
        if not src.exists() or not any(src.iterdir()):
            print(f"{label} directory is empty or does not exist: {src}")
            return False

        try:
            if dst.exists():
                shutil.rmtree(dst)
            print(f"Moving {label} from {str(src)[:5]}... to {str(dst)[:5]}...")
            shutil.copytree(src, dst)
            shutil.rmtree(src)
            print(f"{label} successfully hidden")
            return True
        except Exception as e:
            print(f"Error hiding {label}: {e}")
            return False

    def hide(self, service: str) -> bool:
        service = service.lower()
        if service == "aws":
            return self._hide_directory(self.aws_dir, self.hidden_aws_dir, "AWS")
        if service in ["hf", "huggingface"]:
            return self._hide_directory(self.hf_dir, self.hidden_hf_dir, "Hugging Face")
        print(f"Unknown service: {service}")
        return False

    def apply_aws(self) -> None:
        if not self.hidden_aws_dir.exists():
            self.hide("aws")

        credentials_file = self.hidden_aws_dir / "credentials"
        config_file = self.hidden_aws_dir / "config"

        if not credentials_file.exists():
            print(f"AWS credentials file not found: {credentials_file}")
            return

        os.environ["AWS_SHARED_CREDENTIALS_FILE"] = str(credentials_file)
        os.environ["AWS_CONFIG_FILE"] = str(config_file)

        try:
            import boto3

            session = boto3.Session(profile_name="default")
            creds = session.get_credentials()

            os.environ["AWS_ACCESS_KEY_ID"] = creds.access_key
            os.environ["AWS_SECRET_ACCESS_KEY"] = creds.secret_key
            if hasattr(creds, "token") and creds.token:
                os.environ["AWS_SESSION_TOKEN"] = creds.token
            if session.region_name:
                os.environ["AWS_DEFAULT_REGION"] = session.region_name

            print(f"AWS credentials applied.    Access Key: [........{creds.access_key[-3:]}]")
        except Exception as e:
            print(f"Error applying AWS credentials: {e}")

    def apply_hf(self) -> None:
        if not self.hidden_hf_dir.exists():
            self.hide("hf")

        token_file = self.hidden_hf_dir / "token"
        if not token_file.exists():
            print(f"Hugging Face token file not found: {token_file}")
            return

        with token_file.open("r") as f:
            token = f.read().strip()
            os.environ["HF_TOKEN"] = token
            print(f"Hugging Face token applied. Token:      [........{token[-3:]}]")

    def apply_credentials(self, *services: str) -> None:
        for service in services:
            service = service.lower()
            if service == "aws":
                self.apply_aws()
            elif service in ["hf", "huggingface"]:
                self.apply_hf()
            else:
                print(f"Unsupported service: {service}")


def apply_credentials(*services: str) -> None:
    """Apply credentials for the specified services."""
    manager = CredentialManager()
    manager.apply_credentials(*services)


# Example usage:
# manager = CredentialManager()
# manager.apply_credentials("aws", "hf")
