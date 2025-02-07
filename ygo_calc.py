import streamlit as st
import random
import json
from collections import Counter
from PIL import Image

# Set custom theme and layout
st.set_page_config(page_title="Yu-Gi-Oh! Hand Odds Calculator", 
                   page_icon="🎴", layout="wide")

# Apply custom CSS for a more modern look
st.markdown("""
    <style>
        .css-1d391kg { text-align: center; }
        .stButton>button { 
            background-color: #4CAF50; 
            color: white; 
            border-radius: 8px;
            padding: 10px 20px;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }
    </style>
""", unsafe_allow_html=True)

def monte_carlo_simulation(deck, hand_size, num_draws):
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
    saved_decks = st.session_state.get("saved_decks", {})
    saved_decks[deck_name] = deck.copy()
    st.session_state["saved_decks"] = saved_decks

def load_deck(deck_name):
    return st.session_state.get("saved_decks", {}).get(deck_name, {}).copy()

def main():
    st.title("🎴 Yu-Gi-Oh! Hand Odds Calculator")
    st.markdown("---")
    
    # Initialize session state variables
    if "saved_decks" not in st.session_state:
        st.session_state["saved_decks"] = {"Sample Deck": {"starter": 10, "extender": 10, "hand trap": 10, "board breaker": 10}}
    if "deck" not in st.session_state:
        st.session_state["deck"] = st.session_state["saved_decks"].get("Sample Deck", {}).copy()
    
    # Deck selection and management
    col1, col2 = st.columns([2, 1])
    with col1:
        deck_names = list(st.session_state["saved_decks"].keys())
        selected_deck = st.selectbox("🔽 Select a deck to load", deck_names)
        if selected_deck != st.session_state.get("selected_deck", "Sample Deck"):
            st.session_state["deck"] = load_deck(selected_deck)
            st.session_state["selected_deck"] = selected_deck
            st.rerun()
    with col2:
        deck_name_input = st.text_input("📁 Save Deck As")
        if st.button("💾 Save Deck") and deck_name_input:
            save_deck(deck_name_input, st.session_state["deck"])
            st.success(f"Deck '{deck_name_input}' saved!")
            st.rerun()
    
    st.markdown("---")
    st.subheader("🛠 Deck Configuration")
    new_deck = st.session_state["deck"].copy()
    
    for card_type in list(new_deck.keys()):
        col1, col2 = st.columns([4, 1])
        with col1:
            new_count = st.text_input(f"{card_type}", value=str(new_deck[card_type]))
        with col2:
            if st.button(f"❌ {card_type}"):
                del new_deck[card_type]
                st.session_state["deck"] = new_deck.copy()
                save_deck(selected_deck, new_deck)
                st.rerun()
        if new_count.isdigit():
            new_deck[card_type] = int(new_count)
    
    st.session_state["deck"] = new_deck.copy()
    
    st.markdown("---")
    st.subheader("🎲 Run Simulation")
    hand_size = st.number_input("✋ Hand Size", min_value=1, value=5, step=1)
    num_draws = st.number_input("🔄 Number of Draws (Monte Carlo Simulations)", min_value=100, value=10000, step=100)
    
    if st.button("▶ Run Simulation"):
        total_deck_size, simulated_avg_hand, expected_avg_hand = monte_carlo_simulation(st.session_state["deck"], hand_size, num_draws)
        st.subheader("📊 Results")
        st.write(f"🃏 Deck Size: {total_deck_size}")
        st.write("### 🎲 Simulated Average Hand Composition:", simulated_avg_hand)
        st.write("### 📈 Expected Average Hand Composition:", expected_avg_hand)
    
if __name__ == "__main__":
    main()
