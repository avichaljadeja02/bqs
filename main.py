import sqlite3
from flask import Flask, request, jsonify
import openai
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

openAi_key = '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'

# Set up your OpenAI API credentials
openai.api_key = openAi_key
openai.Model.list()

columns = """PLAYER Paul Skenes, 
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
                 "content": "Create a mysql query given the following columns and user requirement. The table is baseball_table"},
                {"role": "assistant", "content": query},
            ],
            temperature=0.02,
            max_tokens=3596,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        print(f"Got a response from OpenAI for query {query}")
        return response['choices'][0]['message']['content']
    except:
        print(f"failed{query}")


@app.route('/api/search', methods=['GET'])
def query_search():
    query = request.args.get('q', '').lower()
    print("Got request for " + query)

    if not query:
        return jsonify([])
    sqlQuery = get_chat_completion(query)
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    rows = []
    try:
        cursor.execute(sqlQuery)

        # Fetch all rows from the result set
        rows = cursor.fetchall()

        # Display the fetched data
        for row in rows:
            print(row)
    except sqlite3.Error as e:
        print(f"Error fetching data: {e}")
    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()
        return jsonify(rows)

if __name__ == '__main__':
    app.run(port=5000)
