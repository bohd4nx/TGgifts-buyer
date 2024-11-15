from datetime import datetime

from pyrogram import Client
from pyrogram.errors.exceptions import RPCError
from pytz.tzinfo import BaseTzInfo

import config


def current_datetime(timezone: BaseTzInfo) -> str:
    return datetime.now().astimezone(timezone).strftime("%d/%m/%y at %H:%M:%S")


async def buyer(app: Client, chat_id: int, star_gift_id: int, hide_my_name: bool = config.HIDE_SENDER_NAME) -> None:
    from src.notifications import notifications
    try:
        user = await app.get_chat(chat_id)
        username = user.username if user.username else ""

        num = config.NUM_GIFTS
        for _ in range(num):
            await app.send_star_gift(
                chat_id=chat_id,
                star_gift_id=star_gift_id,
                hide_my_name=hide_my_name
            )

        print(
            f"\n\033[93m[ ★ ]\033[0m - {f'{num} ' if num > 1 else ''}Gift{'s' if num > 1 else ''}: "
            f"\033[1m{star_gift_id}\033[0m successfully sent to \033[1m{chat_id}\033[0m"
            + (f" | @{username}\033[0m" if username else "")
            + "\n"
        )

        await notifications(app, star_gift_id, user_id=chat_id, username=username)

    except RPCError as ex:
        error_message = f"<pre>{str(ex)}</pre>"
        if 'BALANCE_TOO_LOW' in str(ex) or '400 BALANCE_TOO_LOW' in str(ex):
            print(f"\n\033[91m[ ERROR ]\033[0m Insufficient stars balance to send gift!\n")
            await notifications(app, star_gift_id, balance_error=True)
        elif 'STARGIFT_USAGE_LIMITED' in str(ex):
            print(f"\033[91m[ ERROR ]\033[0m Limited gift: {star_gift_id}) Out of Stock.\n")
            await notifications(app, star_gift_id, USAGE_LIMITED=True)
            expired_gift_ids.add(star_gift_id)
            raise
        else:
            print(
                f"\n\033[91m[ ERROR ]\033[0m Failed to send gift: \033[1m{star_gift_id}\033[0m to user: \033[1m{chat_id}\033[0m\n{str(ex)}\n"
            )
        await notifications(
            app,
            star_gift_id,
            error_message=error_message
        )
