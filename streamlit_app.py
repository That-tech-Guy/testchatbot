import streamlit as st
import random
import json

st.set_page_config(page_title="Financial Education", layout="wide")

# --- Load chatbot data ---
def load_intents():
    with open("data/intents.json") as f:
        return json.load(f)

intents = load_intents()

def get_response(user_input):
    for intent in intents["intents"]:
        for pattern in intent["patterns"]:
            if pattern.lower() in user_input.lower():
                return random.choice(intent["responses"])
    return "Sorry, I didn't understand that. Try asking about saving, investing, or budgeting."

# --- Header Section ---
st.markdown("""
    <style>
        .navbar {
            background-color: #f0f2f6;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #ccc;
        }
        .nav-links {
            display: flex;
            gap: 2rem;
        }
        .nav-links a {
            text-decoration: none;
            color: #4a4a4a;
            font-weight: bold;
        }
        .footer {
            text-align: center;
            padding: 1rem;
            color: #888;
            border-top: 1px solid #ccc;
            margin-top: 2rem;
        }
    </style>

    <div class="navbar">
        <div style="font-size: 1.5rem; font-weight: bold;">💸 Financial Education</div>
        <div class="nav-links">
            <a href="#home">Home</a>
            <a href="#budgeting">Budgeting</a>
            <a href="#investing">Investing</a>
            <a href="#saving">Saving</a>
            <a href="#chatbot">Chatbot</a>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- Sections ---
st.markdown('<h2 id="home">🏠 Welcome</h2>', unsafe_allow_html=True)
st.write("""
Welcome to your hub for financial literacy. Learn the essentials of budgeting, saving, and investing, and chat with our assistant to guide your journey toward financial independence.
""")

st.markdown('---')

st.markdown('<h2 id="budgeting">💰 Budgeting</h2>', unsafe_allow_html=True)
st.write("""
Learn how to plan your spending with the 50/30/20 rule:
- **50%** for Needs
- **30%** for Wants
- **20%** for Savings
""")

income = st.number_input("Enter your monthly income ($):", min_value=0)
if income:
    st.success(f"Suggested:\n\n- Needs: ${income * 0.5:.2f}\n- Wants: ${income * 0.3:.2f}\n- Savings: ${income * 0.2:.2f}")

st.markdown('---')

st.markdown('<h2 id="investing">📈 Investing</h2>', unsafe_allow_html=True)
st.write("""
Understand how to grow your wealth:
- Begin with low-risk options like **bonds** or **index funds**
- Understand **risk vs. reward**
- Avoid investing money you can't afford to lose
""")

risk = st.selectbox("Select your risk appetite", ["Low", "Medium", "High"])
if risk:
    st.info(f"Suggested for {risk} risk:")
    if risk == "Low":
        st.write("- Government Bonds\n- Savings Accounts\n- Certificates of Deposit")
    elif risk == "Medium":
        st.write("- ETFs\n- Balanced Funds\n- Real Estate")
    else:
        st.write("- Stocks\n- Crypto\n- Startups")

st.markdown('---')

st.markdown('<h2 id="saving">💾 Saving</h2>', unsafe_allow_html=True)
st.write("""
Smart saving helps you build a safety net:
- Set clear goals
- Use automatic transfers
- Save before spending
""")

goal = st.text_input("What are you saving for?")
amount = st.number_input("Goal amount ($):", min_value=0)
months = st.slider("Months to reach goal:", 1, 24, 6)
if goal and amount:
    monthly = amount / months
    st.success(f"Save ${monthly:.2f} per month to reach your **{goal}** goal in {months} months.")

st.markdown('---')

st.markdown('<h2 id="chatbot">🤖 Ask Me Anything</h2>', unsafe_allow_html=True)
user_question = st.text_input("Your finance question:")
if user_question:
    st.write("💬 You:", user_question)
    st.write("🤖 Bot:", get_response(user_question))

st.markdown('<div class="footer">© 2025 Financial Education Project</div>', unsafe_allow_html=True)
