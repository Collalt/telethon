import asyncio
import os
import threading
import configparser

from telethon import TelegramClient, events

config = configparser.ConfigParser()
config.read("config.ini")

api_id = config["Default"]["api_id"]
api_hash = str(config["Default"]["api_hash"])
sessions_dir = os.getcwd()
target_name = config["Default"]["target"]
proxy = ("socks5", config["Default"]["proxy_ip"], int(config["Default"]["proxy_port"]))

f = open('data.txt', 'a')

if sessions_dir == '':
    sessions_dir = os.getcwd()


files_count = len([f for f in os.listdir(sessions_dir)
if f.endswith('.session') and os.path.isfile(os.path.join(sessions_dir, f))])

print(f"Найдено файлов сессии: {files_count}")


async def thread_func(session):
    loop = asyncio.get_event_loop()
    client = TelegramClient(session, api_id, api_hash, loop=loop, proxy=proxy)

    # wait until get message then save message text and disconnect
    @client.on(events.NewMessage(chats=target_name, incoming=True, pattern='Рады видеть вас в TopStore!'))
    async def handler(event):
        await event.message.click(share_phone=True)

    @client.on(events.NewMessage(chats=target_name, incoming=True, pattern='Вы успешно зарегистрировались!'))
    async def handler(event):
        msg = event.message.to_dict()['message']

        login = msg.split(" ")[12]
        password = msg.split(" ")[23]

        login = login.replace("*", "")
        login = login.replace("\n", "")
        password = password.replace("*", "")
        password = password.replace("\n", "")

        f.write(f"{login} {password}\n")
        f.flush()
        await client.disconnect()

    async with client:
        await client.send_message(target_name, '/start')
        await client.run_until_disconnected()


def create_event_loop(session):
    asyncio.run(thread_func(session))


threads = []
for file in os.listdir(sessions_dir):
    if file.endswith(".session"):
        session = os.path.join("sessions", file)
        t = threading.Thread(target=create_event_loop, args=[session])
        threads.append(t)

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

print("Готово! Данные сохранены в файле data.txt")

f.close()
