import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from typing import List

@strawberry.type
class Guest:
    phone_number: str
    is_vip: bool
    name: str = "Valued Guest"

@strawberry.type
class Query:
    @strawberry.field
    async def guest_lookup(self, phone: str) -> Guest:
        # Placeholder for your Astra/Firestore logic
        return Guest(phone_number=phone, is_vip=True)

@strawberry.type
class Mutation:
    @strawberry.field
    def log_call(self, phone: str) -> str:
        return f"Call from {phone} logged for Superhost scale-analysis."

schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

app = FastAPI(title="Superhost API Gateway")
app.include_router(graphql_app, prefix="/graphql")

@app.get("/health")
async def health_check():
    return {"status": "operational", "version": "v1-superhost"}

