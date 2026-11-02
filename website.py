
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

# ============================================================
# COSTCO SMARTSHOP AI - REFERENCE-INSPIRED VISUAL DESIGN
# ============================================================

st.markdown("""
<style>

/* =========================
   PAGE
   ========================= */

.stApp {
    background: #F3F7FD;
}

.block-container {
    max-width: 1180px;
    padding-top: 0rem;
    padding-bottom: 4rem;
}


/* =========================
   TOP NAVIGATION
   ========================= */

.ss-nav {
    background: #103873;
    padding: 18px 28px;

    display: flex;
    align-items: center;
    justify-content: space-between;

    border-radius: 0;
}

.ss-brand {
    display: flex;
    align-items: center;
    gap: 14px;
}

.ss-costco {
    background: #ED1739;
    color: #FFFFFF;

    padding: 7px 13px;
    border-radius: 8px;

    font-size: 17px;
    font-weight: 900;
    letter-spacing: -0.4px;
}

.ss-name {
    color: #FFFFFF;

    font-size: 18px;
    font-weight: 800;
}

.ss-name span {
    opacity: 0.72;
}

.ss-basket-pill {
    background: #FFFFFF;
    color: #07549A;

    padding: 10px 18px;

    border-radius: 100px;

    font-size: 14px;
    font-weight: 800;
}


/* =========================
   HERO SECTION
   ========================= */

.ss-hero {
    position: relative;
    overflow: hidden;

    background: #0868B7;

    min-height: 390px;

    padding: 68px 30px 100px 30px;
}

.ss-hero-content {
    position: relative;
    z-index: 3;

    max-width: 720px;
}


/* AI SHOPPING BADGE */

.ss-badge {
    display: inline-block;

    background: #FFFFFF;
    color: #ED1739;

    padding: 8px 14px;

    border-radius: 100px;

    font-size: 12px;
    font-weight: 900;
    letter-spacing: 1px;

    margin-bottom: 26px;
}


/* HERO TITLE */

.ss-hero h1 {
    color: #FFFFFF !important;

    font-size: 64px !important;
    line-height: 0.98 !important;

    letter-spacing: -3px;

    margin: 0 0 24px 0 !important;

    max-width: 680px;
}

.ss-highlight {
    display: inline-block;

    background: #ED1739;
    color: #FFFFFF;

    padding: 1px 13px 7px 13px;

    border-radius: 13px;
}


/* HERO DESCRIPTION */

.ss-hero-copy {
    color: #FFFFFF;

    font-size: 20px;
    line-height: 1.45;

    max-width: 600px;

    margin: 0;
}


/* =========================
   DECORATIVE CIRCLES
   ========================= */

.ss-red-circle {
    position: absolute;

    width: 330px;
    height: 330px;

    border-radius: 50%;

    background: #ED1739;

    right: -100px;
    top: -65px;

    z-index: 1;
}

.ss-navy-circle {
    position: absolute;

    width: 175px;
    height: 175px;

    border-radius: 50%;

    background: #103873;

    right: 150px;
    bottom: -100px;

    z-index: 1;
}


/* =========================
   SECTION TITLES
   ========================= */

.ss-section-title {
    color: #102A56;

    font-size: 30px;
    font-weight: 900;

    letter-spacing: -0.7px;

    margin-top: 30px;
    margin-bottom: 3px;
}

.ss-section-copy {
    color: #536987;

    font-size: 15px;

    margin-bottom: 14px;
}


/* =========================
   QUICK START BUTTONS
   ========================= */

div.stButton > button {
    min-height: 88px;

    border: none;
    border-radius: 20px;

    font-size: 17px;
    font-weight: 800;

    transition:
        transform 0.18s ease,
        box-shadow 0.18s ease;

    box-shadow: none;
}

div.stButton > button:hover {
    transform: translateY(-3px);

    box-shadow:
        0 12px 25px rgba(16, 56, 115, 0.15);
}


/* FIRST QUICK START CARD */

div[data-testid="stHorizontalBlock"]
> div:nth-child(1)
button {
    background: #ED1739;
    color: #FFFFFF;
}


/* SECOND QUICK START CARD */

div[data-testid="stHorizontalBlock"]
> div:nth-child(2)
button {
    background: #0868B7;
    color: #FFFFFF;
}


/* THIRD QUICK START CARD */

div[data-testid="stHorizontalBlock"]
> div:nth-child(3)
button {
    background: #103873;
    color: #FFFFFF;
}


/* =========================
   CHAT MESSAGES
   ========================= */

[data-testid="stChatMessage"] {
    background: #FFFFFF;

    border: 1px solid #E4ECF5;

    border-radius: 20px;

    padding: 15px 17px;

    margin-bottom: 12px;

    box-shadow:
        0 4px 14px rgba(16, 56, 115, 0.04);
}


/* =========================
   CHAT INPUT
   ========================= */

[data-testid="stChatInput"] {
    background: #FFFFFF;

    border: 1px solid #D5E2EF;

    border-radius: 20px;

    box-shadow:
        0 15px 35px rgba(16, 56, 115, 0.12);
}


/* =========================
   SHOPPING BASKET
   ========================= */

[data-testid="stVerticalBlockBorderWrapper"] {
    background: #FFFFFF;

    border: 1px solid #D9E7F5 !important;

    border-radius: 20px;

    box-shadow:
        0 4px 14px rgba(16, 56, 115, 0.04);
}


/* =========================
   BASKET METRICS
   ========================= */

[data-testid="stMetric"] {
    background: #F3F8FE;

    border: 1px solid #DFEAF5;

    border-radius: 15px;

    padding: 15px;
}


/* =========================
   ALERT BOXES
   ========================= */

[data-testid="stAlert"] {
    border-radius: 14px;
}


/* =========================
   FOOTER
   ========================= */

.ss-footer {
    margin-top: 28px;

    background: #103873;
    color: #FFFFFF;

    border-radius: 14px;

    padding: 15px 20px;

    font-size: 13px;
    font-weight: 600;
}


/* =========================
   REMOVE STREAMLIT CHROME
   ========================= */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}


/* =========================
   MOBILE
   ========================= */

@media (max-width: 700px) {

    .ss-nav {
        padding: 15px 18px;
    }

    .ss-basket-pill {
        display: none;
    }

    .ss-hero {
        padding:
            45px 22px
            75px 22px;

        min-height: 350px;
    }

    .ss-hero h1 {
        font-size: 44px !important;
        letter-spacing: -2px;
    }

    .ss-hero-copy {
        font-size: 17px;
    }

    .ss-red-circle {
        width: 220px;
        height: 220px;

        right: -100px;
    }

    .ss-navy-circle {
        width: 120px;
        height: 120px;

        right: 30px;
    }
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# ============================================================
# NAVIGATION + HERO
# ============================================================

st.markdown(
"""<div class="ss-nav">
<div class="ss-brand">
<div class="ss-costco">COSTCO</div>
<div class="ss-name">SmartShop <span>AI</span></div>
</div>
<div class="ss-basket-pill">🛒 Basket · SmartShop</div>
</div>

<div class="ss-hero">
<div class="ss-red-circle"></div>
<div class="ss-navy-circle"></div>

<div class="ss-hero-content">
<div class="ss-badge">AI SHOPPING ASSISTANT</div>

<h1>
Your list. Your<br>
budget. <span class="ss-highlight">Our AI.</span>
</h1>

<p class="ss-hero-copy">
Discover products, plan your basket and stay inside your budget —
all in one conversation.
</p>

</div>
</div>""",
unsafe_allow_html=True
)

# st.info(
#     "Student prototype. Product prices and inventory are "
#     "simulated, not live Costco data. No real orders are placed."
# )
# Initialize the shopping cart
initialize_cart()



# Display the shopping cart
# display_cart()

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


# Suggested shopping prompts
suggested_question = None
if len(st.session_state.messages) <= 1:
    st.markdown("### Not sure where to start?")
    st.caption("Choose a shopping idea or type your own request.")

    col1, col2, col3 = st.columns(3)



    with col1:
        if st.button("🍝 Plan a Dinner", use_container_width=True):
            suggested_question = (
                "Prepare a vegetarian dinner basket for two "
                "people under $50. Show available products, "
                "prices, and the total."
             )

        with col2:
            if st.button("💰 Shop Under $30", use_container_width=True):
                suggested_question = (
                    "Prepare a grocery basket under $30 using "
                    "available Costco products. Show my "
                    "remaining budget."
                )

        with col3:
            if st.button("🛒 Weekly Groceries", use_container_width=True):
                suggested_question = (
                    "Prepare a weekly grocery basket for a small "
                    "household under $100. Include available "
                    "essentials and calculate the total."
                )

# Customer can type or select a suggested prompt
typed_question = st.chat_input(
    "What would you like to shop for?"
)

question = suggested_question or typed_question


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
