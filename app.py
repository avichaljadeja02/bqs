import os
import sqlite3
from flask import Flask, request, jsonify
import openai
from flask_cors import CORS
from math import ceil

app = Flask(__name__)
CORS(app)

openAi_key = os.getenv('key')
# Set up your OpenAI API credentials
openai.api_key = openAi_key
openai.Model.list()

columns = """NAME Paul Skenes, 
             YEAR 2023,
             RD 1,
             PICK 1,
             TEAM Pittsburgh Pirates,
             POS RHP/LHP/OF/3B/C/TWP/SS,
             SCHOOL LSU,
             TYPE 4YR,
             ST LA,
             SIGNED N,
             BONUS EMPTY/10,000.1"""


def get_chat_completion(query):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "You are creating MYSQL Queries for this given prompt. Assume everything to be related to baseball terminology. I have given some sample Column values: " + columns},
                {"role": "user",
                 "content": "Create a mysql query given the following columns and user requirement. Ensure the query is contains or like instead of an exact match (case might be different as well). If the field is not clear, assume it is on name The table is baseball_table"},
                {"role": "assistant", "content": query},
            ],
            temperature=0.02,
            max_tokens=3596,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        start_index = response['choices'][0]['message']['content'].find("SELECT")
        end_index = response['choices'][0]['message']['content'].find(";", start_index) + 1

        # Extract the SQL query
        sql_query = response['choices'][0]['message']['content'][start_index:end_index]

        print(f"Got a response from OpenAI for query {query} response {sql_query}")
        return sql_query
    except:
        print(f"failed {query}")


@app.route('/api/search', methods=['GET'])
def query_search():
    query = request.args.get('q', '')
    page = int(request.args.get('page', 1))  # Default page is 1
    limit = int(request.args.get('limit', 10))  # Default limit is 10

    print(f"Got request for '{query}', page {page}, limit {limit}")

    if not query:
        return jsonify([])

    sqlQuery = get_chat_completion(query)
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    rows = []
    paginated_rows = []
    total_pages = 0  # Variable to store the total number of pages

    try:
        cursor.execute(sqlQuery)
        rows = cursor.fetchall()
        total_pages = ceil(len(rows) / limit)  # Calculate total pages

        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_rows = rows[start_idx:end_idx]
    except sqlite3.Error as e:
        print(f"Error fetching data: {e}")
    finally:
        cursor.close()
        conn.close()
        response_data = {
            "total_pages": total_pages,
            "data": paginated_rows
        }
        return jsonify(response_data)
