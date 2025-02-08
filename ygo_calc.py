import streamlit as st
import random
import math
from collections import Counter

###############################################################################
# Set up Streamlit theming and layout
###############################################################################
st.set_page_config(
    page_title="Yu-Gi-Oh! Hand Odds Calculator",
    page_icon="🎴",
    layout="wide"
)

# Minimal custom styling to unify background
st.markdown("""
    <style>
        /* Ensure both main page and sidebar share the same background color */
        [data-testid="stAppViewContainer"] {
            background-color: #121212 !important;
        }
        [data-testid="stSidebar"] {
            background-color: #121212 !important;
        }

        /* Center the main header */
        .css-18e3th9 {
            text-align: center;
        }

        /* Style buttons a bit more */
        .stButton>button { 
            background-color: #4CAF50; 
            color: white; 
            border-radius: 6px;
            padding: 6px 12px;
            border: none;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }

        /* Slightly smaller text for label elements */
        .css-145kmo2, .css-1r5f3cv, .css-1v0mbdj {
            font-size: 0.95rem;
        }

        /* More spacing around columns */
        .css-1vd0k7l {
            gap: 1rem;
        }
    </style>
""", unsafe_allow_html=True)


###############################################################################
# Helper functions
###############################################################################
def hypergeom_pmf(k, K, n, N):
    if k > K or k > n or n > N:
        return 0.0
    return (math.comb(K, k) * math.comb(N - K, n - k)) / math.comb(N, n)


def monte_carlo_simulation(deck, hand_size, num_draws):
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
        card: count / num_draws for card, count in results.items()
    }
    expected_avg_hand = {
        card: (count / total_deck_size) * hand_size
        for card, count in deck.items() if card != "_notes"
    }

    return total_deck_size, simulated_avg_hand, expected_avg_hand


def simulate_playable_hands_advanced(deck, hand_size, num_draws, constraints):
    deck_list = [
        card
        for card, count in deck.items()
        if card != "_notes"
        for _ in range(count)
    ]
    total_deck_size = sum(count for card, count in deck.items() if card != "_notes")

    if hand_size > total_deck_size:
        return 0, 0

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
# Deck persistence & editing
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
# Main App
###############################################################################
def main():
    # ---------------------------
    # SIDEBAR for deck management
    # ---------------------------
    st.sidebar.title("Deck Management")

    # Manage cookies
    st.sidebar.subheader("Manage Persistence (Cookies)")
    if st.sidebar.button("💾 Save Decks to Cookies"):
        save_decks_to_cookies()
        st.sidebar.success("Decks saved to cookies!")
    if st.sidebar.button("📂 Load Decks from Cookies"):
        load_decks_from_cookies()
        st.sidebar.success("Decks loaded from cookies!")
        st.rerun()
    if st.sidebar.button("🗑 Clear All Cookies"):
        clear_decks_in_cookies()

    # Initialize session state
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
        st.session_state["deck"] = st.session_state["saved_decks"]["Sample Deck"].copy()
    if "selected_deck" not in st.session_state:
        st.session_state["selected_deck"] = "Sample Deck"

    # Deck selection
    st.sidebar.subheader("Select a Deck")
    deck_names = list(st.session_state["saved_decks"].keys())
    if not deck_names:
        deck_names = ["No Decks Available"]
    selected_deck = st.sidebar.selectbox(
        "Deck:",
        deck_names,
        index=deck_names.index(st.session_state.get("selected_deck", deck_names[0]))
    )
    if selected_deck != st.session_state.get("selected_deck"):
        st.session_state["deck"] = load_deck(selected_deck)
        st.session_state["selected_deck"] = selected_deck
        st.rerun()

    # Create / Delete deck
    st.sidebar.subheader("Create / Delete Deck")
    deck_name_input = st.sidebar.text_input("New Deck Name")
    if st.sidebar.button("Save New Deck"):
        if deck_name_input:
            save_deck(deck_name_input, st.session_state["deck"])
            st.sidebar.success(f"Deck '{deck_name_input}' saved!")
            st.rerun()
        else:
            st.sidebar.warning("Please enter a name for the new deck.")
    if st.sidebar.button("Delete Selected Deck"):
        current_deck = st.session_state["selected_deck"]
        if len(st.session_state["saved_decks"]) == 1:
            st.sidebar.warning("You can't delete the last remaining deck!")
        else:
            delete_deck(current_deck)
            st.sidebar.success(f"Deck '{current_deck}' has been deleted.")
            if st.session_state["saved_decks"]:
                new_selection = list(st.session_state["saved_decks"].keys())[0]
                st.session_state["selected_deck"] = new_selection
                st.session_state["deck"] = load_deck(new_selection)
            else:
                st.session_state["deck"] = {}
                st.session_state["selected_deck"] = None
            st.rerun()

    # -------------
    # MAIN CONTENT
    # -------------
    st.title("🎴 Yu-Gi-Oh! Hand Odds Calculator")
    st.markdown(
        "This application helps you **manage Yu-Gi-Oh! decks** and **calculate** "
        "various probabilities for drawing specific cards or combos in your opening hand."
    )
    st.markdown("---")

    # Expander for Deck Configuration
    with st.expander("🛠 Deck Configuration", expanded=True):
        st.markdown("Edit the quantities of each card type below:")
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

    # Expander for Deck Notes
    with st.expander("📝 Deck Notes"):
        st.write("Add notes or reminders about this deck, combos, or card interactions.")
        notes_key = f"notes_{st.session_state['selected_deck']}"
        current_notes = st.session_state["deck"].get("_notes", "")
        text_val = st.text_area("Notes:", value=current_notes, height=120, key=notes_key)
        if text_val != current_notes:
            st.session_state["deck"]["_notes"] = text_val
            save_deck(selected_deck, st.session_state["deck"])
            st.success("Notes updated!")

    # Expander for Add New Card
    with st.expander("➕ Add New Card Type"):
        st.markdown("Add another card type to the deck.")
        col1, col2 = st.columns([3, 1])
        with col1:
            new_card_name = st.text_input("Card Type Name")
        with col2:
            new_card_quantity = st.text_input("Quantity", value="1")

        if st.button("Add Card Type"):
            if new_card_name and new_card_quantity.isdigit():
                if new_card_name not in st.session_state["deck"]:
                    st.session_state["deck"][new_card_name] = int(new_card_quantity)
                    save_deck(selected_deck, st.session_state["deck"])
                    st.success(f"Added {new_card_name} ({new_card_quantity}) to deck!")
                    st.rerun()
                else:
                    st.warning("Card type already exists! Use the configuration above to update it.")
            else:
                st.warning("Please enter a valid card name and quantity.")

    # Advanced calculations in tabs
    st.markdown("---")
    st.subheader("Advanced Calculations")
    tab_run, tab_constraints, tab_hyper = st.tabs(
        ["🎲 Run Simulation", "⚙️ Custom Hand Constraints", "🔢 Hypergeometric Calc"]
    )

    # 1) Monte Carlo Simulation
    with tab_run:
        st.write("### Monte Carlo Simulation")
        st.markdown(
            "Specify your hand size and the number of random draws (simulations). "
            "We'll estimate the average composition of your opening hand."
        )
        hand_size = st.number_input("✋ Hand Size", min_value=1, value=5, step=1, key="mc_hand_size")
        num_draws = st.number_input("🔄 Number of Draws", min_value=100, value=10000, step=100, key="mc_draws")

        if st.button("▶ Run Simulation", key="run_monte_carlo"):
            total_deck_size, simulated_avg_hand, expected_avg_hand = monte_carlo_simulation(
                st.session_state["deck"],
                hand_size,
                num_draws
            )
            st.subheader("📊 Results")
            st.write(f"🃏 Deck Size: {total_deck_size}")
            st.write("**Simulated Average Hand Composition**", simulated_avg_hand)
            st.write("**Expected Average Hand Composition**", expected_avg_hand)

    # 2) Custom Hand Constraints
    with tab_constraints:
        st.write("### Custom Hand Constraints Probability")
        st.markdown(
            "Define min and max counts for each card type in your deck. We'll run "
            "a Monte Carlo simulation to see how many hands satisfy **all** constraints."
        )

        deck_dict = st.session_state["deck"]
        card_types = [ct for ct in deck_dict.keys() if ct != "_notes"]

        hand_size_constraints = st.number_input("✋ Hand Size (Constraints)", min_value=1, value=5, step=1,
                                                key="con_hand_size")
        num_draws_constraints = st.number_input("🔄 Number of Draws (Constraints)",
                                                min_value=100, value=10000, step=100, key="con_draws")

        if not card_types:
            st.info("No card types found in this deck. Add some above.")
        else:
            constraints = {}
            for ct in card_types:
                col_min, col_max = st.columns(2)
                with col_min:
                    min_val = st.number_input(f"Min {ct} in hand", min_value=0,
                                              max_value=hand_size_constraints,
                                              value=0, key=f"min_{ct}")
                with col_max:
                    max_val = st.number_input(f"Max {ct} in hand", min_value=0,
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

    # 3) Hypergeometric Calculator
    with tab_hyper:
        st.write("### Customizable Hypergeometric Calculator")
        st.markdown(
            "Exact math-based approach to see how likely you are to draw **k** copies "
            "of a single card type in an n-card hand."
        )

        deck_dict = st.session_state["deck"]
        card_types = [ct for ct in deck_dict.keys() if ct != "_notes"]

        if not card_types:
            st.info("No card types in this deck. Add some above.")
        else:
            chosen_card = st.selectbox("Choose Card Type", card_types, key="hyper_card")
            hand_size_hyper = st.number_input("✋ Hand Size (Hypergeom)", min_value=1, value=5, step=1,
                                              key="hyper_hand_size")
            K = deck_dict[chosen_card]
            N = sum(deck_dict[ct] for ct in card_types)
            st.write(f"**Deck Size (N):** {N}, **'{chosen_card}' Copies (K):** {K}")

            k_value = st.number_input("Number of copies in your hand (k)",
                                      min_value=0,
                                      max_value=min(K, hand_size_hyper),
                                      value=1,
                                      step=1,
                                      key="hyper_k")
            mode = st.radio("Probability Type", ["Exactly k", "At least k"], key="hyper_mode")

            if st.button("Calculate Hypergeometric Probability", key="hyper_button"):
                if N < hand_size_hyper:
                    st.warning("Hand size is larger than deck size—check your configuration!")
                else:
                    if mode == "Exactly k":
                        p_exact = hypergeom_pmf(k_value, K, hand_size_hyper, N)
                        st.write(f"**P(X = {k_value})**: {p_exact:.5f}")
                    else:  # "At least k"
                        p_at_least = 0.0
                        for kk in range(k_value, min(K, hand_size_hyper) + 1):
                            p_at_least += hypergeom_pmf(kk, K, hand_size_hyper, N)
                        st.write(f"**P(X ≥ {k_value})**: {p_at_least:.5f}")


if __name__ == "__main__":
    main()
