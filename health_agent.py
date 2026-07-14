import streamlit as st
from agno.agent import Agent
from agno.run.agent import RunOutput
from agno.models.google import Gemini

st.set_page_config(
    page_title="AI Health & Fitness Planner",
    page_icon="🏋️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"]{
    font-family: 'Poppins', sans-serif;
}

/* Background */
.stApp{
    background: linear-gradient(135deg,#07111f,#0f172a,#1e293b);
    background-size:400% 400%;
    animation:bgmove 15s ease infinite;
}

@keyframes bgmove{
0%{background-position:0% 50%;}
50%{background-position:100% 50%;}
100%{background-position:0% 50%;}
}

/* Main Container */

.block-container{
    padding-top:1.8rem;
    max-width:1200px;
}

/* Sidebar */

section[data-testid="stSidebar"]{
    background:rgba(18,25,40,.95);
    backdrop-filter:blur(20px);
    border-right:1px solid rgba(255,255,255,.08);
}

/* Titles */

h1{
    color:white;
    font-weight:700;
}

h2,h3{
    color:#F8FAFC;
}

/* Inputs */

.stTextInput input,
.stNumberInput input{
    background:#162033;
    color:white;
    border-radius:12px;
    border:1px solid #334155;
}

.stTextInput input:focus,
.stNumberInput input:focus{
    border:1px solid #38BDF8;
}

/* Selectbox */

.stSelectbox div[data-baseweb="select"]{
    border-radius:12px;
}

/* Button */

.stButton>button{

background:linear-gradient(90deg, #34D399, #86EFAC);

color:white;

height:55px;

width:100%;

font-size:18px;

font-weight:600;

border:none;

border-radius:14px;

transition:.35s;
}

.stButton>button:hover{

transform:translateY(-3px);

box-shadow:0 10px 30px rgba(6,182,212,.4);
}

/* Cards */

.glass{

background:rgba(255,255,255,.06);

border:1px solid rgba(255,255,255,.08);

backdrop-filter:blur(15px);

padding:25px;

border-radius:18px;

margin-bottom:20px;

}

/* Expander */

details{

background:rgba(255,255,255,.05);

border-radius:15px;

border:1px solid rgba(255,255,255,.08);

padding:12px;

}

/* Success */

div[data-testid="stAlert"]{

border-radius:14px;

}

/* Metric */

div[data-testid="metric-container"]{

background:rgba(255,255,255,.06);

border-radius:16px;

padding:18px;

}

/* Chat */

.chat-user{

background:#2563EB;

padding:15px;

border-radius:18px;

margin-bottom:10px;

color:white;

}

.chat-ai{

background:#1E293B;

padding:15px;

border-radius:18px;

margin-bottom:15px;

color:white;

}

</style>
""", unsafe_allow_html=True)

def display_dietary_plan(plan_content):
    with st.expander("📋 Your Personalized Dietary Plan", expanded=True):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🎯 Why this plan works")
            st.info(plan_content.get("why_this_plan_works", "Information not available"))
            st.markdown("### 🍽️ Meal Plan")
            st.write(plan_content.get("meal_plan", "Plan not available"))
        
        with col2:
            st.markdown("### ⚠️ Important Considerations")
            considerations = plan_content.get("important_considerations", "").split('\n')
            for consideration in considerations:
                if consideration.strip():
                    st.warning(consideration)

def display_fitness_plan(plan_content):
    with st.expander("💪 Your Personalized Fitness Plan", expanded=True):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🎯 Goals")
            st.success(plan_content.get("goals", "Goals not specified"))
            st.markdown("### 🏋️‍♂️ Exercise Routine")
            st.write(plan_content.get("routine", "Routine not available"))
        
        with col2:
            st.markdown("### 💡 Pro Tips")
            tips = plan_content.get("tips", "").split('\n')
            for tip in tips:
                if tip.strip():
                    st.info(tip)

def main():
    if 'dietary_plan' not in st.session_state:
        st.session_state.dietary_plan = {}
        st.session_state.fitness_plan = {}
        st.session_state.qa_pairs = []
        st.session_state.plans_generated = False

    st.markdown("""
<div class="glass">

<h1 style="margin-bottom:5px;">
🤖 AI Health & Fitness Planner
</h1>

<p style="font-size:18px;color:#CBD5E1;">
Your personal AI coach for nutrition, workouts and healthy living.
</p>

</div>
""", unsafe_allow_html=True)
    st.markdown("""
<div class="glass">

<h3>✨ Welcome</h3>

<p>

Generate personalized diet plans, workout routines, healthy habits and ask unlimited AI follow-up questions.

</p>

</div>
""", unsafe_allow_html=True)

    with st.sidebar:
        st.header("🔑 API Configuration")
        gemini_api_key = st.text_input(
            "Gemini API Key",
            type="password",
            help="Enter your Gemini API key to access the service"
        )
        
        if not gemini_api_key:
            st.warning("⚠️ Please enter your Gemini API Key to proceed")
            st.markdown("[Get your API key here](https://aistudio.google.com/apikey)")
            return
        
        st.success("API Key accepted!")

    if gemini_api_key:
        try:
            gemini_model = Gemini(id="gemini-3.5-flash", api_key=gemini_api_key)
        except Exception as e:
            st.error(f"❌ Error initializing Gemini model: {e}")
            return

        st.header("👤 Your Profile")
        
        col1, col2 = st.columns(2)
        
        with col1:
            age = st.number_input("Age", min_value=10, max_value=100, step=1, help="Enter your age")
            height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, step=0.1)
            activity_level = st.selectbox(
                "Activity Level",
                options=["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extremely Active"],
                help="Choose your typical activity level"
            )
            dietary_preferences = st.selectbox(
                "Dietary Preferences",
                options=["Vegetarian", "Keto", "Gluten Free", "Low Carb", "Dairy Free"],
                help="Select your dietary preference"
            )

        with col2:
            weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, step=0.1)
            sex = st.selectbox("Sex", options=["Male", "Female", "Other"])
            fitness_goals = st.selectbox(
                "Fitness Goals",
                options=["Lose Weight", "Gain Muscle", "Endurance", "Stay Fit", "Strength Training"],
                help="What do you want to achieve?"
            )

        if st.button("🎯 Generate My Personalized Plan", use_container_width=True):
            with st.spinner("Creating your perfect health and fitness routine..."):
                try:
                    dietary_agent = Agent(
                        name="Dietary Expert",
                        role="Provides personalized dietary recommendations",
                        model=gemini_model,
                        instructions=[
                            "Consider the user's input, including dietary restrictions and preferences.",
                            "Suggest a detailed meal plan for the day, including breakfast, lunch, dinner, and snacks.",
                            "Provide a brief explanation of why the plan is suited to the user's goals.",
                            "Focus on clarity, coherence, and quality of the recommendations.",
                        ]
                    )

                    fitness_agent = Agent(
                        name="Fitness Expert",
                        role="Provides personalized fitness recommendations",
                        model=gemini_model,
                        instructions=[
                            "Provide exercises tailored to the user's goals.",
                            "Include warm-up, main workout, and cool-down exercises.",
                            "Explain the benefits of each recommended exercise.",
                            "Ensure the plan is actionable and detailed.",
                        ]
                    )

                    user_profile = f"""
                    Age: {age}
                    Weight: {weight}kg
                    Height: {height}cm
                    Sex: {sex}
                    Activity Level: {activity_level}
                    Dietary Preferences: {dietary_preferences}
                    Fitness Goals: {fitness_goals}
                    """

                    dietary_plan_response: RunOutput = dietary_agent.run(user_profile)
                    dietary_plan = {
                        "why_this_plan_works": "High Protein, Healthy Fats, Moderate Carbohydrates, and Caloric Balance",
                        "meal_plan": dietary_plan_response.content,
                        "important_considerations": """
                        - Hydration: Drink plenty of water throughout the day
                        - Electrolytes: Monitor sodium, potassium, and magnesium levels
                        - Fiber: Ensure adequate intake through vegetables and fruits
                        - Listen to your body: Adjust portion sizes as needed
                        """
                    }

                    fitness_plan_response: RunOutput = fitness_agent.run(user_profile)
                    fitness_plan = {
                        "goals": "Build strength, improve endurance, and maintain overall fitness",
                        "routine": fitness_plan_response.content,
                        "tips": """
                        - Track your progress regularly
                        - Allow proper rest between workouts
                        - Focus on proper form
                        - Stay consistent with your routine
                        """
                    }

                    st.session_state.dietary_plan = dietary_plan
                    st.session_state.fitness_plan = fitness_plan
                    st.session_state.plans_generated = True
                    st.session_state.qa_pairs = []

                    display_dietary_plan(dietary_plan)
                    display_fitness_plan(fitness_plan)

                except Exception as e:
                    st.error(f"❌ An error occurred: {e}")

        if st.session_state.plans_generated:
            st.header("❓ Questions about your plan?")
            question_input = st.text_input("What would you like to know?")

            if st.button("Get Answer"):
                if question_input:
                    with st.spinner("Finding the best answer for you..."):
                        dietary_plan = st.session_state.dietary_plan
                        fitness_plan = st.session_state.fitness_plan

                        context = f"Dietary Plan: {dietary_plan.get('meal_plan', '')}\n\nFitness Plan: {fitness_plan.get('routine', '')}"
                        full_context = f"{context}\nUser Question: {question_input}"

                        try:
                            agent = Agent(model=gemini_model, debug_mode=True, markdown=True)
                            run_response: RunOutput = agent.run(full_context)

                            if hasattr(run_response, 'content'):
                                answer = run_response.content
                            else:
                                answer = "Sorry, I couldn't generate a response at this time."

                            st.session_state.qa_pairs.append((question_input, answer))
                        except Exception as e:
                            st.error(f"❌ An error occurred while getting the answer: {e}")

            if st.session_state.qa_pairs:
                st.header("💬 Q&A History")
                for question, answer in st.session_state.qa_pairs:
                    st.markdown(f"**Q:** {question}")
                    st.markdown(f"**A:** {answer}")

if __name__ == "__main__":
    main()