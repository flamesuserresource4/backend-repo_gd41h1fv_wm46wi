import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Team, Player, ClubInfo, Document

app = FastAPI(title="Sports Club API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Sports Club API is running"}

# Utility converter for MongoDB ObjectId
class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        try:
            return str(ObjectId(v))
        except Exception:
            raise ValueError("Invalid ObjectId")

# ---------- Teams Endpoints ----------
@app.post("/api/teams", response_model=dict)
def create_team(team: Team):
    team_id = create_document("team", team)
    return {"id": team_id}

@app.get("/api/teams", response_model=List[dict])
def list_teams():
    docs = get_documents("team")
    # Convert ObjectIds to strings
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return docs

@app.get("/api/teams/{team_id}", response_model=dict)
def get_team(team_id: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    try:
        doc = db["team"].find_one({"_id": ObjectId(team_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Team not found")
        doc["_id"] = str(doc["_id"])
        # Attach players
        players = list(db["player"].find({"team_id": team_id}))
        for p in players:
            p["_id"] = str(p["_id"])
        doc["players"] = players
        return doc
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid team id")

# ---------- Players Endpoints ----------
@app.post("/api/players", response_model=dict)
def create_player(player: Player):
    # Validate referenced team exists
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    if not db["team"].find_one({"_id": ObjectId(player.team_id)}):
        raise HTTPException(status_code=404, detail="Team not found for this player")
    player_id = create_document("player", player)
    return {"id": player_id}

@app.get("/api/players", response_model=List[dict])
def list_players(team_id: Optional[str] = None):
    filter_q = {"team_id": team_id} if team_id else {}
    docs = get_documents("player", filter_q)
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return docs

# ---------- Infos Endpoints ----------
@app.post("/api/infos", response_model=dict)
def create_info(info: ClubInfo):
    info_id = create_document("clubinfo", info)
    return {"id": info_id}

@app.get("/api/infos", response_model=List[dict])
def list_infos():
    docs = get_documents("clubinfo")
    for d in docs:
        d["_id"] = str(d.get("_id"))
    # sort by order then title
    docs.sort(key=lambda x: (x.get("order", 0), x.get("title", "")))
    return docs

# ---------- Documents Endpoints ----------
@app.post("/api/documents", response_model=dict)
def create_doc(doc: Document):
    doc_id = create_document("document", doc)
    return {"id": doc_id}

@app.get("/api/documents", response_model=List[dict])
def list_docs(category: Optional[str] = None):
    filter_q = {"category": category} if category else {}
    docs = get_documents("document", filter_q)
    for d in docs:
        d["_id"] = str(d.get("_id"))
    # sort by date desc if present
    docs.sort(key=lambda x: x.get("published_on") or "", reverse=True)
    return docs

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
