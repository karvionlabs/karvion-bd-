from database import get_db_connection
from langchain_openai import OpenAIEmbeddings

embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")

def retrieve_relevant_documents(query: str, category: str = None, top_k: int = 3):
    """
    Search for relevant documents in pgvector using cosine distance.
    If category is provided, filter by service_category.
    Returns formatted context with the original Source Link included.
    """
    # 1. Embed the search query
    query_embedding = embeddings_model.embed_query(query)
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 2. Vector search using cosine distance <=> operator
    sql = """
        SELECT title, content, agency_name, source_url, service_category,
               (embedding <=> %s::vector) as distance
        FROM documents
    """
    params = [query_embedding]
    
    # Optional filtering by agent domain
    if category:
        sql += " WHERE service_category = %s "
        params.append(category)
        
    sql += " ORDER BY distance ASC LIMIT %s"
    params.append(top_k)
    
    cur.execute(sql, params)
    results = cur.fetchall()
    
    cur.close()
    conn.close()
    
    # 3. Format the results strictly enforcing the source_url
    formatted_results = []
    for row in results:
        formatted_results.append(
            f"📌 **Title:** {row['title']}\n"
            f"🏢 **Agency:** {row['agency_name']}\n"
            f"📄 **Information:** {row['content']}\n"
            f"🔗 **Source Link:** {row['source_url']}"
        )
        
    if not formatted_results:
        return "দুঃখিত, আমাদের ডেটাবেসে এই সংক্রান্ত কোনো তথ্য পাওয়া যায়নি।"
        
    return "\n\n".join(formatted_results)
