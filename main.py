from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import secrets
import json
from pathlib import Path

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

# ---------- Request models (exact match to client) ----------
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

# ---------- Shop (same structure as real backend) ----------
SHOP = [
    {"id": "PartyHat", "name": "Party Hat", "slot": "Head", "price": 150},
    {"id": "PropellerHat", "name": "Propeller Hat", "slot": "Head", "price": 250},
    {"id": "TopHat", "name": "Top Hat", "slot": "Head", "price": 300},
    {"id": "CowboyHat", "name": "Cowboy Hat", "slot": "Head", "price": 350},
    {"id": "Crown", "name": "Crown", "slot": "Head", "price": 1000},
    {"id": "Glasses", "name": "Glasses", "slot": "Face", "price": 150},
    {"id": "Sunglasses", "name": "Sunglasses", "slot": "Face", "price": 200},
    {"id": "Cape", "name": "Cape", "slot": "Body", "price": 600},
    {"id": "Lollipop", "name": "Lollipop", "slot": "Hand", "price": 100},
    {"id": "PageShrink", "name": "Shrink Ray Page", "slot": "Page", "price": 300},
    {"id": "PageInvisible", "name": "Invisibility Page", "slot": "Page", "price": 500},
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
    """Exact shape the client expects (BackendClient.Reply)"""
    reply = {
        "playerId": p["playerId"],
        "name": p["name"],
        "colour": p["colour"],
        "coins": p["coins"],
        "owned": p["owned"],
        "ownedInfo": [i for i in SHOP if i["id"] in p["owned"]],
        "equipped": p["equipped"],
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
    }
    if token:
        reply["token"] = token
    return reply

# ---------- Endpoints ----------

@app.get("/health")
def health():
    return {"ok": True, "storage": "clone"}

@app.post("/api/login")
def login(body: LoginBody):
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
            "name": "ERROR Functi0n",          # ← your requested name
            "colour": "999",                   # ← your requested colour
            "coins": 99999,                    # generous for testing
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
    else:
        player["isNew"] = False
        player["dailyReward"] = 0

    token = secrets.token_urlsafe(32)
    db["tokens"][token] = player["playerId"]
    save(db)
    return make_reply(player, token)

@app.get("/api/me")
def me(authorization: Optional[str] = Header(None)):
    p = get_player(authorization)
    if not p:
        raise HTTPException(401, detail="not logged in")
    return make_reply(p)

@app.get("/api/shop")
def shop():
    return {"items": SHOP}

@app.post("/api/profile")
def profile(body: ProfileBody, authorization: Optional[str] = Header(None)):
    p = get_player(authorization)
    if not p:
        raise HTTPException(401, detail="not logged in")
    if body.name is not None:
        p["name"] = body.name          # no sanitization
    if body.colour is not None:
        p["colour"] = body.colour
    save(db)
    return make_reply(p)

@app.post("/api/buy")
def buy(body: ItemBody, authorization: Optional[str] = Header(None)):
    p = get_player(authorization)
    if not p:
        raise HTTPException(401, detail="not logged in")
    item = next((i for i in SHOP if i["id"] == body.itemId), None)
    if not item:
        raise HTTPException(404, detail="no such item")
    if body.itemId not in p["owned"]:
        if p["coins"] < item["price"]:
            raise HTTPException(400, detail="not enough coins")
        p["coins"] -= item["price"]
        p["owned"].append(body.itemId)
        save(db)
    return make_reply(p)

@app.post("/api/equip")
def equip(body: ItemBody, authorization: Optional[str] = Header(None)):
    p = get_player(authorization)
    if not p:
        raise HTTPException(401, detail="not logged in")
    slot = body.slot or "Head"
    for eq in p["equipped"]:
        if eq["slot"] == slot:
            eq["item"] = body.itemId or ""
            break
    save(db)
    return make_reply(p)

@app.post("/api/claim")
def claim(body: ItemBody, authorization: Optional[str] = Header(None)):
    # same as buy for now
    return buy(body, authorization)

@app.post("/api/tutorial")
def tutorial(authorization: Optional[str] = Header(None)):
    p = get_player(authorization)
    if not p:
        raise HTTPException(401, detail="not logged in")
    p["tutorialDone"] = True
    save(db)
    return make_reply(p)

@app.post("/api/report")
def report(body: ReportBody, authorization: Optional[str] = Header(None)):
    p = get_player(authorization)
    if not p:
        raise HTTPException(401, detail="not logged in")
    return {"ok": True}

@app.post("/api/round")
@app.post("/api/tag")
@app.post("/api/pickup")
@app.post("/api/room")
@app.post("/api/linkcode")
def generic_ok(authorization: Optional[str] = Header(None)):
    p = get_player(authorization)
    if not p:
        raise HTTPException(401, detail="not logged in")
    return {"ok": True}

@app.get("/api/challenges")
def challenges(authorization: Optional[str] = Header(None)):
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
def claim_challenge(authorization: Optional[str] = Header(None)):
    p = get_player(authorization)
    if not p:
        raise HTTPException(401, detail="not logged in")
    return make_reply(p)

# ---------- Run ----------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
