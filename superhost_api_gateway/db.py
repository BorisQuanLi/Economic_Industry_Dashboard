"""Firestore client — primary company profile store.
Analog: Company.find_by_stock_ticker() in etl_service/src/models/company.py.
"""
from google.cloud import firestore


class FirestoreClient:
    def __init__(self, project_id: str):
        self.db = firestore.Client(project=project_id)

    async def upsert_company(self, ticker: str, data: dict) -> dict:
        doc_ref = self.db.collection("companies").document(ticker)
        doc_ref.set(data, merge=True)
        return doc_ref.get().to_dict()

    async def get_company(self, ticker: str) -> dict | None:
        doc = self.db.collection("companies").document(ticker).get()
        return doc.to_dict() if doc.exists else None
