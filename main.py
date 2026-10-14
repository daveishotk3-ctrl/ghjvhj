if player is None:
    new_id = max([int(k) for k in db["players"]] + [100]) + 1
    player = {
        "playerId": new_id,
        "deviceId": body.deviceId,
        "name": "ERROR Functi0n",
        "colour": "999",
        "coins": 99999,
        "owned": [item["id"] for item in SHOP],   # ← auto-own everything
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
    logger.info(f"Created new player {new_id} with all items")
else:
    # Also give existing players any missing items
    for item in SHOP:
        if item["id"] not in player["owned"]:
            player["owned"].append(item["id"])
    player["isNew"] = False
    player["dailyReward"] = 0
