import hashlib
import secrets

from django.utils import timezone

from .models import ApiKey


def generate_key():
    prefix = "mem_"+ secrets.token_hex(4)
    secret = secrets.token_urlsafe(32)
    full_key = f"{prefix}_{secret}"
    return full_key, prefix

def hash_key(full_key):
    return hashlib.sha256(full_key.encode('utf-8')).hexdigest()

def create_api_key(project, created_by, name, can_read, can_write, can_delete, expires_at=None):
    full_key, prefix = generate_key()
    api_key = ApiKey.objects.create(project=project, created_by=created_by, name=name,
                                    prefix=prefix, key_hash=hash_key(full_key),
                                    can_read=can_read, can_write=can_write,
                                    can_delete=can_delete, expires_at=expires_at)
    return api_key, full_key

def revoke_api_key(api_key):
    if api_key.revoked_at is not None: 
        return api_key
    api_key.revoked_at = timezone.now()
    api_key.save(update_fields=['revoked_at'])
    return api_key

def find_valid_key(full_key):
    hashed_key = hash_key(full_key)
    key = ApiKey.objects.filter(key_hash=hashed_key).first()
    if key is None or key.revoked_at is not None:
        return None
    if key.expires_at is not None and key.expires_at <= timezone.now():
        return None
    key.last_used_at = timezone.now()
    key.save(update_fields=["last_used_at"])
    return key