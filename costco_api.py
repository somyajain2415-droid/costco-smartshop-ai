
from fastapi import FastAPI
from pydantic import BaseModel

from shopping_tools import search_products

from basket_tools import calculate_basket

import os
import secrets

from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader

load_dotenv()

api_key_header = APIKeyHeader(
    name="X-Agent-Key",
    auto_error=False
)

def verify_agent_key(
    provided_key: str | None = Depends(api_key_header)
):
    expected_key = os.getenv("COSTCO_AGENT_API_KEY")

    if not expected_key:
        raise HTTPException(
            status_code=503,
            detail="Agent API authentication is not configured"
        )

    if not provided_key or not secrets.compare_digest(
        provided_key,
        expected_key
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid agent API key"
        )

# Create the Costco API
app = FastAPI(title="Costco SmartShop Agent API")


# Define what a customer agent can send
class ShoppingRequest(BaseModel):
    customer_agent: str
    message: str

class BasketItem(BaseModel):
    id: int
    quantity: int


class BasketRequest(BaseModel):
    items: list[BasketItem]
    budget: float


# Test whether the Costco API is running
@app.get("/")
def home():
    return {
        "status": "online",
        "agent": "Costco SmartShop AI",
        "message": "Costco API is ready"
    }


# Receive a message from a customer agent

@app.post(
    "/agent/message",
    dependencies=[Depends(verify_agent_key)]
)

def receive_message(request: ShoppingRequest):
    return {
        "from": "Costco SmartShop AI",
        "to": request.customer_agent,
        "received_message": request.message,
        "status": "received",
        "reply": "Hello! Costco's API received your request."
    }


@app.get(
    "/products/search",
    dependencies=[Depends(verify_agent_key)]
)

def search_costco_products(
    keyword: str,
    vegetarian_only: bool = False
):
    products = search_products(
        keyword=keyword,
        vegetarian_only=vegetarian_only
    )

    return {
        "agent": "Costco SmartShop AI",
        "status": "success",
        "products": products
    }


@app.post(
    "/basket/calculate",
    dependencies=[Depends(verify_agent_key)]
)

def calculate_costco_basket(request: BasketRequest):
    items = [
        {
            "id": item.id,
            "quantity": item.quantity
        }
        for item in request.items
    ]

    result = calculate_basket(
        items=items,
        budget=request.budget
    )

    return {
        "agent": "Costco SmartShop AI",
        "status": "success",
        "basket": result
    }
