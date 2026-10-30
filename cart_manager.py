
import streamlit as st


def initialize_cart():
    """Create a shopping cart if one doesn't exist."""
    if "cart" not in st.session_state:
        st.session_state.cart = None

    if "cart_approved" not in st.session_state:
        st.session_state.cart_approved = False


def save_cart(basket_result):
    """Save a Python-validated basket."""
    initialize_cart()

    st.session_state.cart = basket_result
    st.session_state.cart_approved = False


def display_cart():
    """Display the shopping cart and approval buttons."""
    initialize_cart()

    cart = st.session_state.cart

    if cart is None:
        st.info("Your shopping cart is currently empty.")
        return

    st.subheader("🛒 Your Shopping Basket")

    for item in cart["basket"]:
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            st.write(item["name"])

        with col2:
            st.write(f"Qty: {item['quantity']}")

        with col3:
            st.write(f"${item['subtotal']:.2f}")

    st.divider()

    st.metric("Basket Total", f"${cart['total']:.2f}")

    st.write(
        f"**Remaining Budget:** "
        f"${cart['remaining_budget']:.2f}"
    )

    if cart["problems"]:
        for problem in cart["problems"]:
            st.warning(problem)

    if not cart["within_budget"]:
        st.error("This basket exceeds your budget.")

    if st.session_state.cart_approved:
        st.success(
            "Basket approved for this demonstration! "
            "No real order has been placed."
        )

    elif cart["ready_for_approval"]:
        if st.button("Approve Basket", type="primary"):
            st.session_state.cart_approved = True
            st.rerun()

    if st.button("Clear Basket"):
        st.session_state.cart = None
        st.session_state.cart_approved = False
        st.rerun()
