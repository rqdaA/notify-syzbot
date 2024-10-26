import requests
import discord
import os
import re
from dotenv import load_dotenv

load_dotenv()

CHANNEL=int(os.getenv("CHANNEL",'0'))
TOKEN=os.getenv("TOKEN",'')
ROOT='https://syzkaller.appspot.com'
SAVE_PATH='/workdir/notified_syzbot.txt'

def send_msg(msg: discord.Embed):
    client = discord.Client(intents=discord.Intents.default())

    @client.event
    async def on_ready():
        await client.get_channel(CHANNEL).send(embed=msg)
        await client.close()

    client.run(TOKEN)

def main():
    with open(SAVE_PATH, 'r') as f:
        last_notified = f.read()
    r = requests.get(f'{ROOT}/upstream')
    buf = r.text[r.text.find('<caption id="open"'):]
    first = True
    for t in buf.split('<tr>')[2:10]:
        t = t.replace('\n', '')
        m = re.search(r'class="title">\W*<a href="(.*?)">(.*?)<\/a>', t)
        tags = re.findall(r'class="bug-label"><a href=".*?">(.*?)<\/a><\/span>', t)
        if m is None or len(m.groups()) != 2:
            # print('url or title not found')
            continue
        if tags is None:
            # print('tags not found')
            continue
        for tag in tags:
            if tag.endswith('fs'):
                continue

        url, title = m.groups()
        url = f'{ROOT}/{url}'
        title = re.sub(r' \(\d+\)', '', title)
        if last_notified == title:
            break
        if first:
            with open(SAVE_PATH, 'w') as f:
                f.write(title.strip())
            first = False

        embed = discord.Embed(title=title, url=url)
        embed.add_field(name="Tags", value='\n'.join(tags), inline=False)
        send_msg(embed)

if __name__ == '__main__':
    main()
