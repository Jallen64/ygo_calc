import streamlit as st
import random
import json
from collections import Counter


def monte_carlo_simulation(deck, hand_size, num_draws):
    """
    Simulates drawing a hand from the deck multiple times using Monte Carlo simulation.
    Returns the expected and simulated average hand composition.
    """
    deck_list = [card for card, count in deck.items() for _ in range(count)]
    total_deck_size = sum(deck.values())
    results = Counter()

    for _ in range(num_draws):
        hand = random.sample(deck_list, hand_size)
        hand_counts = Counter(hand)
        for card, count in hand_counts.items():
            results[card] += count

    simulated_avg_hand = {card: count / num_draws for card, count in results.items()}
    expected_avg_hand = {card: (count / total_deck_size) * hand_size for card, count in deck.items()}

    return total_deck_size, simulated_avg_hand, expected_avg_hand


def save_deck(deck_name, deck):
    """
    Saves the current deck under the given deck name.
    """
    saved_decks = st.session_state.get("saved_decks", {})
    saved_decks[deck_name] = deck.copy()
    st.session_state["saved_decks"] = saved_decks
    st.session_state["refresh_dropdown"] = True


def load_deck(deck_name):
    """
    Loads a deck from saved decks.
    """
    return st.session_state.get("saved_decks", {}).get(deck_name, {}).copy()


def main():
    st.markdown("# 🎴Yu-Gi-Oh! Hand Odds Calculator")
    st.markdown("---")

    # Initialize session state variables
    if "saved_decks" not in st.session_state:
        st.session_state["saved_decks"] = {}
    if "refresh_dropdown" not in st.session_state:
        st.session_state["refresh_dropdown"] = False
    if "deck" not in st.session_state:
        st.session_state["deck"] = {}
    if "selected_deck" not in st.session_state:
        st.session_state["selected_deck"] = "New Deck"

    # Deck selection and management
    col1, col2 = st.columns([2, 1])
    with col1:
        deck_names = list(st.session_state["saved_decks"].keys())
        selected_deck = st.selectbox("🔽 Select a deck to load", ["New Deck"] + deck_names, key="deck_dropdown")

        # Load deck only if selection changes and it's not a new deck
        if selected_deck != st.session_state["selected_deck"]:
            if selected_deck != "New Deck":
                st.session_state["deck"] = load_deck(selected_deck)
            else:
                st.session_state["deck"] = {}  # Reset to empty for a new deck
            st.session_state["selected_deck"] = selected_deck
            st.rerun()

    with col2:
        deck_name_input = st.text_input("📁 Save Deck As")
        if st.button("💾 Save Deck") and deck_name_input:
            save_deck(deck_name_input, st.session_state["deck"])
            st.success(f"Deck '{deck_name_input}' saved!")
            st.rerun()
        if selected_deck != "New Deck" and st.button("❌ Delete Deck"):
            del st.session_state["saved_decks"][selected_deck]
            st.success(f"Deck '{selected_deck}' deleted!")
            st.rerun()

    st.markdown("---")
    st.subheader("🛠 Deck Configuration")

    # User input for deck modification
    new_deck = st.session_state["deck"].copy()

    for card_type in list(new_deck.keys()):
        col1, col2 = st.columns([4, 1])
        with col1:
            new_count = st.text_input(f"{card_type}", value=str(new_deck[card_type]), key=f"{card_type}_count")
        with col2:
            if st.button(f"❌ {card_type}", key=f"delete_{card_type}"):
                del new_deck[card_type]
                st.session_state["deck"] = new_deck.copy()
                save_deck(selected_deck, new_deck)  # Save the modified deck immediately
                st.rerun()
        if new_count.isdigit():
            new_deck[card_type] = int(new_count)

    st.session_state["deck"] = new_deck.copy()

    st.markdown("---")
    st.subheader("➕ Add New Card Type")

    col1, col2 = st.columns(2)
    with col1:
        new_card_type = st.text_input("🆕 Card Type", key="new_card_type")
    with col2:
        new_card_count = st.text_input("🔢 Card Count", value="0", key="new_card_count")

    if st.button("✅ Add Card Type") and new_card_type and new_card_count.isdigit():
        st.session_state["deck"][new_card_type] = int(new_card_count)
        save_deck(selected_deck, st.session_state["deck"])  # Save immediately
        st.rerun()

    st.markdown("---")
    st.subheader("🎲 Run Simulation")
    hand_size = st.number_input("✋ Hand Size", min_value=1, value=5, step=1)
    num_draws = st.number_input("🔄 Number of Draws (Monte Carlo Simulations)", min_value=100, value=10000, step=100)

    if st.button("▶ Run Simulation"):
        total_deck_size, simulated_avg_hand, expected_avg_hand = monte_carlo_simulation(st.session_state["deck"],
                                                                                        hand_size, num_draws)
        st.subheader("📊 Results")
        st.write(f"🃏 Deck Size: {total_deck_size}")
        st.write("### 🎲 Simulated Average Hand Composition:", simulated_avg_hand)
        st.write("### 📈 Expected Average Hand Composition:", expected_avg_hand)


if __name__ == "__main__":
    main()
