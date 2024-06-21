from flask import Flask, request, render_template
import hashlib
import hmac
import time

import env

app = Flask(__name__)

# Replace with your bot token
BOT_TOKEN = env.BOT_TOKEN


def verify_telegram_auth(auth_data):
    check_hash = auth_data['hash']
    auth_data.pop('hash')

    data_check_arr = [f"{key}={value}" for key, value in sorted(auth_data.items())]
    data_check_string = "\n".join(data_check_arr)

    secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()
    hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if hash != check_hash:
        return False
    if time.time() - int(auth_data['auth_date']) > 86400:
        return False

    return True


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/handle_auth')
def handle_auth():
    auth_data = request.args.to_dict()

    if verify_telegram_auth(auth_data):
        # Authorized user
        user = auth_data
        # You can now save user info to your database or perform other actions
        return f"Hello, {user['first_name']}!"
    else:
        return "Unauthorized", 403


if __name__ == '__main__':
    app.run(debug=True)
