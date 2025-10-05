import os
import google.generativeai as genai
from dotenv import load_dotenv
from pgn import pgn_to_uci_moves , pgn_to_final_fen

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("❌ GOOGLE_API_KEY not found in environment variables")

# Configure Gemini
genai.configure(api_key=api_key)

# Preferred models
PRIMARY_MODEL = "models/gemini-2.5-flash"
FALLBACK_MODEL = "models/gemini-2.5-pro"

def explain_move(pgn: str, move: str, eval: str) -> str:
    """
    Generate human-friendly commentary for a chess move using Google Gemini.
    
    :param fen: Current position in FEN notation
    :param move: The move played (in SAN)
    :param eval: Engine evaluation of the move
    :return: Natural language commentary string
    """

    prompt = f"""
    Chess Position (FEN): {pgn_to_final_fen(pgn)}
    Moves played to reach here: {pgn_to_uci_moves(pgn)}
    Move: {move}
    Engine Eval: {eval}

    Explain in plain language:
    - Are the moves played before good or bad?
    - Why this move is played
    - What are the short-term and long-term goals
    - Any risks, traps, or tactical ideas
    """

    try:
        model = genai.GenerativeModel(PRIMARY_MODEL)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e1:
        print(f"⚠️ Primary model {PRIMARY_MODEL} failed: {e1}")
        try:
            model = genai.GenerativeModel(FALLBACK_MODEL)
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e2:
            print(f"❌ Fallback model {FALLBACK_MODEL} also failed: {e2}")
            return "Error: Could not generate commentary."