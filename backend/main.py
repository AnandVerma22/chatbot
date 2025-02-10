from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
from pydantic import BaseModel
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch
from fastapi.responses import FileResponse
import logging

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Only allow frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connect to MySQL database
try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shrikrishna@123",  # Change to your password
        database="chatbot_db"
    )
    cursor = db.cursor(dictionary=True)  # ✅ FIXED: Use dictionary=True instead of DictCursor
    logger.info("✅ Database connected successfully!")
except mysql.connector.Error as e:
    logger.error(f"❌ Database connection failed: {e}")

# Load AI Model
model_name = "google/flan-t5-small"  # Small & Fast Model (300MB)

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def generate_ai_response(prompt):
    inputs = tokenizer(prompt, return_tensors="pt")
    output = model.generate(**inputs, max_length=200)
    return tokenizer.decode(output[0], skip_special_tokens=True)

# Data model for user queries
class Query(BaseModel):
    query: str

# Chat history
chat_history = []

@app.post("/chat", operation_id="chat_with_ai")
async def chat(query: Query):
    user_input = query.query.lower()
    chat_history.append({"sender": "user", "message": user_input})  # Store user message

    try:
        # Fetch products if requested
        if "product" in user_input or "list all products" in user_input:
            cursor.execute("SELECT id, name, brand, price, category FROM products")
            products = cursor.fetchall()
            return {"products": products} if products else {"reply": "No products found."}

        # Fetch suppliers if requested
        elif "supplier" in user_input or "list all suppliers" in user_input:
            cursor.execute("SELECT id, name, contact_info FROM suppliers")
            suppliers = cursor.fetchall()
            return {"suppliers": suppliers} if suppliers else {"reply": "No suppliers found."}

        # Generate AI response
        else:
            history_text = "\n".join([f"{msg['sender']}: {msg['message']}" for msg in chat_history[-5:]])  # Last 5 messages
            ai_input = f"Previous conversation:\n{history_text}\nUser: {user_input}\nBot:"
            ai_response = generate_ai_response(ai_input)
            chat_history.append({"sender": "bot", "message": ai_response})
            return {"reply": ai_response}

    except Exception as e:
        logger.error(f"❌ Error processing chat request: {e}")
        return {"error": "An error occurred. Please try again later."}

@app.get("/")
async def home():
    return {"message": "Welcome to the AI Chatbot API! Use /docs to test the endpoints."}

@app.get("/products")
async def get_products():
    try:
        cursor.execute("SELECT id, name, brand, price, category FROM products")
        return {"products": cursor.fetchall()}
    except Exception as e:
        logger.error(f"❌ Error fetching products: {e}")
        return {"error": "Failed to fetch products."}

@app.get("/suppliers")
async def get_suppliers():
    try:
        cursor.execute("SELECT id, name, contact_info FROM suppliers")
        return {"suppliers": cursor.fetchall()}
    except Exception as e:
        logger.error(f"❌ Error fetching suppliers: {e}")
        return {"error": "Failed to fetch suppliers."}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("favicon.ico")
