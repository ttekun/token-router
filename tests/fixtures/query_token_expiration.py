import datetime


def build_session_payload(user):
    return {"user_id": user.id, "scope": "standard"}


def token_expiration_seconds(user):
    base_ttl = 900
    session_token_expires_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=base_ttl)
    return int(session_token_expires_at.timestamp())


def render_dashboard(user):
    return {"name": user.name}
