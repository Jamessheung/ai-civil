from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MOCK_CLUSTERS = [
    {
        "cluster_id": 101,
        "title": "Federal Reserve Report: Inflation Stabilizing",
        "domain": "Power",
        "cluster_state": "Active",
        "last_updated_at": datetime.now().isoformat()
    },
    {
        "cluster_id": 102,
        "title": "Rumor: Tech Giant collapsing?",
        "domain": "Tech",
        "cluster_state": "Disputed",
        "last_updated_at": datetime.now().isoformat()
    }
]

MOCK_DETAILS_101 = {
    "event_cluster": MOCK_CLUSTERS[0],
    "evidence": [
        {
            "evidence_id": 1, "level": 5, 
            "extract": "Data indicates inflation has stabilized at 2.1%.",
            "reliability_score": 0.95,
            "pointer": {"url": "https://gov.federalreserve.org", "match_text": "Inflation stabilized at 2.1%"}
        },
        {
            "evidence_id": 2, "level": 5, 
            "extract": "The Federal Reserve released its quarterly financial report today.",
            "reliability_score": 0.95,
            "pointer": {"url": "https://gov.federalreserve.org", "match_text": "Federal Reserve released"}
        }
    ],
    "latest_score": {"consistency": 1.0, "risk": 0.0, "mechanism_uncertainty": 0.1}
}

MOCK_DETAILS_102 = {
    "event_cluster": MOCK_CLUSTERS[1],
    "evidence": [
        {
            "evidence_id": 3, "level": 2, 
            "extract": "My cousin works at OpenAI and says they are bankrupt.",
            "reliability_score": 0.2,
            "pointer": {"url": "https://x.com/user123", "match_text": "says they are bankrupt"}
        },
        {
            "evidence_id": 4, "level": 1, 
            "extract": "It might be over guys.",
            "reliability_score": 0.1,
            "pointer": {"url": "https://x.com/user123", "match_text": "might be over"}
        }
    ],
    "latest_score": {"consistency": 0.0, "risk": 0.8, "mechanism_uncertainty": 0.9}
}

@app.get("/api/clusters")
def get_clusters():
    return MOCK_CLUSTERS

@app.get("/api/cluster/{cluster_id}")
def get_cluster(cluster_id: int):
    if cluster_id == 101: return MOCK_DETAILS_101
    if cluster_id == 102: return MOCK_DETAILS_102
    return {}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)
