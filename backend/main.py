from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all frontend requests
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

# Connect to MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Shrikrishna@123",  # Replace with your MySQL password
    database="chatbot_db"
)
cursor = db.cursor()

# Load a better AI model from Hugging Face
model_name = "tiiuae/falcon-7b-instruct"  # A free-to-use model


tokenizer = AutoTokenizer.from_pretrained(model_name)

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float32,  # Use float32 for CPU
    device_map={"": "cpu"}  # Force CPU usage
)


def generate_ai_response(prompt):
    inputs = tokenizer(prompt, return_tensors="pt").to("cpu")  # Using CPU mode
    output = model.generate(**inputs, max_length=200, temperature=0.7, do_sample=True)
    return tokenizer.decode(output[0], skip_special_tokens=True)


class Query(BaseModel):
    query: str

chat_history = []  # Stores previous user and bot messages

@app.post("/chat", operation_id="chat_with_ai")
async def chat(query: Query):
    user_input = query.query.lower()

    # Add the user's message to chat history
    chat_history.append({"sender": "user", "message": user_input})

    # Check if user asks for products
    if "product" in user_input or "list all products" in user_input or "show products" in user_input:
        cursor.execute("SELECT id, name, brand, price, category FROM products")
        products = cursor.fetchall()
        if products:
            bot_response = {"products": [dict(zip(["id", "name", "brand", "price", "category"], row)) for row in products]}
        else:
            bot_response = {"reply": "No products found."}

    # Check if user asks for suppliers
    elif "supplier" in user_input or "list all suppliers" in user_input or "show suppliers" in user_input:
        cursor.execute("SELECT id, name, contact_info FROM suppliers")
        suppliers = cursor.fetchall()
        if suppliers:
            bot_response = {"suppliers": [dict(zip(["id", "name", "contact_info"], row)) for row in suppliers]}
        else:
            bot_response = {"reply": "No suppliers found."}

    # Use AI model for general responses with chat history
    else:
        # Structure chat history properly
        history_text = "\n".join([f"{msg['sender']}: {msg['message']}" for msg in chat_history[-5:]])  # Last 5 messages
        ai_input = f"Previous conversation:\n{history_text}\nUser: {user_input}\nBot:"

        # Generate AI response
        ai_generated_text = generate_ai_response(ai_input)
        bot_response = {"reply": ai_generated_text}

    # Add bot response to chat history
    chat_history.append({"sender": "bot", "message": bot_response["reply"]})

    return bot_response

@app.get("/products")
async def get_products():
    cursor.execute("SELECT id, name, brand, price, category FROM products")
    products = cursor.fetchall()
    return {"products": [dict(zip(["id", "name", "brand", "price", "category"], row)) for row in products]}

@app.get("/suppliers")
async def get_suppliers():
    cursor.execute("SELECT id, name, contact_info FROM suppliers")
    suppliers = cursor.fetchall()
    return {"suppliers": [dict(zip(["id", "name", "contact_info"], row)) for row in suppliers]}
