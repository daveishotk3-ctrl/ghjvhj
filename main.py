from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import secrets
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sketchy")

app = FastAPI(title="Sketchy Backend Clone")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DATA_FILE = Path("players.json")

def load():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return {"players": {}, "tokens": {}}

def save(data):
    DATA_FILE.write_text(json.dumps(data, indent=2))

db = load()

# ---------- Request models ----------
class LoginBody(BaseModel):
    deviceId: str
    metaId: Optional[str] = None
    metaProof: Optional[str] = None
    build: Optional[str] = None
    pkg: Optional[str] = None

class ProfileBody(BaseModel):
    name: Optional[str] = None
    colour: Optional[str] = None

class ItemBody(BaseModel):
    itemId: Optional[str] = None
    slot: Optional[str] = None

class ReportBody(BaseModel):
    targetId: int
    reason: str = ""

# Expanded shop
SHOP = [
    {"id": "PartyHat", "name": "Party Hat", "slot": "Head", "price": 150, "enabled": True},
    {"id": "PropellerHat", "name": "Propeller Hat", "slot": "Head", "price": 250, "enabled": True},
    {"id": "TopHat", "name": "Top Hat", "slot": "Head", "price": 300, "enabled": True},
    {"id": "CowboyHat", "name": "Cowboy Hat", "slot": "Head", "price": 350, "enabled": True},
    {"id": "Headphones", "name": "Headphones", "slot": "Head", "price": 400, "enabled": True},
    {"id": "PaperBag", "name": "Paper Bag", "slot": "Head", "price": 200, "enabled": True},
    {"id": "Pumpkin", "name": "Pumpkin Head", "slot": "Head", "price": 500, "enabled": True},
    {"id": "Crown", "name": "Crown", "slot": "Head", "price": 1000, "enabled": True},
    {"id": "Ushanka", "name": "Ushanka", "slot": "Head", "price": 400, "enabled": True},
    {"id": "WitchHat", "name": "Witch Hat", "slot": "Head", "price": 400, "enabled": True},
    {"id": "SantaHat", "name": "Santa Hat", "slot": "Head", "price": 400, "enabled": True},
    {"id": "BunnyEars", "name": "Bunny Ears", "slot": "Head", "price": 350, "enabled": True},
    {"id": "Glasses", "name": "Glasses", "slot": "Face", "price": 150, "enabled": True},
    {"id": "Sunglasses", "name": "Sunglasses", "slot": "Face", "price": 200, "enabled": True},
    {"id": "Monocle", "name": "Monocle", "slot": "Face", "price": 250, "enabled": True},
    {"id": "Moustache", "name": "Moustache", "slot": "Face", "price": 120, "enabled": True},
    {"id": "SkullMask", "name": "Skull Mask", "slot": "Face", "price": 450, "enabled": True},
    {"id": "HeartGlasses", "name": "Heart Glasses", "slot": "Face", "price": 250, "enabled": True},
    {"id": "BowTie", "name": "Bow Tie", "slot": "Body", "price": 180, "enabled": True},
    {"id": "Scarf", "name": "Scarf", "slot": "Body", "price": 250, "enabled": True},
    {"id": "Cape", "name": "Cape", "slot": "Body", "price": 600, "enabled": True},
    {"id": "Lollipop", "name": "Lollipop", "slot": "Hand", "price": 100, "enabled": True},
    {"id": "IceCream", "name": "Ice Cream", "slot": "Hand", "price": 120, "enabled": True},
    {"id": "CandyCane", "name": "Candy Cane", "slot": "Hand", "price": 120, "enabled": True},
    {"id": "CandyBar", "name": "Candy Bar", "slot": "Hand", "price": 100, "enabled": True},
    {"id": "BaseballBat", "name": "Baseball Bat", "slot": "Hand", "price": 350, "enabled": True},
    {"id": "Crowbar", "name": "Crowbar", "slot": "Hand", "price": 400, "enabled": True},
    {"id": "RedBand", "name": "Red Wristband", "slot": "LeftHand", "price": 100, "enabled": True},
    {"id": "BlueBand", "name": "Blue Wristband", "slot": "RightHand", "price": 100, "enabled": True},
    {"id": "PageShrink", "name": "Shrink Ray Page", "slot": "Page", "price": 300, "enabled": True},
    {"id": "PageGrow", "name": "Grow Ray Page", "slot": "Page", "price": 300, "enabled": True},
    {"id": "PageAllVision", "name": "All Vision Page", "slot": "Page", "price": 350, "enabled": True},
    {"id": "PageBlind", "name": "Blindness Page", "slot": "Page", "price": 400, "enabled": True},
    {"id": "PageBomb", "name": "Bomb Page", "slot": "Page", "price": 450, "enabled": True},
    {"id": "PageInvisible", "name": "Invisibility Page", "slot": "Page", "price": 500, "enabled": True},
    {"id": "PageSkelly", "name": "Skelly Summon Page", "slot": "Page", "price": 500, "enabled": True},
    {"id": "PageInvincible", "name": "Invincibility Page", "slot": "Page", "price": 600, "enabled": True},
    {"id": "PageShrinkPotion", "name": "Shrink Potion Page", "slot": "Page", "price": 250, "enabled": True},
    {"id": "PageGrowPotion", "name": "Growth Potion Page", "slot": "Page", "price": 250, "enabled": True},
    {"id": "PageShield", "name": "Shield Page", "slot": "Page", "price": 300, "enabled": True},
    {"id": "PageBush", "name": "Bush Potion Page", "slot": "Page", "price": 300, "enabled": True},
    {"id": "PageSnare", "name": "Snare Page", "slot": "Page", "price": 350, "enabled": True},
    {"id": "PageSpeed", "name": "Speed Boost Page", "slot": "Page", "price": 350, "enabled": True},
    {"id": "PageCharge", "name": "Charge Page", "slot": "Page", "price": 350, "enabled": True},
    {"id": "PageTendrils", "name": "Tendrils Page", "slot": "Page", "price": 400, "enabled": True},
    {"id": "PagePaperLegs", "name": "Paper Legs Page", "slot": "Page", "price": 400, "enabled": True},
    {"id": "PageFlashbang", "name": "Flashbang Page", "slot": "Page", "price": 400, "enabled": True},
    {"id": "PageWebSling", "name": "Web Sling Page", "slot": "Page", "price": 450, "enabled": True},
    {"id": "PageRobo", "name": "Robo Summon Page", "slot": "Page", "price": 500, "enabled": True},
]

def get_player(auth: Optional[str]):
    if not auth or not auth.startswith("Bearer "):
        return None
    token = auth[7:]
    pid = db["tokens"].get(token)
    if pid is None:
        return None
    return db["players"].get(str(pid))

def make_reply(p: dict, token: str = None) -> dict:
    owned_info = []
    for item_id in p.get("owned", []):
        for shop_item in SHOP:
            if shop_item["id"] == item_id:
                owned_info.append(shop_item)
                break

    reply = {
        "playerId": p["playerId"],
        "name": p["name"],
        "colour": p["colour"],
        "coins": p["coins"],
        "owned": p.get("owned", []),
        "ownedInfo": owned_info,
        "equipped": p.get("equipped", []),
        "tutorialDone": p.get("tutorialDone", False),
        "bundleTimed": True,
        "bundleLeft": 999999,
        "discordLinked": False,
        "isNew": p.get("isNew", False),
        "dailyReward": p.get("dailyReward", 0),
        "streak": p.get("streak", 1),
        "streakBonus": 0,
        "streakNext": 25,
        "photonAuth": False,
        "photonApp": "",
        "photonVoice": "",
        "challenges": [],
        "resetsIn": 0,
        "weekResetsIn": 0,
        "earned": 0,
    }
    if token:
        reply["token"] = token
    return reply

@app.get("/health")
def health():
    return {"ok": True, "storage": "clone"}

@app.post("/api/login")
async def login(body: LoginBody):
    logger.info(f"LOGIN deviceId={body.deviceId[:20]}...")
    if len(body.deviceId) < 16:
        raise HTTPException(400, detail="deviceId missing")

    player = None
    for p in db["players"].values():
        if p.get("deviceId") == body.deviceId:
            player = p
            break

    if player is None:
        new_id = max([int(k) for k in db["players"]] + [100]) + 1
        player = {
            "playerId": new_id,
            "deviceId": body.deviceId,
            "name": "ERROR Functi0n",
            "colour": "999",
            "coins": 99999,
            "owned": [],
            "equipped": [
                {"slot": "Head", "item": ""},
                {"slot": "Face", "item": ""},
                {"slot": "Body", "item": ""},
                {"slot": "LeftHand", "item": ""},
                {"slot": "RightHand", "item": ""},
                {"slot": "Badge", "item": ""},
            ],
            "tutorialDone": False,
            "isNew": True,
            "dailyReward": 250,
            "streak": 1,
        }
        db["players"][str(new_id)] = player
        logger.info(f"Created new player {new_id}")
    else:
        player["isNew"] = False
        player["dailyReward"] = 0

    token = secrets.token_urlsafe(32)
    db["tokens"][token] = player["playerId"]
    save(db)
    return make_reply(player, token)

@app.get("/api/me")
async def me(authorization: Optional[str] = Header(None)):
    p = get_player(authorization)
    if not p:
        raise HTTPException(401, detail="not logged in")
    return make_reply(p)

@app.get("/api/shop")
async def shop():
    return {"items": SHOP}

@app.post("/api/profile")
async def profile(body: ProfileBody, authorization: Optional[str] = Header(None)):
    p = get_player(authorization)
    if not p:
        raise HTTPException(401, detail="not logged in")
    if body.name is not None:
        p["name"] = body.name
    if body.colour is not None:
        p["colour"] = body.colour
    save(db)
    return make_reply(p)

@app.post("/api/buy")
async def buy(request: Request, authorization: Optional[str] = Header(None)):
    raw = await request.body()
    logger.info(f"BUY raw body: {raw}")

    try:
        data = json.loads(raw) if raw else {}
    except:
        data = {}

    item_id = data.get("itemId") or data.get("id")
    logger.info(f"BUY itemId={item_id}")

    p = get_player(authorization)
    if not p:
        raise HTTPException(401, detail="not logged in")

    if not item_id:
        raise HTTPException(400, detail="itemId missing")

    item = next((i for i in SHOP if i["id"] == item_id), None)
    if not item:
        logger.warning(f"Unknown item {item_id}, giving it anyway")
        if item_id not in p["owned"]:
            p["owned"].append(item_id)
            save(db)
        return make_reply(p)

    if item_id in p["owned"]:
        logger.info(f"Already owned {item_id}")
        return make_reply(p)

    if p["coins"] < item["price"]:
        raise HTTPException(400, detail="not enough coins")

    p["coins"] -= item["price"]
    p["owned"].append(item_id)
    save(db)
    logger.info(f"Bought {item_id}, coins left: {p['coins']}, owned: {p['owned']}")
    return make_reply(p)

@app.post("/api/equip")
async def equip(request: Request, authorization: Optional[str] = Header(None)):
    raw = await request.body()
    logger.info(f"EQUIP raw body: {raw}")

    try:
        data = json.loads(raw) if raw else {}
    except:
        data = {}

    item_id = data.get("itemId") or ""
    slot = data.get("slot") or "Head"

    p = get_player(authorization)
    if not p:
        raise HTTPException(401, detail="not logged in")

    found = False
    for eq in p["equipped"]:
        if eq["slot"] == slot:
            eq["item"] = item_id
            found = True
            break
    if not found:
        p["equipped"].append({"slot": slot, "item": item_id})

    save(db)
    logger.info(f"Equipped {item_id} on {slot}")
    return make_reply(p)

@app.post("/api/claim")
async def claim(request: Request, authorization: Optional[str] = Header(None)):
    return await buy(request, authorization)

@app.post("/api/tutorial")
async def tutorial(authorization: Optional[str] = Header(None)):
    p = get_player(authorization)
    if not p:
        raise HTTPException(401, detail="not logged in")
    p["tutorialDone"] = True
    save(db)
    return make_reply(p)

@app.post("/api/report")
async def report(body: ReportBody, authorization: Optional[str] = Header(None)):
    p = get_player(authorization)
    if not p:
        raise HTTPException(401, detail="not logged in")
    return {"ok": True}

@app.post("/api/round")
@app.post("/api/tag")
@app.post("/api/pickup")
@app.post("/api/room")
@app.post("/api/linkcode")
async def generic_ok(authorization: Optional[str] = Header(None)):
    p = get_player(authorization)
    if not p:
        raise HTTPException(401, detail="not logged in")
    return {"ok": True}

@app.get("/api/challenges")
async def challenges(authorization: Optional[str] = Header(None)):
    p = get_player(authorization)
    if not p:
        raise HTTPException(401, detail="not logged in")
    return {
        "challenges": [],
        "resetsIn": 86400,
        "weekResetsIn": 604800,
        "streak": p.get("streak", 1),
        "streakNext": 25,
    }

@app.post("/api/challenge")
async def claim_challenge(authorization: Optional[str] = Header(None)):
    p = get_player(authorization)
    if not p:
        raise HTTPException(401, detail="not logged in")
    return make_reply(p)

@app.get("/")
async def root():
    return {"message": "Sketchy Backend Clone is running", "players": len(db["players"])}
