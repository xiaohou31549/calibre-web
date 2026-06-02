# -*- coding: utf-8 -*-

import os
import time
import requests

from .. import logger


log = logger.create()

_TOKEN_CACHE = {
    "token": None,
    "expires_at": 0,
}


def _get_env(name):
    value = os.environ.get(name, "").strip()
    return value if value else None


def _get_tenant_access_token():
    app_id = _get_env("FEISHU_APP_ID")
    app_secret = _get_env("FEISHU_APP_SECRET")
    if not app_id or not app_secret:
        return None, "missing_credentials"

    now = time.time()
    if _TOKEN_CACHE["token"] and now < (_TOKEN_CACHE["expires_at"] - 60):
        return _TOKEN_CACHE["token"], None

    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    try:
        resp = requests.post(
            url,
            json={"app_id": app_id, "app_secret": app_secret},
            timeout=10,
        )
    except requests.RequestException as exc:
        log.error("Feishu auth request failed: %r", exc)
        return None, "auth_request_failed"

    if resp.status_code != 200:
        log.error("Feishu auth failed: status=%s body=%s", resp.status_code, resp.text)
        return None, "auth_failed"

    data = resp.json()
    if data.get("code") != 0:
        log.error("Feishu auth error: %s", data)
        return None, "auth_failed"

    token = data.get("tenant_access_token")
    expires_in = data.get("expire") or data.get("expires_in") or 7200
    _TOKEN_CACHE["token"] = token
    _TOKEN_CACHE["expires_at"] = now + int(expires_in)
    return token, None


def _bitable_base_url():
    app_token = _get_env("FEISHU_BITABLE_APP_TOKEN")
    table_id = _get_env("FEISHU_BITABLE_TABLE_ID")
    if not app_token or not table_id:
        return None
    return "https://open.feishu.cn/open-apis/bitable/v1/apps/{}/tables/{}/records".format(
        app_token, table_id
    )


def create_wishlist_record(fields):
    base_url = _bitable_base_url()
    if not base_url:
        return False, "missing_bitable_config"

    token, error = _get_tenant_access_token()
    if error:
        return False, error

    try:
        resp = requests.post(
            base_url,
            headers={"Authorization": "Bearer {}".format(token)},
            json={"fields": fields},
            timeout=10,
        )
    except requests.RequestException as exc:
        log.error("Feishu record request failed: %r", exc)
        return False, "record_request_failed"

    if resp.status_code != 200:
        log.error("Feishu record failed: status=%s body=%s", resp.status_code, resp.text)
        return False, "record_failed"

    data = resp.json()
    if data.get("code") != 0:
        log.error("Feishu record error: %s", data)
        return False, "record_failed"

    return True, None


def list_wishlist_records(page_size=200):
    """Fetch wishlist records from the Feishu bitable.

    Returns (records, error). Each record is a dict with at least
    ``record_id`` and ``fields`` (the raw column values keyed by column name).
    """
    base_url = _bitable_base_url()
    if not base_url:
        return None, "missing_bitable_config"

    token, error = _get_tenant_access_token()
    if error:
        return None, error

    records = []
    page_token = None
    headers = {"Authorization": "Bearer {}".format(token)}
    # Page through all records so the admin sees the full wishlist.
    while True:
        params = {"page_size": page_size}
        if page_token:
            params["page_token"] = page_token
        try:
            resp = requests.get(base_url, headers=headers, params=params, timeout=10)
        except requests.RequestException as exc:
            log.error("Feishu list request failed: %r", exc)
            return None, "list_request_failed"

        if resp.status_code != 200:
            log.error("Feishu list failed: status=%s body=%s", resp.status_code, resp.text)
            return None, "list_failed"

        data = resp.json()
        if data.get("code") != 0:
            log.error("Feishu list error: %s", data)
            return None, "list_failed"

        payload = data.get("data") or {}
        for item in payload.get("items") or []:
            records.append({
                "record_id": item.get("record_id"),
                "fields": item.get("fields") or {},
            })

        if payload.get("has_more") and payload.get("page_token"):
            page_token = payload["page_token"]
        else:
            break

    return records, None


def update_wishlist_record(record_id, fields):
    """Update a single wishlist record's fields (e.g. mark it as notified)."""
    base_url = _bitable_base_url()
    if not base_url:
        return False, "missing_bitable_config"
    if not record_id:
        return False, "missing_record_id"

    token, error = _get_tenant_access_token()
    if error:
        return False, error

    url = "{}/{}".format(base_url, record_id)
    try:
        resp = requests.put(
            url,
            headers={"Authorization": "Bearer {}".format(token)},
            json={"fields": fields},
            timeout=10,
        )
    except requests.RequestException as exc:
        log.error("Feishu update request failed: %r", exc)
        return False, "update_request_failed"

    if resp.status_code != 200:
        log.error("Feishu update failed: status=%s body=%s", resp.status_code, resp.text)
        return False, "update_failed"

    data = resp.json()
    if data.get("code") != 0:
        log.error("Feishu update error: %s", data)
        return False, "update_failed"

    return True, None
