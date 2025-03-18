import os
import requests
import yfinance as yf
import subprocess

from cs50 import SQL
from yahoo_fin import stock_info
from flask import Flask, flash, redirect, render_template, request, session, jsonify, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///project.db")

def set_success_flag(form_id, success_flag):
    db.execute("INSERT OR REPLACE INTO success_flags(user_id, form_id, success_flags) VALUES (?, ?, ?)",
               session["user_id"], form_id, success_flag)

def get_success_flag():
    rows = db.execute("SELECT form_id, success_flags FROM success_flags WHERE user_id = ?", session["user_id"])
    success_flags = {row["form_id"]: row["success_flags"] for row in rows}
    return success_flags


@app.route("/", methods=["POST", "GET"])
@login_required
def index():
    submissions = db.execute("SELECT * FROM submissions")
    username = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    success_flags = get_success_flag()

    return render_template("index.html", success_flags=success_flags, submissions=submissions, username=username[0]["username"])

@app.route("/submit/form_<int:form_id>", methods=["POST", "GET"])
def submit(form_id):
    week = request.form.get("form_id")
    inputValue = request.form.get("inputValue")
    favPset = request.form.get("fav_pset")
    if favPset == "":
        db.execute("INSERT INTO submissions (person, fav_pset, week_opinion, week, user_id) VALUES ((SELECT username FROM users WHERE id = ?), ?, ?, ?, ?)",
               session["user_id"], "No favourite pset", inputValue, week, session["user_id"])
    else:
        db.execute("INSERT INTO submissions (person, fav_pset, week_opinion, week, user_id) VALUES ((SELECT username FROM users WHERE id = ?), ?, ?, ?, ?)",
                session["user_id"], favPset, inputValue, week, session["user_id"])
    set_success_flag(form_id, True)

    return redirect(url_for('index'))

@app.route("/reset/<int:reset_id>")
def reset(reset_id):
    db.execute("DELETE FROM submissions WHERE person = (SELECT username FROM users WHERE id = ?) AND week = ?", session["user_id"], reset_id)
    db.execute("DELETE FROM success_flags WHERE user_id = ? AND form_id = ?", session["user_id"], reset_id)
    return redirect(url_for('index'))

@app.route("/edit/<int:edit_id>", methods=["POST", "GET"])
def edit(edit_id):
    data = request.get_json()
    updatedText = data.get("text")
    if updatedText:
        db.execute("UPDATE submissions SET week_opinion = ? WHERE user_id = ? AND week = ?", updatedText, session["user_id"], edit_id)
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route("/login", methods=["POST", "GET"])
def login():
    session.clear()

    if request.method == "POST":
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400
        username = data.get("username")
        password = data.get("password")
        if not username:
            return jsonify({"error": "Missing username"}), 400
        elif not password:
            return jsonify({"error": "Missing password"}), 400

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return jsonify({"error": "Invalid username or password"}), 400

        session["user_id"] = rows[0]["id"]
        return jsonify({"success": True, "redirect": "/"})
    else:
        return render_template("login.html")

@app.route("/change_pass", methods=["POST", "GET"])
def change_pass():
    if request.method == "POST":
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400
        currPass = data.get("currPass")
        newPass = data.get("newPass")
        rNewPass = data.get("rNewPass")
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        if not currPass or not newPass or not rNewPass:
            return jsonify({"error": "Missing password"}), 400
        if not check_password_hash(rows[0]["hash"], currPass):
            return jsonify({"error": "Invalid Password"}), 400
        if newPass != rNewPass:
            return jsonify({"error": "Passwords don't match"}), 400

        db.execute("UPDATE users SET hash = ? WHERE id = ?", generate_password_hash(newPass, method='scrypt', salt_length=16), session["user_id"])
        return jsonify({"message": "You have succesfully changed your password","success": True, "redirect": "/"})
    else:
        username = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        return render_template("changepass.html", username=username[0]["username"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400
        if not data.get("username"):
            return jsonify({"error": "Missing username"}), 400
        if not data.get("password") or not data.get("r_password"):
            return jsonify({"error": "Missing password"}), 400
        if data.get("password") != data.get("r_password"):
            return jsonify({"error": "Passwords don't match"}), 400
        try:
            db.execute("INSERT INTO users (username, hash) VALUES(?, ?)",
                       data.get("username"), generate_password_hash(data.get("password"), method='scrypt', salt_length=16))
            return jsonify({"success": True, "redirect": "/"})
        except ValueError:
            return jsonify({"error": "User already taken"}), 400
        except RuntimeError:
            return jsonify({"error": "Error"}), 400
    else:
        return render_template("register.html")

@app.route("/stocks", methods=["POST", "GET"])
def stocks():
    username = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    return render_template("stocks.html", username=username[0]["username"])

@app.route("/get_stocks/<symbol>")
def get_stocks(symbol):
    try:
        stock = yf.Ticker(symbol)
        price = stock.history(period="1d")["Close"].iloc[-1]  # Latest closing price
        company_name = stock.info["longName"]
        return jsonify({"symbol": symbol, "price": round(price, 2), "company_name": company_name})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/stock-info")
def stockInfo():
    symbol = request.args.get("symbol")
    API_KEY = "pzwNHHnyl5Yh/oDW9qenYl7xAWLHE4Q/maUmDWQZQ3s="
    if not symbol:
        return "Stock symbol is required", 400
    try:
        stock = yf.Ticker(symbol)
        stock_info = stock.info
        company_name = stock_info.get("longName", "Unknown Company")
        company_nameClean= company_name.replace("'", " ").replace(",", " ").replace(".", " ")
        company_nameFirst = company_nameClean.split()

        url = f"https://api.brandfetch.io/v2/brands/{company_nameFirst[0].lower()}.com"
        headers = {
            "Authorization": f"Bearer {API_KEY}"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            company = response.json()
            logo_url = None
            for logo in company.get("logos", []):
                if logo.get("theme") == "dark":
                    logo_url = logo["formats"][0]["src"]
                    break
            company_information = company.get("company", {})
            company_info = {
                "logo": logo_url,
                "description": company.get("description", "Description not available"),
                "employees": company_information.get("employees"),
                "foundation": company_information.get("foundedYear", 'N/A'),
                "website": company.get("domain", "noDomain")
            }

            stock_data = {
                "symbol": symbol,
                "company_name": company_name,
                "sector": stock_info["sector"],
                "industry": stock_info["industry"],
                "price": stock_info.get("regularMarketPrice", "N/A"),
                "currency": stock_info.get("currency", "USD"),
                "market_cap": stock_info.get("marketCap", "N/A"),
                "previous_close": stock_info.get("previousClose", "N/A"),
                "open_price": stock_info.get("open", "N/A"),
                "day_high": stock_info.get("dayHigh", "N/A"),
                "day_low": stock_info.get("dayLow", "N/A"),
                "pe_ratio": stock_info['trailingPE'],
                "next_earnings_date": stock.calendar['Earnings Date'][0],
                "dividend_yield": stock_info.get('dividendYield', 'N/A')
            }

            return render_template("stock-info.html", stock=stock_data, company=company_info)

        else:
            return "Error"

    except Exception as e:
        return {"error": f"Failed to fetch data for {symbol}: {str(e)}"}
