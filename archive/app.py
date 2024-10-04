# app.py

# Standard library imports
import threading
import time
import os
import uuid
import html

# Flask imports
from flask import Flask, render_template, request, Response, stream_with_context, abort, redirect, url_for, jsonify

from markupsafe import Markup

# Local imports
from my_agent.agent import run_agent
from my_agent.utils.config import Config

app = Flask(__name__, 
            template_folder='templates',
            static_folder='my_agent/static',
            static_url_path='/my_agent/static')  # This should work fine with your current structure
app.config['EXPLAIN_TEMPLATE_LOADING'] = True  # This will log template loading info
config = Config()
logger = config.get_logger('App')

# Global dictionary to hold states for each session
session_states = {}

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start():
    # Sanitize user input
    query = request.form.get('query', '').strip()

    # Remove any potential HTML tags (basic sanitization)
    query = html.escape(query)

    # Now, 'query' is a plain string
    search_terms = [query]  # Use the sanitized query

    session_id = str(uuid.uuid4())
    initial_state = {
        "search_terms": search_terms,
        "urls_to_be_processed": [],
        "files_to_be_processed": [],
        "log_messages": [],
        "messages": []
    }

    # Start the agent workflow
    try:
        final_state = run_agent(initial_state)
        return jsonify({"session_id": session_id, "message": "Agent workflow started successfully."})
    except Exception as e:
        app.logger.error(f"An error occurred during the agent workflow: {str(e)}")
        return jsonify({"error": "An error occurred during the agent workflow."}), 500

@app.route('/stream')
def stream():
    session_id = request.args.get('session_id')
    if not session_id or session_id not in session_states:
        abort(404)
    
    def generate():
        state = session_states[session_id]
        last_log_index = 0
        while True:
            if 'log_messages' in state:
                while last_log_index < len(state['log_messages']):
                    yield f"data:{state['log_messages'][last_log_index]}\n\n"
                    last_log_index += 1
            if state.get('completed', False):
                yield "data:END\n\n"
                break
            time.sleep(0.1)
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', message="Page not found"), 404

@app.errorhandler(500)
def internal_server_error(e):
    logger.exception(f"An error occurred: {e}")
    return render_template('error.html', message="An unexpected error occurred. Please try again later."), 500

if __name__ == '__main__':
    app.run(debug=True)
