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


def create_wishlist_record(fields):
    app_token = _get_env("FEISHU_BITABLE_APP_TOKEN")
    table_id = _get_env("FEISHU_BITABLE_TABLE_ID")
    if not app_token or not table_id:
        return False, "missing_bitable_config"

    token, error = _get_tenant_access_token()
    if error:
        return False, error

    url = "https://open.feishu.cn/open-apis/bitable/v1/apps/{}/tables/{}/records".format(
        app_token, table_id
    )
    try:
        resp = requests.post(
            url,
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
