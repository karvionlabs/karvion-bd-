import json
import os
from database import get_db_connection
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Using text-embedding-3-small (generates 1536 dimensional vectors)
embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")

def initialize_database():
    """Run the SQL migration to create tables and vector extension."""
    conn = get_db_connection()
    cur = conn.cursor()
    migration_path = os.path.join(os.path.dirname(__file__), "..", "migrations", "01_init_rag_tables.sql")
    with open(migration_path, 'r', encoding='utf-8') as file:
        cur.execute(file.read())
    conn.commit()
    cur.close()
    conn.close()
    print("Database tables initialized successfully.")

def ingest_seed_data():
    """Load JSON data, split into chunks, embed, and store in pgvector."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    seed_path = os.path.join(os.path.dirname(__file__), "seed_data.json")
    with open(seed_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Text splitter setup
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    
    for item in data:
        # Avoid duplicate ingestion for seed data based on title
        cur.execute("SELECT id FROM documents WHERE title = %s", (item["title"],))
        if cur.fetchone():
            print(f"Skipping '{item['title']}', already ingested.")
            continue
            
        chunks = text_splitter.split_text(item["content"])
        
        for chunk in chunks:
            # Generate vector embedding for the text chunk
            embedding = embeddings_model.embed_query(chunk)
            
            # Insert into database with pgvector formatting
            cur.execute(
                """
                INSERT INTO documents (title, content, agency_name, source_url, service_category, embedding)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (item["title"], chunk, item["agency_name"], item["source_url"], item["service_category"], embedding)
            )
            
    conn.commit()
    cur.close()
    conn.close()
    print("Seed data successfully ingested into pgvector.")

if __name__ == "__main__":
    initialize_database()
    ingest_seed_data()
