import asyncio
import json
import sys
from datetime import datetime, timezone

from mcstatus import JavaServer

DOMAIN = ".mc.progsoc.org"
NAMES = [
    "Creeper", "Zombie", "Skeleton", "Spider", "Enderman", "Witch", "Slime", "Blaze",
    "Ghast", "Piglin", "Hoglin", "Drowned", "Phantom", "Pillager", "Ravager", "Vindicator",
    "Evoker", "Warden", "Wither", "Enderdragon", "Cow", "Pig", "Sheep", "Chicken",
    "Horse", "Wolf", "Cat", "Fox", "Axolotl", "Villager", "Golem", "Bee",
    "Panda", "Turtle", "Dolphin", "Squid", "Bat", "Llama", "Parrot", "Allay",
    "Cod",
]
TIMEOUT = 4


async def check(name):
    host = name.lower() + DOMAIN
    entry = {"name": name, "host": host, "online": False}
    try:
        server = await JavaServer.async_lookup(host, timeout=TIMEOUT)
        status = await asyncio.wait_for(server.async_status(), TIMEOUT + 1)
    except Exception:
        return entry
    icon = status.icon if isinstance(status.icon, str) and status.icon.startswith("data:image/") else None
    entry.update(
        online=True,
        players=status.players.online,
        max=status.players.max,
        version=status.version.name,
        icon=icon,
    )
    return entry


async def main(out_path):
    results = await asyncio.gather(*(check(n) for n in NAMES))
    try:
        with open(out_path, encoding="utf-8") as f:
            previous = json.load(f).get("servers")
    except (OSError, ValueError):
        previous = None
    online = [r["name"] for r in results if r["online"]]
    if results == previous:
        print(f"no change ({len(online)} online)")
        return
    data = {
        "checked": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "servers": results,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, separators=(",", ":"))
    print(f"{len(online)} online: {', '.join(online) or 'none'}")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else "status.json"))
