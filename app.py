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

columns = """NAME, Example value - Paul Skenes, 
             YEAR, Example value - 2023,
             RD (round), Example value - 1,
             PICK, Example value - 1,
             TEAM, Example value - Pittsburgh Pirates,
             POS (position), Example value - RHP/LHP/OF/3B/C/TWP/SS,
             SCHOOL, Example value - LSU,
             TYPE, Example value - 4YR,
             ST, Example value - LA,
             SIGNED, Example value - N,
             BONUS, Example value - EMPTY/10,000.1"""


def get_chat_completion(query):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "You are creating MYSQL Queries for this given prompt. Assume everything to be related to baseball terminology. I have given some sample Column values: " + columns + "If you are not sure do not just use the example columns, just return nothing"},
                {"role": "user",
                 "content": "Create a mysql query given the following columns and user requirement. Ensure the query is contains or like instead of an exact match (case might be different as well). If the field is not clear, do a generic match on all columns. The table is baseball_table and end the query with a ;. Ensure you return a runnable sql query"},
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
        if sql_query == '"' or sql_query is None or len(sql_query) < 2 or sql_query == "":
            sql_query = """SELECT *
                        FROM baseball_table
                        WHERE NAME LIKE '%""" + query + """%' OR
                        CAST(YEAR AS VARCHAR) LIKE '%""" + query + """%' OR
                        CAST(RD AS VARCHAR) LIKE '%""" + query + """%' OR
                        CAST(PICK AS VARCHAR) LIKE '%""" + query + """%' OR
                        TEAM LIKE '%""" + query + """%' OR
                        POS LIKE '%""" + query + """%' OR
                        SCHOOL LIKE '%""" + query + """%' OR
                        TYPE LIKE '%""" + query + """%' OR
                        ST LIKE '%""" + query + """%' OR
                        SIGNED LIKE '%""" + query + """%' OR
                        BONUS LIKE '%""" + query + """%'"""
        print(f"sql query {sql_query}")
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
        total_pages = ceil(len(rows) / limit)

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
            "data": paginated_rows,
            "total_results": len(rows)
        }
        return jsonify(response_data)

