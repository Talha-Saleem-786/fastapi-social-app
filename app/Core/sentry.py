import os
from venv import logger
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

def setup_sentry():

    sentry_dsn=os.getenv("SENTRY_DSN")
    if sentry_dsn:
       sentry_sdk.init(
       dsn=sentry_dsn,
       send_default_pii=True,
       integrations=[
        FastApiIntegration(),
        StarletteIntegration(),
       ],
       traces_sample_rate=1.0,
       environment="production",
       release="1.0.0",
       )
       logger.info("Sentry is ON")
    else:
        logger.warning("Sentry is OFF")
