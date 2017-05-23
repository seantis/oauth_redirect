import asyncio

from datetime import datetime


async def start_tasks(app):
    app['remove_expired_tokens'] = app.loop.create_task(
        remove_expired_tokens(app))


async def cleanup_tasks(app):
    app['remove_expired_tokens'].cancel()
    await app['remove_expired_tokens']


async def remove_expired_tokens(app, periodicity=1.0):
    """ Regularly removes expired tokens from the database.

    Runs often because other code does not bother to check the validity
    of the token.

    """

    while True:
        horizon = datetime.utcnow()
        keys = []

        for key, token_bound in app.db.items():
            if token_bound['expiration'] < horizon:
                keys.append(key)

        for key in keys:
            del app.db[key]

        try:
            await asyncio.sleep(1.0)
        except asyncio.CancelledError:
            break
