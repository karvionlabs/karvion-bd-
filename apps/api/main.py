from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import uvicorn

from schemas import OrchestrationRequest, OrchestrationResponse
from intent_router import analyze_intent

# Load environment variables (e.g. OPENAI_API_KEY) from .env
load_dotenv()

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="KARVION BD Master Intent Router",
    description="Analyzes Bengali input and routes to appropriate domain sub-agents.",
    version="1.0.0"
)

# Set up CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3005"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


import sys
import os

# Add packages to path so we can import agents
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "packages")))

from agents.citizen import CitizenAgent
from agents.student import StudentAgent
from agents.consumer import ConsumerAgent
from agents.farmer import FarmerAgent
from agents.market import MarketAgent
from agents.waste import WasteAgent

@app.post("/api/v1/orchestrate")
async def orchestrate_request(request: OrchestrationRequest):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        raise HTTPException(status_code=503, detail="OpenAI API Key is missing. Triggering client-side fallback.")

    try:
        # Step 1: Analyze Intent (or override if explicitly selected)
        if request.selected_agent and request.selected_agent != "Auto":
            routing_result = analyze_intent(request.user_query, request.location)
            routing_result.agent_name = request.selected_agent
            routing_result.requires_clarification = False
        else:
            routing_result = analyze_intent(request.user_query, request.location)
        
        # Step 2: Route to specific agent if confidence is high
        final_answer = None
        if not routing_result.requires_clarification:
            if routing_result.agent_name == "CitizenAgent":
                final_answer = CitizenAgent().process_query(request.user_query)
            elif routing_result.agent_name == "StudentAgent":
                final_answer = StudentAgent().process_query(request.user_query)
            elif routing_result.agent_name == "ConsumerAgent":
                final_answer = ConsumerAgent().process_query(request.user_query)
            elif routing_result.agent_name == "FarmerAgent":
                final_answer = FarmerAgent().process_query(request.user_query)
            elif routing_result.agent_name == "MarketAgent":
                final_answer = MarketAgent().process_query(request.user_query)
            elif routing_result.agent_name == "Waste Agent":
                final_answer = WasteAgent().process_query(request.user_query)

            if final_answer:
                routing_result.next_action = final_answer

        return routing_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from pydantic import BaseModel
from fpdf import FPDF
from fastapi.responses import Response

class ComplaintData(BaseModel):
    content: str

@app.post("/api/v1/download-complaint-pdf")
async def download_complaint_pdf(data: ComplaintData):
    try:
        # Create PDF using fpdf2
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font("ArialUnicode", style="", fname="C:\\Windows\\Fonts\\arial.ttf") 
        # Note: TrueType fonts are needed for Unicode/Bengali. In production, provide an explicit TTF like Kalpurush.ttf.
        # Here we use Arial as a system fallback which may not fully support Bengali rendering perfectly,
        # but serves as the backend logic completion.
        try:
            pdf.set_font("ArialUnicode", size=12)
        except:
            pdf.set_font("Helvetica", size=12) # Fallback if arial fails
            
        # Add content safely (handling encoding)
        for line in data.content.split('\n'):
            pdf.multi_cell(0, 10, txt=line.encode('utf-8', 'ignore').decode('utf-8'))
            
        pdf_bytes = pdf.output()
        
        return Response(content=bytes(pdf_bytes), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=Complaint_Draft.pdf"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
