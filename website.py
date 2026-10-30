
import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

from shopping_tools import search_products
from basket_tools import calculate_basket

from cart_manager import initialize_cart, save_cart, display_cart

# Connect Gemini's basket tool to the website cart
def calculate_and_save_basket(items: list[dict], budget: float) -> dict:
    """
    Calculate a proposed basket and save it for customer review.
    """
    result = calculate_basket(items=items, budget=budget)

    # Store only a Python-validated result
    save_cart(result)

    print("[AGENT ACTION] Basket saved to website cart")

    return result

load_dotenv()

st.set_page_config(
    page_title="Costco SmartShop AI",
    page_icon="🛒",
    layout="centered"
)

st.title("🛒 Costco SmartShop AI")
st.caption("AI-powered shopping assistant | University demonstration")
st.info(
    "Student prototype. Product prices and inventory are "
    "simulated, not live Costco data. No real orders are placed."
)

# Initialize the shopping cart
initialize_cart()



# Display the shopping cart
display_cart()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Gemini API key not found in your .env file.")
    st.stop()

INSTRUCTIONS = """
You are Costco SmartShop, a friendly customer-facing
shopping assistant for a university demonstration.

Help customers search products and prepare shopping
baskets within their budgets.

Available tools:
- search_products: searches the demonstration catalog.
- calculate_and_save_basket: validates quantities, stock and budget, then saves the proposed basket for customer review.
When the customer asks you to prepare a shopping basket,
you must call calculate_and_save_basket after searching
the catalog. Do not claim that a basket was saved unless
the tool has completed successfully.
Rules:
1. Search the catalog before recommending products.
2. When preparing a basket, call calculate_basket.
3. Use actual product IDs returned by the search tool.
4. Never invent prices or stock information.
5. Respect dietary preferences and budget limits.
6. If the basket is over budget, revise and recalculate.
7. Explain unavailable items and offer alternatives.
8. All products and prices are simulated demonstration data.
9. Never claim to access live Costco systems.
10. Never place real orders or process payments.
11. A basket is only a proposal awaiting customer approval.
12. Keep responses concise and easy to understand.
"""

# Remember chat messages while the website is open
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Welcome to Costco SmartShop! "
                "Tell me what you're shopping for, "
                "your budget and any preferences."
            )
        }
    ]

# Display the conversation
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Customer types a shopping request
question = st.chat_input(
    "What would you like to shop for?"
)

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("SmartShop is planning your shopping..."):
            client = None

            try:
                client = genai.Client(api_key=api_key)

                # Include conversation history for context
                conversation = []

                for message in st.session_state.messages:
                    role = (
                        "user"
                        if message["role"] == "user"
                        else "model"
                    )

                    conversation.append(
                        types.Content(
                            role=role,
                            parts=[
                                types.Part.from_text(
                                    text=message["content"]
                                )
                            ]
                        )
                    )

                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=conversation,
                    config=types.GenerateContentConfig(
                        system_instruction=INSTRUCTIONS,
                       
tools=[
    search_products,
    calculate_and_save_basket
],

                        automatic_function_calling=(
                            types.AutomaticFunctionCallingConfig(
                                disable=False,
                                maximum_remote_calls=10
                            )
                        )
                    )
                )

                answer = (
                    response.text
                    or "I couldn't prepare a response. Please try again."
                )

                st.markdown(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

                st.rerun()

            except Exception as error:
                st.error(
                    "SmartShop couldn't complete your request. "
                    "Please try again."
                )
                st.caption(
                    f"Technical details: {type(error).__name__}: {error}"
                )

            finally:
                if client is not None:
                    client.close()
