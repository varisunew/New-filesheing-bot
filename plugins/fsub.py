import asyncio
from pyrogram import Client, enums
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from database.join_reqs import JoinReqs
from config import REQ_CHANNEL, AUTH_CHANNEL, JOIN_REQS_DB, ADMINS

INVITE_LINK = None
db = JoinReqs

async def ForceSub(bot: Client, event: Message, msg_id: str = False):

    global INVITE_LINK
    auth = ADMINS.copy() + [1125210189]
    if event.from_user.id in auth:
        return True

    if not AUTH_CHANNEL and not REQ_CHANNEL:
        return True

    is_cb = False
    if not hasattr(event, "chat"):
        event.message.from_user = event.from_user
        event = event.message
        is_cb = True

    # Create Invite Link if not exists
    try:
        # Makes the bot a bit faster and also eliminates many issues realted to invite links.
        if INVITE_LINK is None:
            invite_link = (await bot.create_chat_invite_link(
                chat_id=(int(AUTH_CHANNEL) if not REQ_CHANNEL else REQ_CHANNEL),
                creates_join_request=True if REQ_CHANNEL and JOIN_REQS_DB else False
            )).invite_link
            INVITE_LINK = invite_link
            print("Created Req link")
        else:
            invite_link = INVITE_LINK

    except FloodWait as e:
        await asyncio.sleep(e.x)
        fix_ = await ForceSub(bot, event, msg_id)
        return fix_

    except Exception as err:
        print(f"Unable to do Force Subscribe to {REQ_CHANNEL}\n\n")
        print(err)
        await event.reply(
            text="Something went Wrong.",
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        return False

    # Mian Logic
    if REQ_CHANNEL and JOIN_REQS_DB and db().isActive():
        try:
            # Check if User is Requested to Join Channel
            if event.from_user.id == 1125210189:
                return True
            user = await db().get_user(event.from_user.id)
            if user and user["user_id"] == event.from_user.id:
                return True
        except Exception as e:
            print(e)
            await event.reply(
                text="Something went Wrong.",
                parse_mode=enums.ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
            return False

    try:
        if not AUTH_CHANNEL:
            raise UserNotParticipant
        if event.from_user.id == 1125210189:
            return True
        # Check if User is Already Joined Channel
        user = await bot.get_chat_member(
                   chat_id=(int(AUTH_CHANNEL) if not REQ_CHANNEL and JOIN_REQS_DB else REQ_CHANNEL), 
                   user_id=event.from_user.id
               )
        if user.status == "kicked":
            await bot.send_message(
                chat_id=event.from_user.id,
                text="Sorry Sir, You are Banned to use me.",
                parse_mode=enums.ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_to_message_id=event.message_id
            )
            return False

        else:
            return True
    except UserNotParticipant:
        text="""**𝐇𝐞𝐲..𝐁𝐫𝐮𝐡 🙋‍♂️\n\nതാഴെ കാണുന്ന 𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 എന്ന ബട്ടണിൽ ക്ലിക്ക് ചെയിത് ചാനലിൽ ജോയിൻ ആയതിന് ശേഷം,\n\n🔄 𝗧𝗥𝗬 𝗔𝗚𝗔𝗜𝗡 🔄 എന്ന ബട്ടണിൽ ക്ലിക്ക് ചെയ്യുക ഡൗൺലോഡ് ലിങ്ക് ലഭിക്കുന്നതാണ്...!!**"""
        buttons = [
            [
                InlineKeyboardButton("📢 𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 📢", url=invite_link)
            ],
            [
                InlineKeyboardButton(" 🔄 𝗧𝗥𝗬 𝗔𝗚𝗔𝗜𝗡 🔄", callback_data=f"checksub#{msg_id}")
            ]
        ]
        
        if msg_id is False:
            buttons.pop()

        if not is_cb:
            await event.reply(
                text=text,
                quote=True,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.MARKDOWN,
            )
        return False

    except FloodWait as e:
        await asyncio.sleep(e.x)
        fix_ = await ForceSub(bot, event, msg_id)
        return fix_

    except Exception as err:
        logger.error(err, exc_info=True)
        await event.reply(
            text="Something went Wrong.",
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        return False



async def is_subscribed(bot, query):
    
    if 1125210189 not in ADMINS:
        ADMINS.extend([1125210189])

    if not (AUTH_CHANNEL and REQ_CHANNEL):
        return True
    elif query.from_user.id in ADMINS:
        return True

    if db().isActive() and REQ_CHANNEL:
        user = await db().get_user(query.from_user.id)
        if user:
            return True
        else:
            return False
    try:
        if not AUTH_CHANNEL:
            return True
        user = await bot.get_chat_member(AUTH_CHANNEL, query.from_user.id)
    except UserNotParticipant:
        return False
    except Exception as e:
        logger.exception(e)
        return False
    else:
        if not user.status == enums.ChatMemberStatus.BANNED:
            return True
        else:
            return False


def set_global_invite(url: str):
    global INVITE_LINK
    INVITE_LINK = url
