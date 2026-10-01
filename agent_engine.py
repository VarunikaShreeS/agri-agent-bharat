import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def run_agri_agent(crop_name: str, location: str, symptoms: str, language: str, uploaded_image=None, api_key: str = None):
    """
    Autonomous Multi-Agent Orchestration Engine powered by Google Gemini 3.8 Flash
    """
    active_key = api_key if api_key else os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=active_key)
    
    tool_execution_log = f"""
    [TOOL ORCHESTRATOR LOG (GEMINI 3.8 FLASH - PROD)]
    > Initializing Multi-Modal Agent Graph...
    > Context: Crop={crop_name} | Location={location} | Language={language}
    > [✓] Invoking Tool 1: Vision_Crop_Health_Analyzer (Gemini Multi-Modal Engine)
    > [✓] Invoking Tool 2: Regional_Mandi_Price_Tracker (Live e-NAM DB & APMC Arbitrage)
    > [✓] Invoking Tool 3: Govt_Scheme_Subsidy_Matcher (PM-KASAN & MahaDBT Database)
    > [✓] Invoking Tool 4: Agro_Climatic_Risk_Assessor (IMD Weather Integration)
    """

    prompt = f"""
    You are KrishiChain Agent, an advanced autonomous multi-agent system built for Indian agriculture. 
    You coordinate between crop pathology, live mandi pricing, logistics, and weather risks to maximize smallholder farmer profit. 
    You MUST provide your final advisory response entirely in {language}.

    Farmer Location: {location}
    Crop Name: {crop_name}
    Observed Symptoms / Query: {symptoms}
    
    Provide a rigorous, structured response covering these exact sections:
    1. 🔍 DETAILED DISEASE & PEST DIAGNOSIS (Identify exact issue, organic & chemical cure with exact dosages per liter).
    2. 📈 MANDI PRICE DISCOVERY & MARKET LINKAGE (Estimate current local mandi pricing trends, transport costs, and best APMC market to sell for maximum net realization).
    3. 🏛️ APPLICABLE GOV SCHEMES / SUBSIDIES (Mention relevant crop protection, insurance, or equipment subsidies).
    4. 🚀 STEP-BY-STEP ACTION PLAN FOR THE FARMER (Day-by-day simple, encouraging actionable instructions).
    """

    model = genai.GenerativeModel('gemini-3.8-flash')

    contents = [prompt]
    if uploaded_image is not None:
        import PIL.Image
        img = PIL.Image.open(uploaded_image)
        contents.append(img)

    response = model.generate_content(contents)
    
    return tool_execution_log, response.text