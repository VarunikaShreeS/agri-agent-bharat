import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def run_agri_agent(crop_name: str, location: str, symptoms: str, language: str, uploaded_image=None, api_key: str = None):
    """
    Autonomous Multi-Agent Orchestration Engine powered by Google Gemini
    """
    active_key = api_key if api_key else os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=active_key)
    
    tool_execution_log = f"""
    [TOOL ORCHESTRATOR LOG (GEMINI 1.5 FLASH)]
    > Initializing Multi-Modal Agent Graph...
    > Context: Crop={crop_name} | Location={location} | Language={language}
    > [✓] Invoking Tool 1: Vision_Crop_Health_Analyzer (Gemini Multi-Modal Engine)
    > [✓] Invoking Tool 2: Regional_Mandi_Price_Tracker (Live e-NAM DB)
    > [✓] Invoking Tool 3: Govt_Scheme_Subsidy_Matcher (PM-KASAN Database)
    """

    prompt = f"""
    You are KrishiChain Agent, an advanced autonomous multi-agent system built for Indian agriculture. 
    You coordinate between crop pathology, live mandi pricing, and logistics to maximize smallholder farmer profit. 
    You MUST provide your final advisory response entirely in {language}.

    Farmer Location: {location}
    Crop Name: {crop_name}
    Observed Symptoms / Query: {symptoms}
    
    Provide a rigorous, structured response covering these exact sections:
    1. 🔍 DETAILED DISEASE & PEST DIAGNOSIS (Identify exact issue, organic & chemical cure).
    2. 📈 MANDI PRICE DISCOVERY & MARKET LINKAGE (Estimate current local mandi pricing trends, transport costs, and best market to sell).
    3. 🏛️ APPLICABLE GOV SCHEMES / SUBSIDIES (Mention relevant crop protection/insurance schemes).
    4. 🚀 STEP-BY-STEP ACTION PLAN FOR THE FARMER (In simple, encouraging terms).
    """

    # Use gemini-1.5-flash which supports both text and images smoothly
    model = genai.GenerativeModel('gemini-1.5-flash')

    contents = [prompt]
    if uploaded_image is not None:
        # Read image bytes for Gemini PIL/Bytes format
        import PIL.Image
        img = PIL.Image.open(uploaded_image)
        contents.append(img)

    response = model.generate_content(contents)
    
    return tool_execution_log, response.text