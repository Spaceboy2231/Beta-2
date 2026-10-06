from pyrogram import filters
from pyromod import Client
from pyrogram.types import Message
from utilsdf.db import Database
from re import findall
from utilsdf.vars import PREFIXES
from main import CHANNEL_LOGS


OWNER_ID = 5320997298

FORMAT_CMD = "<b>Formato: <code>/set_rol seller|admin USER_ID</code></b>"


@Client.on_message(filters.command("set_rol", PREFIXES))
async def rol(client: Client, m: Message):
    user_id = m.from_user.id

    with Database() as db:

        # Verificar que quien ejecuta el comando sea administrador
        if not db.is_admin(user_id):
            return

        data = str(m.text[len(m.command[0]) + 2:].strip())
        data_split = data.split(" ")

        # Verificar formato
        if len(data_split) <= 1 or data_split[0].lower() not in ["seller", "admin"]:
            return await m.reply(FORMAT_CMD, quote=True)

        rank = data_split[0].lower()

        # Obtener ID
        data = findall(r"\d+", data)

        if len(data) != 1:
            return await m.reply(FORMAT_CMD, quote=True)

        target_id = int(data[0])

        # =========================================================
        # 🔒 PROTECCIÓN DEL PROPIETARIO
        # =========================================================
        if target_id == OWNER_ID:
            return await m.reply(
                "<b>❌ El propietario está protegido y no puede ser modificado.</b>",
                quote=True
            )

        # =========================================================
        # 👑 SOLO EL PROPIETARIO PUEDE CREAR OTROS ADMINS
        # =========================================================
        if rank == "admin" and user_id != OWNER_ID:
            return await m.reply(
                "<b>❌ Solo el propietario puede asignar el rango Admin.</b>",
                quote=True
            )

        result = None

        # =========================================================
        # ASIGNAR SELLER
        # =========================================================
        if rank == "seller":
            result = db.promote_to_seller(str(target_id))

        # =========================================================
        # ASIGNAR ADMIN
        # =========================================================
        elif rank == "admin":
            result = db.promote_to_admin(str(target_id))

        # =========================================================
        # VERIFICAR SI EXISTE EL USUARIO
        # =========================================================
        if result is None:
            return await m.reply(
                "<b>La ID no se encuentra en la base de datos!\n"
                "Pidele al usuario que hable con el bot!</b>",
                quote=True
            )

        # =========================================================
        # CONFIRMACIÓN
        # =========================================================
        await m.reply(
            f"""<b>
La ID <code>{target_id}</code> ha sido promovida a {rank.capitalize()}.
</b>""",
            quote=True
        )

        # =========================================================
        # LOG
        # =========================================================
        await client.send_message(
            CHANNEL_LOGS,
            f"""#new_user_rol

id -» <a href='tg://user?id={target_id}'>{target_id}</a>
rol -» <code>{rank.capitalize()}</code>
rol by -» <a href='tg://user?id={user_id}'>{m.from_user.first_name}</a>"""
        )
