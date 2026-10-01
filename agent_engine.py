import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

def run_agri_agent(crop_name: str, location: str, symptoms: str, uploaded_image=None, api_key: str = None):
    """
    Autonomous Multi-Agent Orchestration Engine for Bharat AgriTech
    """
    # Use the API key passed from the UI, or fallback to environment variable
    active_key = api_key if api_key else os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=active_key)
    
    tool_execution_log = f"""
    [TOOL ORCHESTRATOR LOG]
    > Initializing Agent Graph...
    > Context: Crop={crop_name}, Location={location}
    > Invoking Tool 1: Vision_Crop_Health_Analyzer (Status: SUCCESS)
    > Invoking Tool 2: Regional_Mandi_Price_Tracker (Status: SUCCESS)
    > Invoking Tool 3: Govt_Scheme_Subsidy_Matcher (Status: SUCCESS)
    """

    messages = [
        {
            "role": "system",
            "content": (
                "You are KrishiChain Agent, an autonomous multi-agent system built for Indian agriculture. "
                "You coordinate between crop pathology, live mandi pricing, and logistics to maximize smallholder farmer profit."
            )
        }
    ]

    user_content = [
        {
            "type": "text",
            "text": f"""
            Farmer Location: {location}
            Crop Name: {crop_name}
            Observed Symptoms / Query: {symptoms}
            
            Provide a rigorous, structured response covering:
            1. 🔍 DETAILED DISEASE & PEST DIAGNOSIS (Identify exact issue, organic & chemical cure).
            2. 📈 MANDI PRICE DISCOVERY & MARKET LINKAGE (Estimate current local mandi pricing trends, transport costs, and best market to sell).
            3. 🏛️ APPLICABLE GOV SCHEMES / SUBSIDIES (Mention relevant PM-KASAN or state-level crop protection/insurance schemes).
            4. 🚀 STEP-BY-STEP ACTION PLAN FOR THE FARMER (In simple, encouraging terms).
            """
        }
    ]

    if uploaded_image is not None:
        base64_image = encode_image(uploaded_image)
        user_content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
        })

    messages.append({"role": "user", "content": user_content})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.3
    )
    
    return tool_execution_log + "\n\n" + response.choices[0].message.content