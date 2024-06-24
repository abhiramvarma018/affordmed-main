from flask import Flask, request, jsonify
import requests
import time
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Configuration
WINDOW_SIZE = 10
TEST_SERVER_URLS = {
    "prime": "http://20.244.56.144/test/primes",
    "fibonacci": "http://20.244.56.144/test/fibo",
    "even": "http://20.244.56.144/test/even",
    "random": "http://20.244.56.144/test/rand"
}
QUALIFIED_IDS = {"0": "prime", "1": "fibonacci", "2": "even", "3": "random"}
window = []

# Get the access token from the environment variables
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

def fetch_numbers(qualifier):
    url = TEST_SERVER_URLS[qualifier]
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    try:
        response = requests.get(url, headers=headers, timeout=0.5)
        print(f"Request to {url} returned status code {response.status_code}")
        if response.status_code == 200:
            print(f"Response JSON: {response.json()}")
            return response.json().get("numbers", [])
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except requests.exceptions.Timeout:
        print(f"Request to {url} timed out")
    except Exception as e:
        print(f"An error occurred: {e}")
    return []

@app.route('/numbers/<qualifier>', methods=['GET'])
def get_numbers(qualifier):
    if qualifier not in QUALIFIED_IDS:
        return jsonify({"error": "Invalid qualifier"}), 400

    qualifier_key = QUALIFIED_IDS[qualifier]
    numbers = fetch_numbers(qualifier_key)
    
    global window
    previous_window = window[:]
    
    for number in numbers:
        if number not in window:
            if len(window) >= WINDOW_SIZE:
                window.pop(0)
            window.append(number)

    avg = sum(window) / len(window) if window else 0

    response = {
        "numbers": numbers,
        "windowPrevState": previous_window,
        "windowCurrState": window,
        "avg": round(avg, 2)
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(port=9876)
