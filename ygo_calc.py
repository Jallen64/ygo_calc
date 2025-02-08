import streamlit as st
import random
import math
from collections import Counter

# Set custom theme and layout
st.set_page_config(
    page_title="Yu-Gi-Oh! Hand Odds Calculator",
    page_icon="🎴",
    layout="wide"
)

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

###############################################################################
# Part A: Helper Functions
###############################################################################

def hypergeom_pmf(k, K, n, N):
    """
    Probability of exactly k successes in n draws (Hypergeometric).
    N = total deck size (excluding _notes)
    K = number of copies of the chosen card
    n = hand size
    k = successes in your drawn hand
    """
    if k > K or k > n or n > N:
        return 0.0
    return (math.comb(K, k) * math.comb(N - K, n - k)) / math.comb(N, n)

def monte_carlo_simulation(deck, hand_size, num_draws):
    """
    Existing Monte Carlo simulation for average hand composition.
    """
    deck_list = [
        card
        for card, count in deck.items()
        if card != "_notes"
        for _ in range(count)
    ]
    total_deck_size = sum(count for card, count in deck.items() if card != "_notes")
    results = Counter()

    for _ in range(num_draws):
        hand = random.sample(deck_list, hand_size)
        hand_counts = Counter(hand)
        for card, count in hand_counts.items():
            results[card] += count

    simulated_avg_hand = {
        card: count / num_draws
        for card, count in results.items()
    }
    expected_avg_hand = {
        card: (count / total_deck_size) * hand_size
        for card, count in deck.items()
        if card != "_notes"
    }

    return total_deck_size, simulated_avg_hand, expected_avg_hand

def simulate_playable_hands_advanced(deck, hand_size, num_draws, constraints):
    """
    Monte Carlo approach where 'constraints' is a dict:
      constraints[card_type] = (min_count, max_count)

    For each simulated hand, we check:
        min_count <= # of that card_type in hand <= max_count
    for ALL card types in constraints. If all pass,
    we consider that hand valid/playable.

    Returns (valid_count, total_draws).
    """
    deck_list = [
        card
        for card, count in deck.items()
        if card != "_notes"
        for _ in range(count)
    ]
    total_deck_size = sum(count for card, count in deck.items() if card != "_notes")

    if hand_size > total_deck_size:
        return 0, 0  # invalid scenario

    valid_count = 0

    for _ in range(num_draws):
        hand = random.sample(deck_list, hand_size)
        hand_counts = Counter(hand)

        # Check each constraint
        is_valid = True
        for ctype, (min_ct, max_ct) in constraints.items():
            c_count = hand_counts.get(ctype, 0)
            if not (min_ct <= c_count <= max_ct):
                is_valid = False
                break

        if is_valid:
            valid_count += 1

    return valid_count, num_draws


###############################################################################
# Part B: Deck Persistence & Editing
###############################################################################

def save_deck(deck_name, deck):
    saved_decks = st.session_state.get("saved_decks", {})
    saved_decks[deck_name] = deck.copy()
    st.session_state["saved_decks"] = saved_decks
    st.session_state["selected_deck"] = deck_name

def load_deck(deck_name):
    return st.session_state.get("saved_decks", {}).get(deck_name, {}).copy()

def save_decks_to_cookies():
    st.query_params["saved_decks"] = str(st.session_state.get("saved_decks", {}))

def load_decks_from_cookies():
    saved_decks = st.query_params.get("saved_decks", "{}")
    st.session_state["saved_decks"] = eval(saved_decks)

def delete_deck(deck_name):
    saved_decks = st.session_state.get("saved_decks", {})
    if deck_name in saved_decks:
        del saved_decks[deck_name]
    st.session_state["saved_decks"] = saved_decks

def clear_decks_in_cookies():
    st.query_params["saved_decks"] = "{}"
    st.session_state["saved_decks"] = {
        "Sample Deck": {
            "starter": 10,
            "extender": 10,
            "hand trap": 10,
            "board breaker": 10,
            "_notes": ""
        }
    }
    st.session_state["deck"] = st.session_state["saved_decks"]["Sample Deck"].copy()
    st.session_state["selected_deck"] = "Sample Deck"
    st.rerun()

###############################################################################
# Part C: Main Streamlit App
###############################################################################

def main():
    #
    # HOME PAGE SECTIONS
    #
    st.title("🎴 Yu-Gi-Oh! Hand Odds Calculator")

    # 1. Manage Persistence (Cookies)
    st.markdown("---")
    st.subheader("Manage Persistence (Cookies)")
    col_a, col_b, col_c = st.columns([1.2, 1.2, 1.6])
    with col_a:
        if st.button("💾 Save Decks to Cookies"):
            save_decks_to_cookies()
            st.success("Decks saved to cookies!")
    with col_b:
        if st.button("📂 Load Decks from Cookies"):
            load_decks_from_cookies()
            st.success("Decks loaded from cookies!")
            st.rerun()
    with col_c:
        if st.button("🗑 Clear All Cookies"):
            clear_decks_in_cookies()

    # 2. Initialize session state
    if "saved_decks" not in st.session_state:
        st.session_state["saved_decks"] = {
            "Sample Deck": {
                "starter": 10,
                "extender": 10,
                "hand trap": 10,
                "board breaker": 10,
                "_notes": ""
            }
        }
    if "deck" not in st.session_state:
        st.session_state["deck"] = st.session_state["saved_decks"].get("Sample Deck", {}).copy()
    if "selected_deck" not in st.session_state:
        st.session_state["selected_deck"] = "Sample Deck"

    # 3. Select Deck & Create/Delete Deck side by side
    st.markdown("---")
    col_sel, col_crdlt = st.columns([2, 1])
    with col_sel:
        st.subheader("Select Deck")
        deck_names = list(st.session_state["saved_decks"].keys())
        if not deck_names:
            deck_names = ["No Decks Available"]
        selected_deck = st.selectbox(
            "🔽 Select a deck to load",
            deck_names,
            index=deck_names.index(st.session_state.get("selected_deck", deck_names[0]))
        )
        if selected_deck != st.session_state.get("selected_deck"):
            st.session_state["deck"] = load_deck(selected_deck)
            st.session_state["selected_deck"] = selected_deck
            st.rerun()

    with col_crdlt:
        st.subheader("Create / Delete Deck")
        deck_name_input = st.text_input("📁 Save Deck As")
        col_b1, col_b2 = st.columns([1, 1])
        with col_b1:
            if st.button("💾 Create Deck"):
                if deck_name_input:
                    save_deck(deck_name_input, st.session_state["deck"])
                    st.success(f"Deck '{deck_name_input}' saved!")
                    st.rerun()
                else:
                    st.warning("Please enter a name for the new deck.")
        with col_b2:
            if st.button("🗑 Delete Selected Deck"):
                current_deck = st.session_state["selected_deck"]
                if len(st.session_state["saved_decks"]) == 1:
                    st.warning("You can't delete the last remaining deck!")
                else:
                    delete_deck(current_deck)
                    st.success(f"Deck '{current_deck}' has been deleted.")
                    if st.session_state["saved_decks"]:
                        new_selection = list(st.session_state["saved_decks"].keys())[0]
                        st.session_state["selected_deck"] = new_selection
                        st.session_state["deck"] = load_deck(new_selection)
                    else:
                        st.session_state["deck"] = {}
                        st.session_state["selected_deck"] = None
                    st.rerun()

    # 4. Deck Configuration
    st.markdown("---")
    st.subheader("🛠 Deck Configuration")
    new_deck = st.session_state["deck"].copy()

    for card_type in list(new_deck.keys()):
        if card_type == "_notes":
            continue
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

    # 5. Deck Notes
    st.markdown("---")
    st.subheader("📝 Deck Notes")
    notes_key = f"notes_{st.session_state['selected_deck']}"
    current_notes = st.session_state["deck"].get("_notes", "")
    st.text_area("Add your notes here:",
                 value=current_notes,
                 height=150,
                 key=notes_key)

    if st.session_state[notes_key] != current_notes:
        st.session_state["deck"]["_notes"] = st.session_state[notes_key]
        save_deck(selected_deck, st.session_state["deck"])
        st.success("Notes updated!")

    # 6. Add New Card Type
    st.markdown("---")
    st.subheader("➕ Add New Card Type")
    col1, col2 = st.columns([3, 1])
    with col1:
        new_card_name = st.text_input("🃏 Card Type Name", key="new_card_name")
    with col2:
        new_card_quantity = st.text_input("📦 Quantity", key="new_card_quantity")

    if st.button("➕ Add Card") and new_card_name and new_card_quantity.isdigit():
        if new_card_name not in st.session_state["deck"]:
            st.session_state["deck"][new_card_name] = int(new_card_quantity)
            save_deck(selected_deck, st.session_state["deck"])
            st.success(f"Added {new_card_name} ({new_card_quantity}) to deck!")
            st.rerun()
        else:
            st.warning("Card type already exists! Use the deck configuration above to update it.")

    #
    # ---------------
    # TABBED SECTIONS
    # ---------------
    #
    st.markdown("---")
    st.subheader("Calculations")

    tab_run, tab_constraints, tab_hyper = st.tabs(
        ["🎲 Run Simulation", "⚙️ Custom Hand Constraints", "🔢 Hypergeometric Calc"]
    )

    with tab_run:
        st.write("### Monte Carlo Simulation")
        hand_size = st.number_input("✋ Hand Size", min_value=1, value=5, step=1)
        num_draws = st.number_input("🔄 Number of Draws (Monte Carlo Simulations)",
                                    min_value=100, value=10000, step=100)

        if st.button("▶ Run Simulation", key="run_monte_carlo"):
            total_deck_size, simulated_avg_hand, expected_avg_hand = monte_carlo_simulation(
                st.session_state["deck"],
                hand_size,
                num_draws
            )
            st.subheader("📊 Results")
            st.write(f"🃏 Deck Size: {total_deck_size}")
            st.write("### 🎲 Simulated Average Hand Composition:", simulated_avg_hand)
            st.write("### 📈 Expected Average Hand Composition:", expected_avg_hand)

    with tab_constraints:
        st.write("### Custom Hand Constraints Probability")

        deck_dict = st.session_state["deck"]
        card_types = [ct for ct in deck_dict.keys() if ct != "_notes"]

        if not card_types:
            st.info("No card types in this deck (besides notes). Add some card types first.")
        else:
            # Let user define hand_size / num_draws here as well, or reuse from above
            st.write("Use the same 'hand_size' and 'num_draws' from the Run Simulation tab, or set anew below.")
            hand_size_constraints = st.number_input("✋ Hand Size (Constraints)", min_value=1, value=5, step=1)
            num_draws_constraints = st.number_input("🔄 Draws (Constraints)",
                                                    min_value=100, value=10000, step=100)

            st.write("Define min/max counts for each card type. We'll compute the fraction of hands that satisfy ALL constraints.")
            constraints = {}
            for ct in card_types:
                col_min, col_max = st.columns(2)
                with col_min:
                    min_val = st.number_input(f"Min {ct}", min_value=0,
                                              max_value=hand_size_constraints,
                                              value=0, key=f"min_{ct}")
                with col_max:
                    max_val = st.number_input(f"Max {ct}", min_value=0,
                                              max_value=hand_size_constraints,
                                              value=hand_size_constraints, key=f"max_{ct}")
                constraints[ct] = (min_val, max_val)

            if st.button("Calculate Probability", key="constraints_probability"):
                valid_count, total_sims = simulate_playable_hands_advanced(
                    deck_dict,
                    hand_size_constraints,
                    num_draws_constraints,
                    constraints
                )
                if total_sims > 0:
                    playable_rate = valid_count / total_sims
                    st.write(f"**Hands Meeting Constraints:** {valid_count} / {total_sims}")
                    st.write(f"**Probability:** {playable_rate:.2%}")
                else:
                    st.warning("Check your deck size or hand size. Simulation couldn't run properly.")

    with tab_hyper:
        st.write("### Customizable Hypergeometric Calculator")

        deck_dict = st.session_state["deck"]
        card_types = [ct for ct in deck_dict.keys() if ct != "_notes"]

        if not card_types:
            st.info("No card types found in this deck. Add some card types first.")
        else:
            st.write("You can pick a card type, set how many copies (k), and see the EXACT probability using Hypergeom.")
            # Let user define or reuse 'hand_size'
            hand_size_hyper = st.number_input("✋ Hand Size (Hypergeom)", min_value=1, value=5, step=1)
            chosen_card = st.selectbox("Choose a card type to analyze (Hypergeom)", card_types)
            K = deck_dict[chosen_card]
            N = sum(deck_dict[ct] for ct in card_types)

            st.write(f"**Deck Size (N):** {N}, **Copies of '{chosen_card}' (K):** {K}, **Hand Size (n):** {hand_size_hyper}")
            k_value = st.number_input("Number of copies in your hand (k)",
                                      min_value=0,
                                      max_value=min(K, hand_size_hyper),
                                      value=1,
                                      step=1)
            mode = st.radio("Probability Type:", ["Exactly k", "At least k"], key="hyper_mode")

            if st.button("Calculate Hypergeometric Probability", key="hyper_button"):
                if N < hand_size_hyper:
                    st.warning("Hand size is larger than deck size—check your configuration!")
                else:
                    if mode == "Exactly k":
                        p_exact = hypergeom_pmf(k_value, K, hand_size_hyper, N)
                        st.write(f"**P(X = {k_value})**: {p_exact:.5f}")
                    else:
                        p_at_least = 0.0
                        for kk in range(k_value, min(K, hand_size_hyper) + 1):
                            p_at_least += hypergeom_pmf(kk, K, hand_size_hyper, N)
                        st.write(f"**P(X ≥ {k_value})**: {p_at_least:.5f}")


if __name__ == "__main__":
    main()
