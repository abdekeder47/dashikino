from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import os
import random
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ethio_bet_secure_key_v18')
@app.route('/google32f97bf68dfe6928.html')
def google_verify():
    return "google-site-verification: google32f97bf68dfe6928.html"
users_db = {
    "0997384093": {
        "password": generate_password_hash 
        "balance": 100000.00, 
        "is_admin": True
    }
}

deposit_requests = []
withdraw_requests = []
global_bet_history = []
aviator_history_list = ["2.10x", "1.45x", "3.20x"]
keno_recent_draws = []

# ==========================================
# BINGO GENERATOR & STATE MANAGEMENT
# ==========================================
def generate_bingo_card(card_id):
    random.seed(card_id)
    card = {
        'B': random.sample(range(1, 16), 5),
        'I': random.sample(range(16, 31), 5),
        'N': random.sample(range(31, 46), 5),
        'G': random.sample(range(46, 61), 5),
        'O': random.sample(range(61, 76), 5)
    }
    card['N'][2] = "FREE"  # Center FREE space
    return card

BINGO_CARDS = {i: generate_bingo_card(i) for i in range(1, 101)}

bingo_rooms = {
    10: {"players": {}, "timer": 30, "status": "WAITING", "drawn": [], "pot": 0.0, "winners": []},
    30: {"players": {}, "timer": 30, "status": "WAITING", "drawn": [], "pot": 0.0, "winners": []},
    50: {"players": {}, "timer": 30, "status": "WAITING", "drawn": [], "pot": 0.0, "winners": []},
    100: {"players": {}, "timer": 30, "status": "WAITING", "drawn": [], "pot": 0.0, "winners": []}
}

KENO_ODDS = {
    1: {1: 3.5},
    2: {1: 1.0, 2: 10.0},
    3: {0: 0.0, 1: 0.0, 2: 2.0, 3: 50.0},
    4: {2: 1.5, 3: 10.0, 4: 80.0},
    5: {2: 1.0, 3: 3.0, 4: 30.0, 5: 150.0},
    6: {3: 2.0, 4: 15.0, 5: 60.0, 6: 500.0},
    7: {0: 1.0, 3: 2.0, 4: 4.0, 5: 20.0, 6: 80.0, 7: 1000.0},
    8: {0: 1.0, 4: 5.0, 5: 15.0, 6: 50.0, 7: 200.0, 8: 2000.0},
    9: {0: 2.0, 4: 2.0, 5: 10.0, 6: 25.0, 7: 125.0, 8: 1000.0, 9: 5000.0},
    10: {0: 2.0, 5: 5.0, 6: 30.0, 7: 100.0, 8: 300.0, 9: 2000.0, 10: 10000.0}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="am">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Ethio Bet - Premium Gaming Platform</title>
    <style>
        :root {
            --bg-dark: #12181f;
            --card-bg: #1a222d;
            --accent-green: #00e676;
            --accent-pink: #e91e63;
            --accent-orange: #ff9800;
            --accent-yellow: #f5a623;
            --text-main: #ffffff;
            --text-muted: #8b949e;
            --border-color: #26323f;
        }

        * { box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 0; }
        body { background-color: var(--bg-dark); color: var(--text-main); padding: 8px; }

        .top-nav { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: #0c1015; border-radius: 8px; margin-bottom: 12px; border: 1px solid var(--border-color); }
        .logo-text { font-weight: 900; font-size: 20px; color: #ffffff; font-style: italic; letter-spacing: 0.5px; cursor: pointer; }
        .logo-text span { color: var(--accent-yellow); }
        .balance-container { display: flex; align-items: center; gap: 6px; }
        .balance-pill { background: #070a0d; border: 1px solid #1f2936; border-radius: 20px; padding: 4px 10px; font-weight: bold; color: var(--accent-green); font-size: 13px; }
        .btn-deposit { background: var(--accent-green); color: #000; border: none; padding: 5px 10px; border-radius: 20px; font-weight: bold; font-size: 11px; cursor: pointer; }
        .btn-withdraw { background: var(--accent-orange); color: #000; border: none; padding: 5px 10px; border-radius: 20px; font-weight: bold; font-size: 11px; cursor: pointer; }
        .btn-logout { background: #ff1744; color: #fff; text-decoration: none; padding: 5px 8px; border-radius: 6px; font-size: 11px; font-weight: bold; }

        .auth-container { max-width: 420px; margin: 20px auto; background: #18222d; border-radius: 10px; overflow: hidden; border: 1px solid var(--border-color); box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
        .auth-header { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: #0e1620; border-bottom: 1px solid var(--border-color); }
        .auth-top-btns { display: flex; gap: 8px; }
        .btn-top-login { background: #2b3644; color: #fff; border: none; padding: 6px 14px; border-radius: 6px; font-weight: bold; font-size: 13px; cursor: pointer; }
        .btn-top-reg { background: var(--accent-yellow); color: #000; border: none; padding: 6px 14px; border-radius: 6px; font-weight: bold; font-size: 13px; cursor: pointer; }

        .auth-title-bar { display: flex; align-items: center; gap: 10px; padding: 14px 16px; font-size: 16px; font-weight: 800; color: #fff; border-bottom: 1px solid var(--border-color); }
        .back-arrow { background: #2b3644; color: #fff; width: 28px; height: 28px; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 14px; cursor: pointer; }

        .auth-tabs { display: grid; grid-template-columns: repeat(4, 1fr); background: #0f1722; border-bottom: 1px solid var(--border-color); }
        .auth-tab { padding: 12px 4px; text-align: center; font-size: 11px; color: var(--text-muted); cursor: pointer; border-bottom: 2px solid transparent; display: flex; flex-direction: column; align-items: center; gap: 4px; }
        .auth-tab.active { color: #fff; background: #18222d; border-bottom: 2px solid var(--accent-yellow); font-weight: bold; }

        .auth-body { padding: 20px 16px; }
        .phone-input-group { display: flex; gap: 8px; margin-bottom: 14px; }
        .country-code-box { background: #ffffff; color: #000; border-radius: 6px; padding: 0 10px; display: flex; align-items: center; gap: 6px; font-weight: bold; font-size: 13px; }
        .flag-icon { width: 20px; height: 14px; object-fit: cover; border-radius: 2px; }
        .auth-input { width: 100%; padding: 12px; background: #ffffff; color: #000; border: 1px solid #ccc; border-radius: 6px; font-size: 14px; font-weight: 600; outline: none; }
        .password-input-wrapper { position: relative; margin-bottom: 14px; }
        .eye-icon { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); color: #555; cursor: pointer; font-size: 16px; }

        .auth-options { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; font-size: 13px; }
        .remember-me { display: flex; align-items: center; gap: 8px; color: #ccc; cursor: pointer; }
        .forgot-pass { color: var(--accent-yellow); text-decoration: underline; cursor: pointer; font-weight: 500; }

        .btn-login-submit { width: 100%; background: var(--accent-yellow); color: #000; border: none; padding: 12px; border-radius: 6px; font-weight: 900; font-size: 15px; cursor: pointer; margin-bottom: 16px; }
        .register-footer { text-align: center; font-size: 13px; color: var(--text-muted); }
        .register-footer a { color: var(--accent-yellow); text-decoration: underline; font-weight: bold; cursor: pointer; }

        .home-game-menu { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 15px; }
        
        .game-banner-card { background: #1e2836; border-radius: 12px; overflow: hidden; border: 2px solid var(--border-color); cursor: pointer; position: relative; box-shadow: 0 8px 20px rgba(0,0,0,0.6); transition: transform 0.2s ease, border-color 0.2s ease; display: flex; flex-direction: column; justify-content: space-between; min-height: 200px; }
        .game-banner-card:hover { transform: translateY(-4px); border-color: var(--accent-yellow); }

        .card-shamo { background: radial-gradient(circle at center, #800000 0%, #300000 100%); }
        .card-birabiro { background: radial-gradient(circle at center, #2e1a00 0%, #110900 100%); }
        .card-bingo { background: radial-gradient(circle at center, #004d40 0%, #001a14 100%); }

        .card-brand-header { padding: 6px 8px; font-size: 10px; font-weight: 800; color: #fff; display: flex; justify-content: space-between; align-items: center; background: rgba(0,0,0,0.3); }
        .card-center-content { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 10px 4px; text-align: center; }

        .shamo-title { font-size: 28px; font-weight: 900; color: #ffe600; text-shadow: 2px 2px 0px #d32f2f; }
        .birabiro-title { font-size: 24px; font-weight: 900; color: #ff9800; }
        .bingo-title { font-size: 26px; font-weight: 900; color: #00e676; text-shadow: 0 0 10px rgba(0,230,118,0.5); }

        .card-footer-btn { background: rgba(0,0,0,0.5); padding: 6px; text-align: center; font-weight: bold; font-size: 10px; color: #fff; border-top: 1px solid rgba(255,255,255,0.1); }

        .game-nav-bar { display: flex; gap: 4px; margin-bottom: 12px; }
        .nav-btn { flex: 1; background: var(--card-bg); color: var(--text-muted); border: 1px solid var(--border-color); padding: 8px 4px; border-radius: 6px; font-weight: bold; font-size: 11px; cursor: pointer; text-align: center; }
        .nav-btn.active { background: #26323f; color: #fff; border-color: var(--accent-yellow); }

        .game-top-bar { display: flex; justify-content: space-between; align-items: center; position: relative; margin-bottom: 8px; padding: 4px 8px; background: #1a222d; border-radius: 8px; border: 1px solid var(--border-color); }
        .menu-btn { background: #26323f; border: 1px solid var(--border-color); color: #fff; font-size: 18px; font-weight: bold; width: 32px; height: 32px; border-radius: 6px; cursor: pointer; display: flex; align-items: center; justify-content: center; }
        .dropdown-menu-box { display: none; position: absolute; top: 40px; right: 8px; background: #1a222d; border: 1px solid var(--border-color); border-radius: 8px; box-shadow: 0 8px 20px rgba(0,0,0,0.8); z-index: 50; width: 180px; overflow: hidden; }
        .dropdown-item { padding: 10px 12px; font-size: 12px; color: #fff; cursor: pointer; display: flex; align-items: center; gap: 8px; border-bottom: 1px solid #26323f; }

        /* BINGO SPECIFIC STYLES */
        .bingo-card-container { background: #12181f; border: 1px solid var(--border-color); border-radius: 8px; padding: 6px; margin-bottom: 10px; }
        .bingo-card-container.winning-card { border: 2px solid var(--accent-yellow) !important; box-shadow: 0 0 15px rgba(245, 166, 35, 0.6); }
        .bingo-card-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px; background: #0c1015; padding: 8px; border-radius: 8px; }
        .bingo-header-cell { background: var(--accent-yellow); color: #000; font-weight: 900; text-align: center; padding: 6px; border-radius: 4px; font-size: 14px; }
        .bingo-cell { background: #1a222d; color: #fff; border: 1px solid var(--border-color); text-align: center; padding: 10px 0; font-weight: bold; font-size: 12px; border-radius: 4px; cursor: pointer; }
        .bingo-cell.marked { background: var(--accent-green); color: #000; font-weight: 900; box-shadow: 0 0 8px var(--accent-green); }
        .bingo-cell.free { background: var(--accent-pink); color: #fff; }

        .history-table { width: 100%; border-collapse: collapse; font-size: 11px; text-align: left; }
        .history-table th { background: #0c1015; padding: 6px; color: var(--text-muted); border-bottom: 1px solid var(--border-color); }
        .history-table td { padding: 6px; border-bottom: 1px solid #1a222d; }
        .badge-win { color: var(--accent-green); font-weight: bold; }
        .badge-loss { color: #ff1744; font-weight: bold; }

        .modal-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); justify-content: center; align-items: center; z-index: 100; }
        .modal-box { background: var(--card-bg); padding: 16px; border-radius: 10px; width: 90%; max-width: 380px; border: 1px solid var(--border-color); text-align: center; }
        .form-control { width: 100%; padding: 10px; background: #0c1015; border: 1px solid var(--border-color); color: #fff; border-radius: 6px; margin-bottom: 10px; font-size: 13px; }
        
        .btn-start-bet { background: linear-gradient(180deg, #00e676 0%, #00a855 100%); color: #000; border: none; border-radius: 8px; font-weight: 900; padding: 10px 0; cursor: pointer; text-align: center; width: 100%; transition: all 0.2s ease; }
        .btn-start-bet.cancel { background: linear-gradient(180deg, #ff1744 0%, #b71c1c 100%) !important; color: #fff !important; }
        .btn-start-bet.flying { background: linear-gradient(180deg, #ffea00 0%, #f57f17 100%) !important; color: #000 !important; }
        .btn-start-bet.won { background: linear-gradient(180deg, #00e676 0%, #00a855 100%) !important; color: #000 !important; }

        .number-picker { background: #0c1015; border-radius: 6px; border: 1px solid var(--border-color); display: flex; align-items: center; justify-content: space-between; padding: 2px 4px; margin-bottom: 6px; }
        .num-btn { background: #26323f; color: #fff; border: none; width: 28px; height: 28px; border-radius: 4px; font-size: 16px; font-weight: bold; cursor: pointer; }
        .num-input { background: transparent; border: none; color: #fff; text-align: center; font-size: 14px; font-weight: bold; width: 60px; outline: none; }
        .bet-card { background: var(--card-bg); border-radius: 10px; border: 1px solid var(--border-color); padding: 10px; }
        .keno-balls-preview { display: flex; gap: 4px; margin-bottom: 6px; }
        .k-ball { width: 20px; height: 20px; background: radial-gradient(circle at 30% 30%, #ffeb3b, #f57f17); color: #000; border-radius: 50%; font-size: 9px; font-weight: 900; display: flex; align-items: center; justify-content: center; }
        .multiplier-bar { display: flex; gap: 6px; overflow-x: auto; padding: 4px 0; margin-bottom: 8px; white-space: nowrap; height: 32px; align-items: center; }
        .mult-tag { background: #1a222d; border-radius: 4px; padding: 2px 8px; font-size: 11px; font-weight: bold; border: 1px solid var(--border-color); display: inline-block; }
        .mult-tag.green { color: var(--accent-green); }
        .mult-tag.pink { color: var(--accent-pink); }
        .mult-tag.blue { color: #29b6f6; }
        
        .aviator-screen { background: radial-gradient(circle at center, #1e2836 0%, #0c1015 100%); height: 140px; border-radius: 12px; border: 1px solid var(--border-color); position: relative; display: flex; flex-direction: column; justify-content: center; align-items: center; margin-bottom: 10px; overflow: hidden; }
        .aviator-mult { font-size: 32px; font-weight: 900; color: #fff; z-index: 2; }
        .plane-img { font-size: 32px; position: absolute; bottom: 10px; left: 10px; transition: transform 0.05s linear; z-index: 3; filter: drop-shadow(0 0 8px rgba(255, 23, 68, 0.9)); }
        .aviator-canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; pointer-events: none; }
        
        .dual-bet-container { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 10px; }
        .auto-controls-row { display: flex; justify-content: space-between; align-items: center; font-size: 10px; color: var(--text-muted); margin-bottom: 6px; background: #0c1015; padding: 4px 6px; border-radius: 4px; }
        .auto-cash-input { background: #1a222d; border: 1px solid var(--border-color); color: #fff; width: 45px; text-align: center; font-size: 10px; border-radius: 3px; }
        .live-bets-panel { background: var(--card-bg); border-radius: 8px; padding: 8px; border: 1px solid var(--border-color); margin-bottom: 10px; }
        .live-bets-title { font-size: 11px; font-weight: bold; color: var(--text-muted); margin-bottom: 6px; display: flex; justify-content: space-between; border-bottom: 1px solid var(--border-color); padding-bottom: 4px; }
        .live-bet-row { display: flex; justify-content: space-between; font-size: 11px; padding: 4px 0; border-bottom: 1px solid #1a222d; align-items: center; }
        .keno-board-container { background: var(--card-bg); border-radius: 10px; padding: 10px; border: 1px solid var(--border-color); margin-bottom: 10px; }
        .keno-header { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 11px; color: var(--text-muted); }
        .keno-grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 3px; }
        .keno-num { background: #12181f; border: 1px solid #232f3e; color: #fff; text-align: center; padding: 6px 0; border-radius: 4px; font-size: 9px; font-weight: bold; cursor: pointer; }
        .keno-num.selected { background: #0288d1; color: #fff; }
        .keno-num.drawn-regular { background: #29b6f6; color: #000; }
        .keno-num.ticket-matched { background: var(--accent-yellow) !important; color: #000 !important; font-weight: 900; }
        .keno-spinning-box-container { display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 10px; background: #0c1015; padding: 8px; border-radius: 8px; border: 1px solid var(--border-color); }
        .spinning-label { font-size: 11px; color: var(--text-muted); font-weight: bold; }
        .spinning-slot { width: 50px; height: 35px; background: #1a222d; border: 2px solid var(--accent-yellow); border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 16px; font-weight: 900; color: var(--accent-yellow); }
        .recent-keno-detailed-box { background: #0c1015; border-radius: 8px; padding: 10px; border: 1px solid var(--border-color); margin-bottom: 10px; }
        .recent-keno-title { font-size: 11px; font-weight: bold; color: var(--accent-yellow); margin-bottom: 6px; display: flex; justify-content: space-between; border-bottom: 1px solid var(--border-color); padding-bottom: 4px; }
        .keno-history-row { font-size: 10px; padding: 4px 0; border-bottom: 1px solid #1a222d; display: flex; flex-direction: column; gap: 3px; }
        .keno-history-balls { display: flex; flex-wrap: wrap; gap: 2px; }
        .kh-ball { background: #1a222d; border: 1px solid #29b6f6; color: #29b6f6; padding: 1px 4px; border-radius: 3px; font-size: 8px; font-weight: bold; }
        
        /* 1. KENO HISTORY HIGHLIGHT STYLES (MATCHING TICKETS/HITS) */
        .kh-ball.hit-match { background: var(--accent-yellow) !important; color: #000 !important; border-color: #fff !important; font-weight: 900 !important; box-shadow: 0 0 6px var(--accent-yellow); }

        .t-num-badge { background: #26323f; border: 1px solid #37474f; color: #fff; padding: 2px 4px; border-radius: 4px; font-size: 9px; display: inline-block; margin: 1px; }
        .t-num-badge.hit { background: var(--accent-yellow) !important; color: #000 !important; font-weight: 900; }
        
        .stat-summary-box { background: #0c1015; border: 1px solid var(--border-color); border-radius: 6px; padding: 6px 10px; margin-bottom: 8px; font-size: 11px; font-weight: bold; color: var(--accent-yellow); display: flex; justify-content: space-between; align-items: center; }
    </style>
</head>
<body>

    {% if not logged_in %}
    <div class="auth-container">
        <div class="auth-header">
            <div class="logo-text">ETHIO<span>BET</span></div>
            <div class="auth-top-btns">
                <button class="btn-top-login">Log in</button>
                <button class="btn-top-reg" onclick="register()">Registration</button>
            </div>
        </div>

        <div class="auth-title-bar">
            <div class="back-arrow">←</div>
            <span>LOG IN</span>
        </div>

        <div class="auth-tabs">
            <div class="auth-tab"><span class="auth-tab-icon">✉️</span><span>Email</span></div>
            <div class="auth-tab active"><span class="auth-tab-icon">📱</span><span>Phone</span></div>
            <div class="auth-tab"><span class="auth-tab-icon">💬</span><span>Code</span></div>
            <div class="auth-tab"><span class="auth-tab-icon">👥</span><span>Social</span></div>
        </div>

        <div class="auth-body">
            <div class="phone-input-group">
                <div class="country-code-box">
                    <img src="https://flagcdn.com/w40/et.png" class="flag-icon" alt="ET Flag">
                    <span>+251</span>
                </div>
                <input type="text" id="auth-phone" class="auth-input" placeholder="Phone number">
            </div>

            <div class="password-input-wrapper">
                <input type="password" id="auth-password" class="auth-input" placeholder="Password*">
                <span class="eye-icon" onclick="togglePasswordVisibility()">👁️</span>
            </div>

            <div class="auth-options">
                <label class="remember-me"><input type="checkbox" checked><span>Remember me</span></label>
                <span class="forgot-pass">Forgot password?</span>
            </div>

            <button class="btn-login-submit" onclick="login()">LOG IN</button>

            <div class="register-footer">
                <span>Don't have an account? </span>
                <a onclick="register()">Register</a>
            </div>
        </div>
    </div>

    {% else %}
    <div class="top-nav">
        <div class="logo-text" onclick="showHomeScreen()">ETHIO<span>BET</span></div>
        <div class="balance-container">
            <div class="balance-pill"><span id="user-balance">{{ "%.2f"|format(balance) }}</span> ETB</div>
            <button class="btn-deposit" onclick="openDepositModal()">+ Dep</button>
            <button class="btn-withdraw" onclick="openWithdrawModal()">- With</button>
            {% if is_admin %}
            <a href="/admin" style="background: #0288d1; color: #fff; text-decoration: none; padding: 5px 8px; border-radius: 6px; font-size: 11px; font-weight: bold;">ADMIN</a>
            {% endif %}
            <a href="/logout" class="btn-logout">ውጣ</a>
        </div>
    </div>

    <div id="home-dashboard-view">
        <h3 style="font-size: 14px; color: var(--text-muted); margin-bottom: 10px; font-weight: bold;">የጨዋታ ምርጫዎች (SELECT GAME)</h3>
        <div class="home-game-menu">
            
            <div class="game-banner-card card-shamo" onclick="switchGame('keno')">
                <div class="card-brand-header">
                    <span>ETHIO<span>BET</span></span>
                </div>
                <div class="card-center-content">
                    <div class="keno-balls-preview">
                        <div class="k-ball">30</div>
                        <div class="k-ball">8</div>
                        <div class="k-ball">67</div>
                    </div>
                    <div class="shamo-title">ሻሞ</div>
                </div>
                <div class="card-footer-btn">PLAY KENO ▶</div>
            </div>

            <div class="game-banner-card card-birabiro" onclick="switchGame('aviator')">
                <div class="card-brand-header">
                    <span>ETHIO<span>BET</span></span>
                </div>
                <div class="card-center-content">
                    <div class="birabiro-title">በራሪው</div>
                    <div style="font-size: 30px;">✈️</div>
                </div>
                <div class="card-footer-btn">PLAY JET ▶</div>
            </div>

            <div class="game-banner-card card-bingo" onclick="switchGame('bingo')">
                <div class="card-brand-header">
                    <span>ETHIO<span>BET</span></span>
                </div>
                <div class="card-center-content">
                    <div class="bingo-title">ቢንጎ</div>
                    <div style="font-size: 30px;">🎱</div>
                </div>
                <div class="card-footer-btn">PLAY BINGO ▶</div>
            </div>

        </div>
    </div>

    <div class="game-nav-bar">
        <div class="nav-btn active" id="btn-nav-home" onclick="showHomeScreen()">🏠 HOME</div>
        <div class="nav-btn" id="btn-nav-keno" onclick="switchGame('keno')">🎱 ሻሞ</div>
        <div class="nav-btn" id="btn-nav-aviator" onclick="switchGame('aviator')">✈️ በራሪው</div>
        <div class="nav-btn" id="btn-nav-bingo" onclick="switchGame('bingo')">🎯 ቢንጎ</div>
        <div class="nav-btn" id="btn-nav-history" onclick="switchGame('history')">📜 HISTORY</div>
    </div>

    <!-- ================= AVIATOR SECTION ================= -->
    <div id="aviator-section" style="display: none;">
        <div class="game-top-bar">
            <span style="font-size: 12px; font-weight: bold; color: var(--accent-yellow);">በራሪው (JET ✈️)</span>
            <button class="menu-btn" onclick="toggleDropdownMenu(event, 'aviator-dropdown-menu')">⋮</button>
            <div class="dropdown-menu-box" id="aviator-dropdown-menu">
                <div class="dropdown-item" onclick="openAviatorLimitsModal()">⚙️ የጨዋታ ገደብ (Limits)</div>
                <div class="dropdown-item" onclick="openAviatorHistoryModal()">📜 የአቪዬተር ሂስትሪ</div>
            </div>
        </div>

        <div class="multiplier-bar" id="aviator-history-bar">
            <div class="mult-tag green">2.10x</div>
            <div class="mult-tag blue">1.45x</div>
            <div class="mult-tag pink">3.20x</div>
        </div>

        <div class="aviator-screen" id="aviator-screen-box">
            <canvas id="aviator-canvas" class="aviator-canvas"></canvas>
            <div class="aviator-mult" id="aviator-mult-display">1.00x</div>
            <!-- 2. JET ICON ✈️ REPLACED HERE -->
            <div class="plane-img" id="plane-icon" style="color: #ff1744;">✈️</div>
        </div>

        <div class="dual-bet-container">
            <div class="bet-card">
                <div class="number-picker">
                    <button class="num-btn" onclick="adjustBet(1, -5)">-</button>
                    <input type="number" class="num-input" id="aviator-bet-val-1" value="10.00" onchange="onManualBetChange(1, this.value)">
                    <button class="num-btn" onclick="adjustBet(1, 5)">+</button>
                </div>
                <div class="auto-controls-row">
                    <label style="display: flex; align-items: center; gap: 4px; cursor: pointer;">
                        <input type="checkbox" id="auto-cash-toggle-1" checked onchange="toggleAutoCashInput(1)"> አውቶ
                    </label>
                    <input type="text" class="auto-cash-input" id="auto-cash-val-1" value="2.00">
                </div>
                <button class="btn-start-bet" id="aviator-bet-btn-1" onclick="handleAviatorBtnClick(1)">
                    <span class="btn-title" id="aviator-btn-title-1">BET #1</span>
                    <span class="btn-sub" id="aviator-btn-sub-1">10.00 ETB</span>
                </button>
            </div>

            <div class="bet-card">
                <div class="number-picker">
                    <button class="num-btn" onclick="adjustBet(2, -5)">-</button>
                    <input type="number" class="num-input" id="aviator-bet-val-2" value="20.00" onchange="onManualBetChange(2, this.value)">
                    <button class="num-btn" onclick="adjustBet(2, 5)">+</button>
                </div>
                <div class="auto-controls-row">
                    <label style="display: flex; align-items: center; gap: 4px; cursor: pointer;">
                        <input type="checkbox" id="auto-cash-toggle-2" checked onchange="toggleAutoCashInput(2)"> አውቶ
                    </label>
                    <input type="text" class="auto-cash-input" id="auto-cash-val-2" value="2.00">
                </div>
                <button class="btn-start-bet" id="aviator-bet-btn-2" onclick="handleAviatorBtnClick(2)">
                    <span class="btn-title" id="aviator-btn-title-2">BET #2</span>
                    <span class="btn-sub" id="aviator-btn-sub-2">20.00 ETB</span>
                </button>
            </div>
        </div>

        <div class="live-bets-panel">
            <div class="stat-summary-box">
                <span>አጠቃላይ/ካሻውት: <span id="aviator-stat-ratio" style="color:#fff;">0/0</span></span>
                <span>የወጣ ብር: <span id="aviator-stat-totalwin" style="color:var(--accent-green);">0.00 ETB</span></span>
            </div>

            <div class="live-bets-title">
                <span>የአቪዬተር የቀጥታ መደቦች (LIVE BETS)</span>
                <span style="color: var(--accent-green);" id="aviator-live-count">0 Bets</span>
            </div>
            <div id="aviator-live-bets-list">
                <p style="font-size: 11px; color: var(--text-muted);">በዚህ ዙር የተመደበ የለም።</p>
            </div>
        </div>
    </div>

    <!-- ================= KENO SECTION ================= -->
    <div id="keno-section" style="display: none;">
        <div class="game-top-bar">
            <span style="font-size: 12px; font-weight: bold; color: var(--accent-yellow);">ሻሞ (KENO - Max 20 Tickets)</span>
            <button class="menu-btn" onclick="toggleDropdownMenu(event, 'keno-dropdown-menu')">⋮</button>
            <div class="dropdown-menu-box" id="keno-dropdown-menu">
                <div class="dropdown-item" onclick="openModal('keno-limits-modal')">⚙️ የጨዋታ ገደብ (Limits)</div>
                <div class="dropdown-item" onclick="openKenoHistoryModal()">📜 የኬኖ ታሪክ (History)</div>
            </div>
        </div>

        <div class="stat-summary-box">
            <span>በዚህ ዙር የተመደቡ አጠቃላይ የጨዋታዎች ብዛት፦</span>
            <span id="keno-total-round-bets" style="font-size: 13px; color: var(--accent-green);">0</span>
        </div>

        <div class="recent-keno-detailed-box">
            <div class="recent-keno-title">
                <span>ያለፉት 3 የኬኖ ጨዋታዎች ውጤት</span>
            </div>
            <div id="recent-keno-detailed-list">
                <div class="keno-history-row"><span>ጨዋታ #1: ጫን...</span></div>
                <div class="keno-history-row"><span>ጨዋታ #2: ጫን...</span></div>
                <div class="keno-history-row"><span>ጨዋታ #3: ጫን...</span></div>
            </div>
        </div>

        <div class="keno-spinning-box-container">
            <span class="spinning-label">እየተሽከረከረ የሚወጣ እጣ:</span>
            <div class="spinning-slot" id="keno-spinner-slot">--</div>
        </div>

        <div class="keno-board-container">
            <div class="keno-header">
                <span>1 እስከ 80 ቁጥሮችን ይምረጡ (ከ1 እስከ 10)</span>
                <span>ቀጣይ እጣ: <b id="keno-timer-display" style="color: var(--accent-pink);">45s</b></span>
            </div>
            <div class="keno-grid" id="keno-grid-board"></div>
        </div>

        <div class="bet-card" style="margin-bottom: 10px;">
            <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 8px;">
                <button style="flex: 1; padding: 10px; background: #29b6f6; color: #000; font-weight: 900; border:none; border-radius:6px; cursor:pointer;" onclick="selectRandomKenoNumbers()">
                    🎲 RANDOM PICK (በዘፍቀድ)
                </button>
                <button style="padding: 10px 14px; background: #ff1744; color: #fff; font-weight: bold; border:none; border-radius:6px; cursor:pointer;" onclick="clearKenoSelection()">
                    🧹 CLEAR
                </button>
            </div>
            <div style="display: flex; gap: 8px; align-items: center;">
                <div class="number-picker" style="flex: 1; margin-bottom: 0;">
                    <button class="num-btn" onclick="adjustKenoBet(-5)">-</button>
                    <input type="number" class="num-input" id="keno-bet-val" value="10.00" min="5" max="12000" onchange="onManualKenoBetChange(this.value)" style="width: 80px;">
                    <button class="num-btn" onclick="adjustKenoBet(5)">+</button>
                </div>
                <button style="flex: 1; padding: 10px; background: var(--accent-yellow); color: #000; font-weight: bold; border:none; border-radius:6px; cursor:pointer;" onclick="addKenoTicket()">
                    + ADD TICKET
                </button>
            </div>
        </div>

        <div class="live-bets-panel">
            <div class="live-bets-title">
                <span>የኬኖ የተመደቡ ቲኬቶች (<span id="keno-tickets-count">0</span>/20)</span>
                <button class="btn-start-bet" id="keno-place-all-btn" style="width: 100px; padding: 4px 0;" onclick="placeAllKenoBets()">
                    <span class="btn-title">PLACE ALL</span>
                </button>
            </div>
            <div id="keno-tickets-list">
                <p style="font-size: 11px; color: var(--text-muted);">ምንም የተዘጋጀ ቲኬት የለም።</p>
            </div>
        </div>
    </div>

    <!-- ================= BINGO SECTION ================= -->
    <div id="bingo-section" style="display: none;">
        <div class="game-top-bar">
            <span style="font-size: 12px; font-weight: bold; color: var(--accent-green);">75-BALL BINGO (ቢንጎ)</span>
            <button class="menu-btn" onclick="showHomeScreen()">❌</button>
        </div>

        <!-- BINGO MENU VIEW -->
        <div id="bingo-menu-view">
            <h3 style="font-size: 13px; color: var(--accent-yellow); margin-bottom: 8px;">1. የመደብ መጠን ይምረጡ (50 & 100 Added)</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px;">
                <button style="padding: 10px; background: #1a222d; border: 2px solid var(--accent-green); color: #fff; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 11px;" onclick="selectBingoStake(10)">
                    10 ETB Room
                </button>
                <button style="padding: 10px; background: #1a222d; border: 2px solid var(--accent-yellow); color: #fff; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 11px;" onclick="selectBingoStake(30)">
                    30 ETB Room
                </button>
                <button style="padding: 10px; background: #1a222d; border: 2px solid var(--accent-orange); color: #fff; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 11px;" onclick="selectBingoStake(50)">
                    50 ETB Room (New)
                </button>
                <button style="padding: 10px; background: #1a222d; border: 2px solid var(--accent-pink); color: #fff; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 11px;" onclick="selectBingoStake(100)">
                    100 ETB Room (New)
                </button>
            </div>

            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <h3 style="font-size: 13px; color: var(--accent-yellow);">2. ካርድ ይምረጡ (የተመረጡ: <span id="bingo-selected-count">0</span>)</h3>
                <div style="display: flex; gap: 6px;">
                    <button style="padding: 4px 8px; background: #0288d1; color: #fff; border: none; border-radius: 4px; font-weight: bold; font-size: 11px; cursor: pointer;" onclick="pickRandomBingoCard()">🎲 RANDOM</button>
                    <button style="padding: 4px 8px; background: #ff1744; color: #fff; border: none; border-radius: 4px; font-weight: bold; font-size: 11px; cursor: pointer;" onclick="clearAllBingoCards()">🧹 CLEAR</button>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; max-height: 180px; overflow-y: auto; background: #0c1015; padding: 8px; border-radius: 8px; border: 1px solid var(--border-color); margin-bottom: 12px;" id="bingo-card-selector">
            </div>

            <button class="btn-start-bet" style="padding: 12px;" onclick="joinBingoGame()">JOIN BINGO GAME ▶</button>
        </div>

        <!-- BINGO GAMEPLAY VIEW -->
        <div id="bingo-game-view" style="display: none;">
            <div style="display: flex; justify-content: space-between; align-items: center; background: #0c1015; padding: 8px; border-radius: 6px; margin-bottom: 8px; font-size: 11px;">
                <span>ካርዶች: <b id="bingo-player-count" style="color: var(--accent-green);">0</b></span>
                <span>ሁኔታ: <b id="bingo-room-status" style="color: var(--accent-yellow);">በቂ ተጫዋች በመጠባበቅ ላይ...</b></span>
                <span>ቆጠራ: <b id="bingo-room-timer" style="color: var(--accent-pink);">--</b></span>
            </div>

            <div style="text-align: center; margin-bottom: 8px; background: #1a222d; padding: 6px; border-radius: 6px;">
                <span style="font-size: 11px; color: var(--text-muted);">የወጣ ቁጥር / ፖት (POT):</span>
                <div id="bingo-current-call" style="font-size: 24px; font-weight: 900; color: var(--accent-yellow);">--</div>
                <div style="font-size: 11px; color: var(--accent-green);" id="bingo-pot-display">POT: 0 ETB</div>
            </div>

            <div id="bingo-cards-wrapper" style="max-height: 300px; overflow-y: auto;"></div>

            <div style="display: flex; gap: 8px; margin-top: 8px;">
                <button class="btn-start-bet" style="padding: 10px; background: var(--accent-yellow); color: #000;" onclick="switchGame('bingo'); resetBingoToMenu();">
                    ➕ JOIN (ተጨማሪ ግባ)
                </button>
                <button class="btn-start-bet" id="btn-cancel-bingo" style="padding: 10px; background: #ff1744; color: #fff;" onclick="cancelBingoSelection()">
                    ✖ CANCEL (ሰርዝ)
                </button>
            </div>
        </div>
    </div>

    <!-- ================= HISTORY SECTION ================= -->
    <div id="history-section" class="bet-card" style="display: none;">
        <h3 style="margin-bottom: 10px; color: var(--accent-orange); font-size: 14px;">የእርስዎ የጨዋታ ሂስትሪ (BET HISTORY)</h3>
        <table class="history-table">
            <thead>
                <tr>
                    <th>ጨዋታ</th>
                    <th>መደብ</th>
                    <th>ውጤት</th>
                    <th>ያሸነፉት</th>
                </tr>
            </thead>
            <tbody id="user-history-tbody">
                <tr><td colspan="4" style="text-align: center; color: var(--text-muted);">ምንም ሂስትሪ የለም</td></tr>
            </tbody>
        </table>
    </div>

    <!-- ================= MODALS ================= -->
    <div class="modal-overlay" id="bingo-winner-modal">
        <div class="modal-box">
            <h2 style="color: var(--accent-yellow); margin-bottom: 10px; font-size: 24px;">🎉 BINGO WINNER! 🎉</h2>
            <div id="bingo-winner-details" style="font-size: 14px; margin-bottom: 15px; color: #fff;"></div>
            <button style="width: 100%; padding: 10px; background: var(--accent-green); color: #000; border: none; border-radius: 6px; font-weight: 900; cursor: pointer;" onclick="closeModal('bingo-winner-modal')">OK / ቀጥል</button>
        </div>
    </div>

    <div class="modal-overlay" id="keno-limits-modal">
        <div class="modal-box">
            <h3 style="color: var(--accent-yellow); margin-bottom: 12px;">⚙️ የኬኖ (Keno) መደብ ገደብ</h3>
            <div style="background: #0c1015; padding: 12px; border-radius: 6px; border: 1px solid var(--border-color); font-size: 13px; line-height: 1.8; margin-bottom: 12px;">
                <div>• <b>አነስተኛ መደብ:</b> <span style="color: var(--accent-green);">5.00 ETB</span></div>
                <div>• <b>ከፍተኛ መደብ:</b> <span style="color: var(--accent-pink);">12,000.00 ETB</span></div>
                <div>• <b>የቲኬት ገደብ:</b> <span style="color: var(--accent-yellow);">ከ20 በላይ ቲኬት መቁረጥ አይቻልም</span></div>
            </div>
            <button style="width: 100%; padding: 8px; background: #26323f; color: #fff; border: none; border-radius: 4px; cursor: pointer;" onclick="closeModal('keno-limits-modal')">ዝጋ</button>
        </div>
    </div>

    <div class="modal-overlay" id="keno-history-modal">
        <div class="modal-box" style="max-width: 420px;">
            <h3 style="color: var(--accent-yellow); margin-bottom: 12px;">📜 የኬኖ ታሪክ (Keno History)</h3>
            <div style="max-height: 250px; overflow-y: auto; margin-bottom: 12px;">
                <table class="history-table">
                    <thead>
                        <tr>
                            <th>መደብ</th>
                            <th>የወጡት/ቁጥሮች</th>
                            <th>ያሸነፉት</th>
                        </tr>
                    </thead>
                    <tbody id="keno-only-history-tbody">
                        <tr><td colspan="3" style="text-align: center; color: var(--text-muted);">ምንም የኬኖ ታሪክ የለም</td></tr>
                    </tbody>
                </table>
            </div>
            <button style="width: 100%; padding: 8px; background: #26323f; color: #fff; border: none; border-radius: 4px; cursor: pointer;" onclick="closeModal('keno-history-modal')">ዝጋ</button>
        </div>
    </div>

    <div class="modal-overlay" id="aviator-limits-modal">
        <div class="modal-box">
            <h3 style="color: var(--accent-yellow); margin-bottom: 12px;">⚙️ የአቪዬተር መደብ ገደብ</h3>
            <div style="background: #0c1015; padding: 12px; border-radius: 6px; border: 1px solid var(--border-color); font-size: 13px; line-height: 1.8; margin-bottom: 12px;">
                <div>• <b>አነስተኛ መደብ:</b> <span style="color: var(--accent-green);">5.00 ETB</span></div>
                <div>• <b>ከፍተኛ መደብ:</b> <span style="color: var(--accent-pink);">12,000.00 ETB</span></div>
            </div>
            <button style="width: 100%; padding: 8px; background: #26323f; color: #fff; border: none; border-radius: 4px; cursor: pointer;" onclick="closeModal('aviator-limits-modal')">ዝጋ</button>
        </div>
    </div>

    <div class="modal-overlay" id="aviator-history-modal">
        <div class="modal-box" style="max-width: 420px;">
            <h3 style="color: var(--accent-orange); margin-bottom: 12px;">📜 የአቪዬተር ብቻ ሂስትሪ</h3>
            <div style="max-height: 250px; overflow-y: auto; margin-bottom: 12px;">
                <table class="history-table">
                    <thead>
                        <tr>
                            <th>መደብ</th>
                            <th>ኤክስ (Multiplier)</th>
                            <th>ያሸነፉት</th>
                        </tr>
                    </thead>
                    <tbody id="aviator-only-history-tbody">
                        <tr><td colspan="3" style="text-align: center; color: var(--text-muted);">ምንም ሂስትሪ የለም</td></tr>
                    </tbody>
                </table>
            </div>
            <button style="width: 100%; padding: 8px; background: #26323f; color: #fff; border: none; border-radius: 4px; cursor: pointer;" onclick="closeModal('aviator-history-modal')">ዝጋ</button>
        </div>
    </div>

    <div class="modal-overlay" id="deposit-modal">
        <div class="modal-box">
            <h3 style="color: var(--accent-green); margin-bottom: 10px;">ብር ማስገቢያ (Deposit)</h3>
            <div style="background: #0c1015; border: 1px solid var(--accent-green); border-radius: 6px; padding: 10px; margin-bottom: 12px; font-size: 12px; line-height: 1.6;">
                <div style="color: var(--accent-yellow); font-weight: bold; margin-bottom: 4px;">📱 በቴሌብር (Telebirr) ገቢ ማድረጊያ:</div>
                <div><b>ስልክ ቁጥር:</b> <span style="color: var(--accent-green); font-weight: bold;">0997384093</span></div>
                <div><b>ስም:</b> <span style="color: #fff; font-weight: bold;">አብድል ዋሂድ</span></div>
            </div>
            <input type="number" id="dep-amount-input" class="form-control" placeholder="የላኩት ብር መጠን (ETB)">
            <button class="btn-start-bet" style="width: 100%; height: 40px; margin-bottom: 6px;" onclick="submitDepositForm()">SUBMIT DEPOSIT</button>
            <button style="width: 100%; padding: 8px; background: #26323f; color: #fff; border: none; border-radius: 4px; cursor: pointer;" onclick="closeModal('deposit-modal')">ዝጋ</button>
        </div>
    </div>

    <div class="modal-overlay" id="withdraw-modal">
        <div class="modal-box">
            <h3 style="color: var(--accent-orange); margin-bottom: 10px;">ብር ማውጫ (Withdraw)</h3>
            <select id="with-method" class="form-control">
                <option value="Telebirr">Telebirr</option>
                <option value="CBE Birr">CBE Birr</option>
            </select>
            <input type="text" id="with-account" class="form-control" placeholder="የመቀበያ ስልክ / አካውንት">
            <input type="number" id="with-amount" class="form-control" placeholder="የምታወጡት ብር መጠን">
            <button class="btn-start-bet" style="width: 100%; height: 40px; margin-bottom: 6px; background: linear-gradient(180deg, #ff9800 0%, #e65100 100%);" onclick="submitWithdrawForm()">WITHDRAW</button>
            <button style="width: 100%; padding: 8px; background: #26323f; color: #fff; border: none; border-radius: 4px; cursor: pointer;" onclick="closeModal('withdraw-modal')">ዝጋ</button>
        </div>
    </div>
    {% endif %}

    <!-- ================= JAVASCRIPT LOGIC ================= -->
    <script>
        let currentMultiplier = 1.00;
        let isGameRunning = false;
        let drawnKenoNumbers = [];
        let flightPoints = [];
        let isKenoDrawingActive = false;

        const KENO_ODDS = {
            1: {1: 3.5}, 2: {1: 1.0, 2: 10.0}, 3: {0: 0.0, 1: 0.0, 2: 2.0, 3: 50.0},
            4: {2: 1.5, 3: 10.0, 4: 80.0}, 5: {2: 1.0, 3: 3.0, 4: 30.0, 5: 150.0},
            6: {3: 2.0, 4: 15.0, 5: 60.0, 6: 500.0}, 7: {0: 1.0, 3: 2.0, 4: 4.0, 5: 20.0, 6: 80.0, 7: 1000.0},
            8: {0: 1.0, 4: 5.0, 5: 15.0, 6: 50.0, 7: 200.0, 8: 2000.0}, 9: {0: 2.0, 4: 2.0, 5: 10.0, 6: 25.0, 7: 125.0, 8: 1000.0, 9: 5000.0},
            10: {0: 2.0, 5: 5.0, 6: 30.0, 7: 100.0, 8: 300.0, 9: 2000.0, 10: 10000.0}
        };

        function showHomeScreen() {
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            document.getElementById('btn-nav-home').classList.add('active');

            document.getElementById('home-dashboard-view').style.display = 'block';
            document.getElementById('aviator-section').style.display = 'none';
            document.getElementById('keno-section').style.display = 'none';
            document.getElementById('bingo-section').style.display = 'none';
            document.getElementById('history-section').style.display = 'none';
        }

        function switchGame(game) {
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            document.getElementById('home-dashboard-view').style.display = 'none';
            document.getElementById('aviator-section').style.display = 'none';
            document.getElementById('keno-section').style.display = 'none';
            document.getElementById('bingo-section').style.display = 'none';
            document.getElementById('history-section').style.display = 'none';

            document.getElementById('btn-nav-' + game).classList.add('active');
            document.getElementById(game + '-section').style.display = 'block';

            if(game === 'history') fetchUserHistory();
            if(game === 'bingo') resetBingoToMenu();
            if(game === 'aviator') resizeCanvas();
        }

        function togglePasswordVisibility() {
            let pwd = document.getElementById('auth-password');
            pwd.type = (pwd.type === 'password') ? 'text' : 'password';
        }

        function toggleDropdownMenu(e, menuId) {
            e.stopPropagation();
            let menu = document.getElementById(menuId);
            let isVisible = menu.style.display === 'block';
            document.querySelectorAll('.dropdown-menu-box').forEach(m => m.style.display = 'none');
            menu.style.display = isVisible ? 'none' : 'block';
        }

        document.addEventListener('click', function() {
            document.querySelectorAll('.dropdown-menu-box').forEach(m => m.style.display = 'none');
        });

        function openAviatorLimitsModal() { document.getElementById('aviator-limits-modal').style.display = 'flex'; }
        
        function openKenoHistoryModal() {
            fetch('/user_history').then(r=>r.json()).then(d=>{
                let tbody = document.getElementById('keno-only-history-tbody');
                let kenoHist = d.history ? d.history.filter(h => h.game.includes('Keno') || h.game.includes('ሻሞ')) : [];
                
                if(kenoHist.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="3" style="text-align: center; color: var(--text-muted);">ምንም የኬኖ ታሪክ የለም</td></tr>`;
                } else {
                    let html = "";
                    kenoHist.forEach(h => {
                        let isWin = h.win_amount > 0;
                        html += `<tr>
                            <td><b>${h.bet_amount} ETB</b></td>
                            <td>${h.result_info}</td>
                            <td class="${isWin ? 'badge-win' : 'badge-loss'}">${isWin ? '+' + h.win_amount + ' ETB' : '0.00 ETB'}</td>
                        </tr>`;
                    });
                    tbody.innerHTML = html;
                }
                document.getElementById('keno-history-modal').style.display = 'flex';
            });
        }

        function openAviatorHistoryModal() {
            fetch('/user_history').then(r=>r.json()).then(d=>{
                let tbody = document.getElementById('aviator-only-history-tbody');
                let aviatorHist = d.history ? d.history.filter(h => h.game === 'Aviator') : [];
                
                if(aviatorHist.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="3" style="text-align: center; color: var(--text-muted);">ምንም የአቪዬተር ሂስትሪ የለም</td></tr>`;
                } else {
                    let html = "";
                    aviatorHist.forEach(h => {
                        let isWin = h.win_amount > 0;
                        html += `<tr>
                            <td><b>${h.bet_amount} ETB</b></td>
                            <td>${h.result_info}</td>
                            <td class="${isWin ? 'badge-win' : 'badge-loss'}">${isWin ? '+' + h.win_amount + ' ETB' : '0.00 ETB'}</td>
                        </tr>`;
                    });
                    tbody.innerHTML = html;
                }
                document.getElementById('aviator-history-modal').style.display = 'flex';
            });
        }

        /* ================= BINGO SYSTEM LOGIC (3. CONTINUOUS TIMER FIX) ================= */
        let selectedBingoStake = 10;
        let selectedBingoCardIds = [];
        let currentBingoCardsData = [];
        let bingoTimerInterval = null;
        let bingoCallInterval = null;
        let bingoCallsList = [];
        let bingoStatusPollInterval = null;
        let bingoCurrentTimeLeft = 30;
        let bingoHasWonCurrentGame = false;

        const cardSelectorContainer = document.getElementById('bingo-card-selector');
        if(cardSelectorContainer) {
            let html = "";
            for(let i = 1; i <= 100; i++) {
                html += `<div id="b-card-btn-${i}" onclick="toggleBingoCardNum(${i})" style="background: #1a222d; color: #fff; text-align: center; padding: 8px 0; border-radius: 4px; font-weight: bold; cursor: pointer; border: 1px solid var(--border-color); font-size: 11px;">#${i}</div>`;
            }
            cardSelectorContainer.innerHTML = html;
        }

        function selectBingoStake(amount) {
            selectedBingoStake = amount;
            alert(amount + " ETB Room ተመርጧል!");
        }

        function toggleBingoCardNum(cardId) {
            if(selectedBingoCardIds.includes(cardId)) {
                selectedBingoCardIds = selectedBingoCardIds.filter(id => id !== cardId);
            } else {
                selectedBingoCardIds.push(cardId);
            }
            updateBingoCardSelectionUI();
        }

        function pickRandomBingoCard() {
            let r = Math.floor(Math.random() * 100) + 1;
            if(!selectedBingoCardIds.includes(r)) {
                selectedBingoCardIds.push(r);
            }
            updateBingoCardSelectionUI();
        }

        function clearAllBingoCards() {
            selectedBingoCardIds = [];
            updateBingoCardSelectionUI();
        }

        function updateBingoCardSelectionUI() {
            document.getElementById('bingo-selected-count').innerText = selectedBingoCardIds.length;
            for(let i = 1; i <= 100; i++) {
                let el = document.getElementById('b-card-btn-' + i);
                if(el) {
                    if(selectedBingoCardIds.includes(i)) {
                        el.style.background = 'var(--accent-yellow)';
                        el.style.color = '#000';
                    } else {
                        el.style.background = '#1a222d';
                        el.style.color = '#fff';
                    }
                }
            }
        }

        function resetBingoToMenu() {
            clearInterval(bingoTimerInterval);
            clearInterval(bingoCallInterval);
            clearInterval(bingoStatusPollInterval);
            bingoTimerInterval = null;
            bingoHasWonCurrentGame = false;
            document.getElementById('bingo-menu-view').style.display = 'block';
            document.getElementById('bingo-game-view').style.display = 'none';
            document.getElementById('btn-cancel-bingo').style.display = 'block';
        }

        function joinBingoGame() {
            if(selectedBingoCardIds.length === 0) {
                alert("እባክዎን ቢያንስ አንድ ካርድ ይምረጡ!");
                return;
            }

            let fd = new FormData();
            fd.append('stake', selectedBingoStake);
            fd.append('card_ids', JSON.stringify(selectedBingoCardIds));

            fetch('/join_bingo', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{
                if(!d.success) { alert(d.message); return; }
                
                document.getElementById('user-balance').innerText = d.new_balance.toFixed(2);
                currentBingoCardsData = d.cards;
                renderAllBingoCards(d.cards);

                document.getElementById('bingo-menu-view').style.display = 'none';
                document.getElementById('bingo-game-view').style.display = 'block';
                
                startBingoLobbyPolling();
            });
        }

        function cancelBingoSelection() {
            if(bingoCurrentTimeLeft <= 15) {
                alert("ጨዋታው ለመጀመር 15 ሰከንድ ወይም ከዚያ በታች ስለቀረው ካንሰል ማድረግ አይቻልም!");
                return;
            }

            let fd = new FormData();
            fd.append('stake', selectedBingoStake);
            fd.append('card_count', currentBingoCardsData ? currentBingoCardsData.length : selectedBingoCardIds.length);

            fetch('/cancel_bingo', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{
                if(d.success) {
                    alert(d.message);
                    document.getElementById('user-balance').innerText = d.new_balance.toFixed(2);
                    resetBingoToMenu();
                } else {
                    alert(d.message);
                }
            });
        }

        function startBingoLobbyPolling() {
            if (bingoStatusPollInterval) clearInterval(bingoStatusPollInterval);
            bingoStatusPollInterval = setInterval(() => {
                fetch(`/bingo_room_status?stake=${selectedBingoStake}`).then(r=>r.json()).then(data => {
                    document.getElementById('bingo-player-count').innerText = data.player_count;
                    document.getElementById('bingo-pot-display').innerText = "POT: " + data.pot.toFixed(2) + " ETB";

                    // Continuously ensure timer engine stays active without resetting prematurely
                    if(data.player_count < 2) {
                        document.getElementById('bingo-room-status').innerText = "ቢያንስ 2 ተጫዋች ያስፈልጋል...";
                        document.getElementById('bingo-room-timer').innerText = "መጠባበቅ";
                    } else {
                        document.getElementById('bingo-room-status').innerText = "ተጫዋች ተሟልቷል! ቆጠራ ላይ...";
                        if(!bingoTimerInterval && data.status === "WAITING") {
                            startBingoTimerEngine();
                        }
                    }
                });
            }, 1000);
        }

        function renderAllBingoCards(cards) {
            let wrapper = document.getElementById('bingo-cards-wrapper');
            wrapper.innerHTML = "";

            cards.forEach((cardObj) => {
                let cardEl = document.createElement('div');
                cardEl.className = 'bingo-card-container';
                cardEl.id = `bingo-card-container-${cardObj.id}`;

                let headers = ['B', 'I', 'N', 'G', 'O'];
                let html = `<div style="font-size:11px; font-weight:bold; color:var(--accent-yellow); margin-bottom:4px;">ካርድ #${cardObj.id}</div><div class="bingo-card-grid">`;

                headers.forEach(h => html += `<div class="bingo-header-cell">${h}</div>`);

                for(let r = 0; r < 5; r++) {
                    headers.forEach(h => {
                        let val = cardObj.card[h][r];
                        if(val === "FREE") {
                            html += `<div class="bingo-cell free marked" id="b-cell-${cardObj.id}-${h}-${r}" data-val="FREE">FREE</div>`;
                        } else {
                            html += `<div class="bingo-cell" id="b-cell-${cardObj.id}-${h}-${r}" data-val="${val}">${val}</div>`;
                        }
                    });
                }
                html += `</div>`;
                cardEl.innerHTML = html;
                wrapper.appendChild(cardEl);
            });
        }

        function autoMarkBingoNumber(num) {
            currentBingoCardsData.forEach((cardObj) => {
                let headers = ['B', 'I', 'N', 'G', 'O'];
                headers.forEach(h => {
                    for(let r = 0; r < 5; r++) {
                        let val = cardObj.card[h][r];
                        if(parseInt(val) === num) {
                            let cell = document.getElementById(`b-cell-${cardObj.id}-${h}-${r}`);
                            if(cell) {
                                cell.classList.add('marked');
                            }
                        }
                    }
                });
                checkBingoWinPattern(cardObj.id);
            });
        }

        function startBingoTimerEngine() {
            if(bingoTimerInterval) return; // Prevent duplicate interval loops
            bingoCurrentTimeLeft = 30;
            let timerEl = document.getElementById('bingo-room-timer');

            bingoTimerInterval = setInterval(() => {
                bingoCurrentTimeLeft--;
                timerEl.innerText = bingoCurrentTimeLeft + "s";

                if(bingoCurrentTimeLeft <= 15) {
                    let cancelBtn = document.getElementById('btn-cancel-bingo');
                    if(cancelBtn) cancelBtn.style.display = 'none';
                }

                if(bingoCurrentTimeLeft <= 0) {
                    clearInterval(bingoTimerInterval);
                    bingoTimerInterval = null;
                    if(bingoStatusPollInterval) clearInterval(bingoStatusPollInterval);
                    timerEl.innerText = "ተጀምሯል!";
                    document.getElementById('bingo-room-status').innerText = "ጨዋታው እየተካሄደ ነው!";
                    start75BingoCalls();
                }
            }, 1000);
        }

        function start75BingoCalls() {
            bingoCallsList = [];
            let pool = Array.from({length: 75}, (_, i) => i + 1);
            pool.sort(() => Math.random() - 0.5);

            let idx = 0;
            bingoCallInterval = setInterval(() => {
                if(idx < pool.length && !bingoHasWonCurrentGame) {
                    let num = pool[idx];
                    bingoCallsList.push(num);
                    
                    let letter = num <= 15 ? 'B' : (num <= 30 ? 'I' : (num <= 45 ? 'N' : (num <= 60 ? 'G' : 'O')));
                    document.getElementById('bingo-current-call').innerText = letter + "-" + num;
                    
                    autoMarkBingoNumber(num);
                    idx++;
                } else if (!bingoHasWonCurrentGame) {
                    clearInterval(bingoCallInterval);
                    alert("75ቱ ቁጥሮች ወጥተው አልቀዋል!");
                    resetBingoToMenu();
                }
            }, 2000);
        }

        function checkBingoWinPattern(cardId) {
            if (bingoHasWonCurrentGame) return;

            let headers = ['B', 'I', 'N', 'G', 'O'];
            let isWon = false;

            for(let r = 0; r < 5; r++) {
                let rowWin = true;
                headers.forEach(h => {
                    let cell = document.getElementById(`b-cell-${cardId}-${h}-${r}`);
                    if(!cell || !cell.classList.contains('marked')) rowWin = false;
                });
                if(rowWin) isWon = true;
            }

            headers.forEach(h => {
                let colWin = true;
                for(let r = 0; r < 5; r++) {
                    let cell = document.getElementById(`b-cell-${cardId}-${h}-${r}`);
                    if(!cell || !cell.classList.contains('marked')) colWin = false;
                }
                if(colWin) isWon = true;
            });

            let diag1Win = true;
            let diag2Win = true;
            for(let i = 0; i < 5; i++) {
                let cell1 = document.getElementById(`b-cell-${cardId}-${headers[i]}-${i}`);
                let cell2 = document.getElementById(`b-cell-${cardId}-${headers[4-i]}-${i}`);
                if(!cell1 || !cell1.classList.contains('marked')) diag1Win = false;
                if(!cell2 || !cell2.classList.contains('marked')) diag2Win = false;
            }
            if(diag1Win || diag2Win) isWon = true;

            if(isWon) {
                bingoHasWonCurrentGame = true;
                clearInterval(bingoCallInterval);
                
                let winContainer = document.getElementById(`bingo-card-container-${cardId}`);
                if(winContainer) winContainer.classList.add('winning-card');

                triggerBingoWinClaim(cardId);
            }
        }

        function triggerBingoWinClaim(winningCardId) {
            let fd = new FormData();
            fd.append('stake', selectedBingoStake);
            fd.append('card_id', winningCardId);

            fetch('/claim_bingo', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{
                if(d.success) {
                    document.getElementById('user-balance').innerText = d.new_balance.toFixed(2);
                    
                    let winDetails = document.getElementById('bingo-winner-details');
                    winDetails.innerHTML = `
                        <div>ያሸነፉበት ካርድ፡ <b>Card #${winningCardId}</b></div>
                        <div style="font-size: 20px; color: var(--accent-green); font-weight: 900; margin-top: 8px;">የሽልማት መጠን፡ ${d.win_amount.toFixed(2)} ETB</div>
                    `;
                    document.getElementById('bingo-winner-modal').style.display = 'flex';
                }
            });
        }

        /* ================= AVIATOR ENGINE ================= */
        let aviatorBets = {
            1: { amount: 10.00, status: 'NONE', winAmt: 0 },
            2: { amount: 20.00, status: 'NONE', winAmt: 0 }
        };

        let aviatorStats = { total: 0, cashedOut: 0, totalWinAmt: 0.0 };
        let canvas, ctx;

        function resizeCanvas() {
            let screenBox = document.getElementById('aviator-screen-box');
            canvas = document.getElementById('aviator-canvas');
            if(canvas && screenBox) {
                canvas.width = screenBox.clientWidth;
                canvas.height = screenBox.clientHeight;
                ctx = canvas.getContext('2d');
            }
        }

        function drawAviatorTrajectory() {
            if(!ctx || !canvas) return;
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            if(flightPoints.length > 1) {
                ctx.beginPath();
                ctx.moveTo(flightPoints[0].x, flightPoints[0].y);
                for(let i = 1; i < flightPoints.length; i++) {
                    ctx.lineTo(flightPoints[i].x, flightPoints[i].y);
                }
                ctx.strokeStyle = "rgba(255, 23, 68, 0.9)";
                ctx.lineWidth = 3;
                ctx.setLineDash([6, 4]);
                ctx.stroke();
                ctx.setLineDash([]);
            }
        }

        function toggleAutoCashInput(id) {
            let isChecked = document.getElementById(`auto-cash-toggle-${id}`).checked;
            document.getElementById(`auto-cash-val-${id}`).style.display = isChecked ? 'inline-block' : 'none';
        }

        function adjustBet(id, val) {
            if(aviatorBets[id].status !== 'NONE' && aviatorBets[id].status !== 'WAITING') return;
            let newAmt = Math.min(12000, Math.max(5, aviatorBets[id].amount + val));
            aviatorBets[id].amount = newAmt;
            document.getElementById(`aviator-bet-val-${id}`).value = aviatorBets[id].amount.toFixed(2);
            document.getElementById(`aviator-btn-sub-${id}`).innerText = aviatorBets[id].amount.toFixed(2) + " ETB";
        }

        function onManualBetChange(id, val) {
            if(aviatorBets[id].status !== 'NONE' && aviatorBets[id].status !== 'WAITING') return;
            let num = parseFloat(val);
            if(isNaN(num) || num < 5) num = 5.00;
            if(num > 12000) num = 12000.00;
            aviatorBets[id].amount = num;
            document.getElementById(`aviator-bet-val-${id}`).value = num.toFixed(2);
            document.getElementById(`aviator-btn-sub-${id}`).innerText = num.toFixed(2) + " ETB";
        }

        function handleAviatorBtnClick(id) {
            let state = aviatorBets[id].status;

            if(state === 'NONE') {
                if(isGameRunning) {
                    let fd = new FormData();
                    fd.append('amount', aviatorBets[id].amount);

                    fetch('/place_bet', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{
                        if(!d.success) { alert(d.message); return; }
                        document.getElementById('user-balance').innerText = d.new_balance.toFixed(2);
                        
                        aviatorBets[id].status = 'WAITING';
                        let btn = document.getElementById(`aviator-bet-btn-${id}`);
                        btn.className = 'btn-start-bet cancel';
                        document.getElementById(`aviator-btn-title-${id}`).innerText = "CANCEL";
                        document.getElementById(`aviator-btn-sub-${id}`).innerText = "ይሰረዝ (" + aviatorBets[id].amount.toFixed(2) + " ETB)";
                        renderAviatorLiveBets();
                    });
                    return;
                }

                let fd = new FormData();
                fd.append('amount', aviatorBets[id].amount);

                fetch('/place_bet', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{
                    if(!d.success) { alert(d.message); return; }
                    document.getElementById('user-balance').innerText = d.new_balance.toFixed(2);
                    
                    aviatorBets[id].status = 'BET';
                    let btn = document.getElementById(`aviator-bet-btn-${id}`);
                    btn.className = 'btn-start-bet cancel';
                    document.getElementById(`aviator-btn-title-${id}`).innerText = "CANCEL";
                    document.getElementById(`aviator-btn-sub-${id}`).innerText = "ሰርዝ (" + aviatorBets[id].amount.toFixed(2) + " ETB)";
                    renderAviatorLiveBets();
                });
            } 
            else if(state === 'BET' || state === 'WAITING') {
                let fd = new FormData();
                fd.append('amount', aviatorBets[id].amount);

                fetch('/cancel_bet', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{
                    if(d.success) {
                        document.getElementById('user-balance').innerText = d.new_balance.toFixed(2);
                        aviatorBets[id].status = 'NONE';
                        
                        let btn = document.getElementById(`aviator-bet-btn-${id}`);
                        btn.className = 'btn-start-bet';
                        document.getElementById(`aviator-btn-title-${id}`).innerText = `BET #${id}`;
                        document.getElementById(`aviator-btn-sub-${id}`).innerText = aviatorBets[id].amount.toFixed(2) + " ETB";
                        renderAviatorLiveBets();
                    }
                });
            }
            else if(state === 'RUNNING') {
                executeCashout(id);
            }
        }

        function executeCashout(id) {
            let b = aviatorBets[id];
            if(b.status !== 'RUNNING') return;

            let cashoutVal = (b.amount * currentMultiplier).toFixed(2);
            let fd = new FormData();
            fd.append('game', 'Aviator');
            fd.append('bet_amount', b.amount);
            fd.append('win_amount', cashoutVal);
            fd.append('result_info', currentMultiplier.toFixed(2) + "x");

            fetch('/cashout', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{
                if(d.success) {
                    document.getElementById('user-balance').innerText = d.new_balance.toFixed(2);
                    b.status = 'WON';
                    b.winAmt = cashoutVal;

                    aviatorStats.cashedOut += 1;
                    aviatorStats.totalWinAmt += parseFloat(cashoutVal);

                    let btn = document.getElementById(`aviator-bet-btn-${id}`);
                    btn.className = 'btn-start-bet won';
                    btn.disabled = false;
                    document.getElementById(`aviator-btn-title-${id}`).innerText = "CASHED OUT";
                    document.getElementById(`aviator-btn-sub-${id}`).innerText = cashoutVal + " ETB";
                    renderAviatorLiveBets();
                }
            });
        }

        function renderAviatorLiveBets() {
            let list = document.getElementById('aviator-live-bets-list');
            let countSpan = document.getElementById('aviator-live-count');
            if(!list) return;

            let activeBets = Object.keys(aviatorBets).filter(k => aviatorBets[k].status !== 'NONE');
            countSpan.innerText = activeBets.length + " Bets";

            document.getElementById('aviator-stat-ratio').innerText = `${aviatorStats.total}/${aviatorStats.cashedOut}`;
            document.getElementById('aviator-stat-totalwin').innerText = aviatorStats.totalWinAmt.toFixed(2) + " ETB";

            if(activeBets.length === 0) {
                list.innerHTML = `<p style="font-size: 11px; color: var(--text-muted);">በዚህ ዙር የተመደበ የለም።</p>`;
                return;
            }

            let html = "";
            activeBets.forEach(k => {
                let b = aviatorBets[k];
                if(b.status === 'RUNNING') {
                    let totalVal = (b.amount * currentMultiplier).toFixed(2);
                    let btn = document.getElementById(`aviator-bet-btn-${k}`);
                    btn.className = 'btn-start-bet flying';
                    document.getElementById(`aviator-btn-title-${k}`).innerText = "CASH OUT";
                    document.getElementById(`aviator-btn-sub-${k}`).innerText = `${totalVal} ETB (${currentMultiplier.toFixed(2)}x)`;
                }

                let statusText = "";
                if(b.status === 'WON') statusText = `<span style="color: var(--accent-green); font-weight: 900;">+${b.winAmt} ETB</span>`;
                else if(b.status === 'BET') statusText = `<span style="color: var(--accent-yellow);">ሳይጀምር የተያዘ</span>`;
                else if(b.status === 'WAITING') statusText = `<span style="color: var(--accent-orange);">ቀጣይ ዙር የሚጠብቅ</span>`;
                else if(b.status === 'RUNNING') statusText = `<span style="color: var(--accent-green); font-weight:bold;">${(b.amount * currentMultiplier).toFixed(2)} ETB 🚀</span>`;

                html += `<div class="live-bet-row"><span>መደብ #${k}: <b>${b.amount.toFixed(2)} ETB</b></span>${statusText}</div>`;
            });
            list.innerHTML = html;
        }

        function updateAviatorHistoryBar() {
            fetch('/aviator_history_data').then(r => r.json()).then(d => {
                let bar = document.getElementById('aviator-history-bar');
                if(!bar) return;
                let html = "";
                d.history.forEach(m => {
                    let colorClass = parseFloat(m) > 2.0 ? 'green' : (parseFloat(m) > 1.5 ? 'blue' : 'pink');
                    html += `<div class="mult-tag ${colorClass}">${m}</div>`;
                });
                bar.innerHTML = html;
            });
        }

        function runAviatorAutoEngine() {
            let multDisplay = document.getElementById('aviator-mult-display');
            let plane = document.getElementById('plane-icon');
            if(!multDisplay) return;

            resizeCanvas();
            flightPoints = [];
            currentMultiplier = 1.00;
            isGameRunning = true;
            multDisplay.style.color = "#fff";
            multDisplay.innerText = "1.00x";
            plane.innerText = "✈️";

            aviatorStats = { total: 0, cashedOut: 0, totalWinAmt: 0.0 };

            let rand = Math.random();
            let crashPoint = rand < 0.75 ? (Math.random() * 0.98 + 1.01).toFixed(2) : (Math.random() * 10.0 + 2.0).toFixed(2);

            setTimeout(() => {
                [1, 2].forEach(id => {
                    if(aviatorBets[id].status === 'BET') {
                        aviatorBets[id].status = 'RUNNING';
                        aviatorStats.total += 1;
                        let btn = document.getElementById(`aviator-bet-btn-${id}`);
                        btn.className = 'btn-start-bet flying';
                        btn.disabled = false;
                    }
                });
                renderAviatorLiveBets();
            }, 300);

            let timer = setInterval(() => {
                currentMultiplier += currentMultiplier > 5 ? 0.08 : 0.025;
                multDisplay.innerText = currentMultiplier.toFixed(2) + "x";
                
                let curX = Math.min((currentMultiplier - 1) * 28, canvas.width - 40);
                let curY = canvas.height - Math.min((currentMultiplier - 1) * 18, canvas.height - 40) - 20;

                flightPoints.push({x: curX + 15, y: curY + 15});
                drawAviatorTrajectory();

                if(plane) {
                    plane.style.transform = `translate(${curX}px, -${canvas.height - curY - 20}px)`;
                }

                [1, 2].forEach(id => {
                    if(aviatorBets[id].status === 'RUNNING') {
                        let isAutoCashEnabled = document.getElementById(`auto-cash-toggle-${id}`).checked;
                        if(isAutoCashEnabled) {
                            let autoCashInput = document.getElementById(`auto-cash-val-${id}`).value;
                            let targetMult = parseFloat(autoCashInput);
                            if(!isNaN(targetMult) && currentMultiplier >= targetMult) {
                                executeCashout(parseInt(id));
                            }
                        }
                    }
                });
                renderAviatorLiveBets();

                if(currentMultiplier >= parseFloat(crashPoint)) {
                    clearInterval(timer);
                    isGameRunning = false;
                    multDisplay.style.color = "var(--accent-pink)";
                    multDisplay.innerText = "FLEW AWAY @ " + crashPoint + "x";

                    plane.innerText = "💥🔥";

                    fetch('/add_aviator_history', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                        body: 'mult=' + crashPoint + 'x'
                    }).then(() => updateAviatorHistoryBar());

                    [1, 2].forEach(id => {
                        if(aviatorBets[id].status === 'RUNNING') {
                            let fd = new FormData();
                            fd.append('game', 'Aviator');
                            fd.append('bet_amount', aviatorBets[id].amount);
                            fd.append('win_amount', 0);
                            fd.append('result_info', crashPoint + "x (Crashed)");
                            fetch('/record_loss', {method: 'POST', body: fd});
                        }
                        
                        if(aviatorBets[id].status === 'WAITING') {
                            aviatorBets[id].status = 'BET';
                            let btn = document.getElementById(`aviator-bet-btn-${id}`);
                            btn.className = 'btn-start-bet cancel';
                            document.getElementById(`aviator-btn-title-${id}`).innerText = "CANCEL";
                            document.getElementById(`aviator-btn-sub-${id}`).innerText = "ሰርዝ (" + aviatorBets[id].amount.toFixed(2) + " ETB)";
                        } else {
                            aviatorBets[id].status = 'NONE';
                            let btn = document.getElementById(`aviator-bet-btn-${id}`);
                            btn.className = 'btn-start-bet';
                            btn.disabled = false;
                            document.getElementById(`aviator-btn-title-${id}`).innerText = `BET #${id}`;
                            document.getElementById(`aviator-btn-sub-${id}`).innerText = aviatorBets[id].amount.toFixed(2) + " ETB";
                        }
                    });

                    let countdown = 5;
                    let cdTimer = setInterval(() => {
                        multDisplay.innerText = "NEXT IN " + countdown + "s";
                        countdown--;
                        if(countdown < 0) {
                            clearInterval(cdTimer);
                            if(plane) plane.style.transform = `translate(0px, 0px)`;
                            runAviatorAutoEngine();
                        }
                    }, 1000);
                }
            }, 80);
        }

        /* ================= KENO ENGINE ================= */
        let selectedKenoList = [];
        let kenoTickets = [];
        let kenoBetAmount = 10.00;
        let kenoTotalRoundBetsCount = 0;
        const gridBoard = document.getElementById('keno-grid-board');

        if(gridBoard) {
            for(let i = 1; i <= 80; i++) {
                let cell = document.createElement('div');
                cell.className = 'keno-num';
                cell.innerText = i;
                cell.id = 'keno-cell-' + i;
                cell.onclick = () => selectKenoNum(i, cell);
                gridBoard.appendChild(cell);
            }
        }

        function selectKenoNum(num, el) {
            if(selectedKenoList.includes(num)) {
                selectedKenoList = selectedKenoList.filter(n => n !== num);
                el.classList.remove('selected');
            } else {
                if(selectedKenoList.length < 10) {
                    selectedKenoList.push(num);
                    el.classList.add('selected');
                } else { alert("ከ10 በላይ ቁጥሮችን መምረጥ አይችሉም!"); }
            }
        }

        function selectRandomKenoNumbers() {
            clearKenoSelection();
            let count = Math.floor(Math.random() * 5) + 4;
            let nums = [];
            while(nums.length < count) {
                let r = Math.floor(Math.random() * 80) + 1;
                if(!nums.includes(r)) nums.push(r);
            }
            nums.forEach(n => {
                let cell = document.getElementById('keno-cell-' + n);
                if(cell) selectKenoNum(n, cell);
            });
        }

        function clearKenoSelection() {
            selectedKenoList = [];
            document.querySelectorAll('.keno-num').forEach(e => e.classList.remove('selected'));
        }

        function adjustKenoBet(val) {
            let newBet = Math.min(12000, Math.max(5, kenoBetAmount + val));
            kenoBetAmount = newBet;
            document.getElementById('keno-bet-val').value = kenoBetAmount.toFixed(2);
        }

        function onManualKenoBetChange(val) {
            let num = parseFloat(val);
            if(isNaN(num) || num < 5) num = 5.00;
            if(num > 12000) num = 12000.00;
            kenoBetAmount = num;
            document.getElementById('keno-bet-val').value = num.toFixed(2);
        }

        function addKenoTicket() {
            if(isKenoDrawingActive) {
                alert("ጨዋታው ስለተጀመረ አሁን ቲኬት መጨመር አይቻልም!");
                return;
            }
            if(kenoTickets.length >= 20) {
                alert("በአንድ ዙር ከ 20 ቲኬት በላይ መቁረጥ አይቻልም!");
                return;
            }
            if(selectedKenoList.length === 0) { alert("ቢያንስ 1 ቁጥር ይምረጡ!"); return; }
            kenoTickets.push({ numbers: [...selectedKenoList], amount: kenoBetAmount, placed: false });
            clearKenoSelection();
            renderKenoTicketsUI();
        }

        function renderKenoTicketsUI() {
            let list = document.getElementById('keno-tickets-list');
            if(!list) return;
            document.getElementById('keno-tickets-count').innerText = kenoTickets.length;
            document.getElementById('keno-total-round-bets').innerText = kenoTotalRoundBetsCount;
            
            if(kenoTickets.length === 0) {
                list.innerHTML = `<p style="font-size: 11px; color: var(--text-muted);">ምንም የተዘጋጀ ቲኬት የለም።</p>`;
                return;
            }

            let html = "";
            kenoTickets.forEach((t, i) => {
                let numBadges = t.numbers.map(n => {
                    let isHit = drawnKenoNumbers.includes(n);
                    return `<span class="t-num-badge ${isHit ? 'hit' : ''}">${n}</span>`;
                }).join('');

                html += `<div class="live-bet-row" style="flex-direction: column; align-items: flex-start; gap: 4px;">
                    <div>ቲኬት #${i+1} (${t.numbers.length} ቁጥሮች) - <b>${t.amount.toFixed(2)} ETB</b> ${t.placed ? '✅ (ቆይቷል)' : ''}</div>
                    <div>${numBadges}</div>
                </div>`;
            });
            list.innerHTML = html;
        }

        function placeAllKenoBets() {
            let unplaced = kenoTickets.filter(t => !t.placed);
            if(unplaced.length === 0) { alert("የተመደበ አዲስ ቲኬት የለም!"); return; }

            let totalAmt = unplaced.reduce((acc, t) => acc + t.amount, 0);
            let fd = new FormData();
            fd.append('amount', totalAmt);

            fetch('/place_bet', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{
                if(!d.success) { alert(d.message); return; }
                document.getElementById('user-balance').innerText = d.new_balance.toFixed(2);
                
                unplaced.forEach(t => t.placed = true);
                kenoTotalRoundBetsCount += unplaced.length;
                renderKenoTicketsUI();
                alert("ቲኬቶች በትክክል ተመድበዋል!");
            });
        }

        function runKenoTimerEngine() {
            let timeLeft = 45;
            let timerDisplay = document.getElementById('keno-timer-display');
            let spinnerSlot = document.getElementById('keno-spinner-slot');
            
            setInterval(() => {
                timeLeft--;
                if(timerDisplay) timerDisplay.innerText = timeLeft + "s";

                if(timeLeft <= 5) {
                    isKenoDrawingActive = true;
                }

                if(timeLeft <= 0) {
                    timeLeft = 45;
                    isKenoDrawingActive = true;
                    drawnKenoNumbers = [];
                    
                    document.querySelectorAll('.keno-num').forEach(el => {
                        el.classList.remove('drawn-regular', 'ticket-matched', 'selected');
                    });
                    selectedKenoList = [];
                    renderKenoTicketsUI();
                    
                    fetch('/draw_keno_numbers').then(r=>r.json()).then(dData => {
                        let drawn = dData.drawn;
                        let index = 0;
                        let drawInterval = setInterval(() => {
                            if(index < drawn.length) {
                                let n = drawn[index];
                                drawnKenoNumbers.push(n);
                                
                                let spinCount = 0;
                                let spinTimer = setInterval(() => {
                                    if(spinnerSlot) spinnerSlot.innerText = Math.floor(Math.random() * 80) + 1;
                                    spinCount++;
                                    if(spinCount > 6) {
                                        clearInterval(spinTimer);
                                        if(spinnerSlot) spinnerSlot.innerText = n;
                                    }
                                }, 60);

                                let cell = document.getElementById('keno-cell-' + n);
                                if(cell) {
                                    cell.classList.add('drawn-regular');
                                    kenoTickets.forEach(t => {
                                        if(t.placed && t.numbers.includes(n)) {
                                            cell.classList.add('ticket-matched');
                                        }
                                    });
                                }
                                renderKenoTicketsUI();
                                index++;
                            } else {
                                clearInterval(drawInterval);
                                if(spinnerSlot) spinnerSlot.innerText = "✓";
                                evaluateKenoResults(drawn);
                                isKenoDrawingActive = false;
                            }
                        }, 650);
                    });
                }
            }, 1000);
        }

        function evaluateKenoResults(drawn) {
            fetch('/update_keno_history', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: 'draws=' + JSON.stringify(drawn)
            }).then(r => r.json()).then(d => {
                let listContainer = document.getElementById('recent-keno-detailed-list');
                if(listContainer && d.recent) {
                    let html = "";
                    d.recent.forEach((item, idx) => {
                        let ballsHtml = item.map(num => {
                            let isMatchedHit = drawnKenoNumbers.includes(num);
                            return `<span class="kh-ball ${isMatchedHit ? 'hit-match' : ''}">${num}</span>`;
                        }).join('');

                        html += `<div class="keno-history-row">
                            <span><b>ጨዋታ #${idx+1}</b> (ወጥተዋል: ${item.length} ቁጥሮች)</span>
                            <div class="keno-history-balls">${ballsHtml}</div>
                        </div>`;
                    });
                    listContainer.innerHTML = html;
                }
            });

            kenoTickets.forEach(t => {
                if(t.placed) {
                    let selectedCount = t.numbers.length;
                    let hits = t.numbers.filter(n => drawn.includes(n)).length;
                    
                    let multiplier = (KENO_ODDS[selectedCount] && KENO_ODDS[selectedCount][hits] !== undefined) 
                                     ? KENO_ODDS[selectedCount][hits] 
                                     : 0.0;

                    let winAmt = t.amount * multiplier;

                    if(winAmt > 0) {
                        let fd = new FormData();
                        fd.append('game', 'Keno (ሻሞ)');
                        fd.append('bet_amount', t.amount);
                        fd.append('win_amount', winAmt.toFixed(2));
                        fd.append('result_info', `${hits}/${selectedCount} Hits (${multiplier}x)`);
                        fetch('/cashout', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{
                            if(d.success) document.getElementById('user-balance').innerText = d.new_balance.toFixed(2);
                        });
                    } else {
                        let fd = new FormData();
                        fd.append('game', 'Keno (ሻሞ)');
                        fd.append('bet_amount', t.amount);
                        fd.append('result_info', `${hits}/${selectedCount} Hits (0x)`);
                        fetch('/record_loss', {method: 'POST', body: fd});
                    }
                }
            });
            
            kenoTickets = [];
            kenoTotalRoundBetsCount = 0;
            renderKenoTicketsUI();

            setTimeout(() => {
                document.querySelectorAll('.keno-num').forEach(el => {
                    el.classList.remove('drawn-regular', 'ticket-matched');
                });
            }, 3000);
        }

        function fetchUserHistory() {
            fetch('/user_history').then(r=>r.json()).then(d=>{
                let tbody = document.getElementById('user-history-tbody');
                if(!d.history || d.history.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: var(--text-muted);">ምንም ሂስትሪ የለም</td></tr>`;
                    return;
                }
                let html = "";
                d.history.forEach(h => {
                    let isWin = h.win_amount > 0;
                    html += `<tr>
                        <td><b>${h.game}</b></td>
                        <td>${h.bet_amount} ETB</td>
                        <td>${h.result_info}</td>
                        <td class="${isWin ? 'badge-win' : 'badge-loss'}">${isWin ? '+' + h.win_amount + ' ETB' : '0.00 ETB'}</td>
                    </tr>`;
                });
                tbody.innerHTML = html;
            });
        }

        window.onload = function() {
            runAviatorAutoEngine();
            runKenoTimerEngine();
            window.addEventListener('resize', resizeCanvas);
        };

        function login() {
            let fd = new FormData();
            fd.append('phone', document.getElementById('auth-phone').value);
            fd.append('password', document.getElementById('auth-password').value);
            fetch('/login', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{ if(d.success) location.reload(); else alert(d.message); });
        }
        function register() {
            let fd = new FormData();
            fd.append('phone', document.getElementById('auth-phone').value);
            fd.append('password', document.getElementById('auth-password').value);
            fetch('/register', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{ if(d.success) location.reload(); else alert(d.message); });
        }

        function openDepositModal() { document.getElementById('deposit-modal').style.display = 'flex'; }
        function openWithdrawModal() { document.getElementById('withdraw-modal').style.display = 'flex'; }
        function closeModal(id) { document.getElementById(id).style.display = 'none'; }
        
        function submitDepositForm() {
            let amount = document.getElementById('dep-amount-input').value;
            if(!amount) { alert("እባክዎን የብር መጠን ያስገቡ!"); return; }

            let fd = new FormData();
            fd.append('amount', amount);
            fetch('/deposit', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{
                alert(d.message); if(d.success) closeModal('deposit-modal');
            });
        }

        function submitWithdrawForm() {
            let method = document.getElementById('with-method').value;
            let account = document.getElementById('with-account').value;
            let amount = document.getElementById('with-amount').value;

            let fd = new FormData();
            fd.append('method', method); fd.append('account', account); fd.append('amount', amount);
            fetch('/withdraw', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{
                alert(d.message); if(d.success) closeModal('withdraw-modal');
            });
        }
    </script>
</body>
</html>
"""

ADMIN_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="am">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="5"> <!-- Auto refresh every 5 seconds -->
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ethio Bet - Admin Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; background: #12181f; color: #fff; padding: 20px; }
        h1, h2 { color: #f5a623; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 30px; background: #1a222d; }
        th, td { border: 1px solid #26323f; padding: 10px; text-align: left; }
        th { background: #0c1015; color: #8b949e; }
        .btn-approve { background: #00e676; color: #000; border: none; padding: 6px 12px; font-weight: bold; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }
        .btn-reject { background: #ff1744; color: #fff; border: none; padding: 6px 12px; font-weight: bold; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }
        .nav-home { color: #00e676; text-decoration: none; font-weight: bold; display: inline-block; margin-bottom: 20px; }
    </style>
</head>
<body>
    <a href="/" class="nav-home">← ወደ ዋናው ገጽ ተመለስ (Back to Home)</a>
    <h1>Admin Control Panel</h1>
    <p style="font-size: 12px; color: #8b949e;">ይህ ገጽ በየ 5 ሰከንዱ ራሱን ያድሳል (Auto-refreshes every 5s)</p>
    <hr style="border-color: #26323f; margin-bottom: 20px;">

    <h2>1. የዲፖዚት ጥያቄዎች (Deposit Requests)</h2>
    <table>
        <thead>
            <tr>
                <th>ተራ ቁጥር</th>
                <th>ስልክ ቁጥር</th>
                <th>መጠን (ETB)</th>
                <th>እርምጃ (Action)</th>
            </tr>
        </thead>
        <tbody>
            {% if not deposit_requests %}
            <tr><td colspan="4" style="text-align: center; color: #8b949e;">ምንም የዲፖዚት ጥያቄ የለም</td></tr>
            {% endif %}
            {% for req in deposit_requests %}
            <tr>
                <td>{{ loop.index }}</td>
                <td><b>{{ req.phone }}</b></td>
                <td style="color: #00e676; font-weight: bold;">{{ "%.2f"|format(req.amount) }} ETB</td>
                <td>
                    <a href="/admin/approve_deposit/{{ loop.index0 }}" class="btn-approve">አፅድቅ (Approve)</a>
                    <a href="/admin/reject_deposit/{{ loop.index0 }}" class="btn-reject">ሰርዝ (Reject)</a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <h2>2. የብር ማውጫ ጥያቄዎች (Withdraw Requests)</h2>
    <table>
        <thead>
            <tr>
                <th>ተራ ቁጥር</th>
                <th>ስልክ ቁጥር</th>
                <th>አካውንት/ስልክ</th>
                <th>ዘዴ</th>
                <th>መጠን (ETB)</th>
                <th>እርምጃ (Action)</th>
            </tr>
        </thead>
        <tbody>
            {% if not withdraw_requests %}
            <tr><td colspan="6" style="text-align: center; color: #8b949e;">ምንም የብር ማውጫ ጥያቄ የለም</td></tr>
            {% endif %}
            {% for req in withdraw_requests %}
            <tr>
                <td>{{ loop.index }}</td>
                <td><b>{{ req.phone }}</b></td>
                <td>{{ req.account }}</td>
                <td>{{ req.method }}</td>
                <td style="color: #ff9800; font-weight: bold;">{{ "%.2f"|format(req.amount) }} ETB</td>
                <td>
                    <a href="/admin/approve_withdraw/{{ loop.index0 }}" class="btn-approve">ተፈፅሟል (Complete)</a>
                    <a href="/admin/reject_withdraw/{{ loop.index0 }}" class="btn-reject">መልስ/ሰርዝ (Reject)</a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

@app.route('/')
def index():
    if 'user' not in session:
        return render_template_string(HTML_TEMPLATE, logged_in=False)
    
    phone = session['user']
    user_data = users_db.get(phone, {"balance": 0.0, "is_admin": False})
    return render_template_string(HTML_TEMPLATE, 
                                  logged_in=True, 
                                  phone=phone, 
                                  balance=user_data['balance'], 
                                  is_admin=user_data.get('is_admin', False))

@app.route('/register', methods=['POST'])
def register():
    phone = request.form.get('phone', '').strip()
    password = request.form.get('password', '').strip()
    if not phone or not password or phone in users_db:
        return jsonify({"success": False, "message": "መረጃው ተሳስቷል ወይም አስቀድሞ አለ!"})
    
    users_db[phone] = { "password": generate_password_hash(password), "balance": 0.0, "is_admin": False }
    session['user'] = phone
    return jsonify({"success": True})

@app.route('/login', methods=['POST'])
def login():
    phone = request.form.get('phone', '').strip()
    password = request.form.get('password', '').strip()
    user = users_db.get(phone)
    if user and check_password_hash(user['password'], password):
        session['user'] = phone
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "የተሳሳተ መረጃ!"})

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/place_bet', methods=['POST'])
def place_bet():
    if 'user' not in session: return jsonify({"success": False})
    phone = session['user']
    bet_amount = float(request.form.get('amount', 0))
    if users_db[phone]['balance'] < bet_amount or bet_amount <= 0:
        return jsonify({"success": False, "message": "በቂ ባላንስ የሎትም!"})
    users_db[phone]['balance'] -= bet_amount
    return jsonify({"success": True, "new_balance": users_db[phone]['balance']})

@app.route('/cancel_bet', methods=['POST'])
def cancel_bet():
    if 'user' not in session: return jsonify({"success": False})
    phone = session['user']
    amount = float(request.form.get('amount', 0))
    users_db[phone]['balance'] += amount
    return jsonify({"success": True, "new_balance": users_db[phone]['balance']})

@app.route('/cashout', methods=['POST'])
def cashout():
    if 'user' not in session: return jsonify({"success": False})
    phone = session['user']
    win_amount = float(request.form.get('win_amount', 0))
    bet_amount = float(request.form.get('bet_amount', 0))
    game = request.form.get('game', 'Game')
    result_info = request.form.get('result_info', '')

    users_db[phone]['balance'] += win_amount
    global_bet_history.append({"phone": phone, "game": game, "bet_amount": bet_amount, "win_amount": win_amount, "result_info": result_info})
    return jsonify({"success": True, "new_balance": users_db[phone]['balance']})

@app.route('/record_loss', methods=['POST'])
def record_loss():
    if 'user' not in session: return jsonify({"success": False})
    phone = session['user']
    bet_amount = float(request.form.get('bet_amount', 0))
    game = request.form.get('game', 'Game')
    result_info = request.form.get('result_info', '')

    global_bet_history.append({"phone": phone, "game": game, "bet_amount": bet_amount, "win_amount": 0, "result_info": result_info})
    return jsonify({"success": True})

@app.route('/draw_keno_numbers')
def draw_keno_numbers():
    drawn = random.sample(range(1, 81), 20)
    return jsonify({"drawn": drawn})

@app.route('/join_bingo', methods=['POST'])
def join_bingo():
    if 'user' not in session: return jsonify({"success": False, "message": "እባክዎን አስቀድመው ይግቡ!"})
    phone = session['user']
    stake = int(request.form.get('stake', 10))
    card_ids_str = request.form.get('card_ids', '[]')
    card_ids = json.loads(card_ids_str)

    total_stake = stake * len(card_ids)

    if users_db[phone]['balance'] < total_stake:
        return jsonify({"success": False, "message": "በቂ ባላንስ የሎትም!"})

    users_db[phone]['balance'] -= total_stake
    
    net_stake = total_stake * 0.80
    room = bingo_rooms.get(stake, bingo_rooms[10])
    
    if phone not in room['players']:
        room['players'][phone] = []
    
    room['players'][phone].extend(card_ids)
    room['pot'] += net_stake

    selected_cards = [{"id": cid, "card": BINGO_CARDS.get(cid)} for cid in card_ids]
    return jsonify({
        "success": True, 
        "new_balance": users_db[phone]['balance'], 
        "cards": selected_cards
    })

@app.route('/bingo_room_status')
def bingo_room_status():
    stake = int(request.args.get('stake', 10))
    room = bingo_rooms.get(stake, bingo_rooms[10])
    player_count = sum(len(cards) for cards in room['players'].values())
    return jsonify({
        "player_count": player_count,
        "pot": room['pot'],
        "status": room['status']
    })

@app.route('/claim_bingo', methods=['POST'])
def claim_bingo():
    if 'user' not in session: return jsonify({"success": False})
    phone = session['user']
    stake = int(request.form.get('stake', 10))
    room = bingo_rooms.get(stake, bingo_rooms[10])
    
    win_amount = room['pot'] if room['pot'] > 0 else stake * 2
    users_db[phone]['balance'] += win_amount
    room['pot'] = 0.0

    global_bet_history.append({"phone": phone, "game": f"Bingo ({stake} ETB Room)", "bet_amount": stake, "win_amount": win_amount, "result_info": "Bingo Won!"})
    return jsonify({"success": True, "new_balance": users_db[phone]['balance'], "win_amount": win_amount})

@app.route('/cancel_bingo', methods=['POST'])
def cancel_bingo():
    if 'user' not in session: return jsonify({"success": False})
    phone = session['user']
    stake = int(request.form.get('stake', 10))
    card_count = int(request.form.get('card_count', 1))
    
    refund_amount = stake * card_count
    users_db[phone]['balance'] += refund_amount
    
    room = bingo_rooms.get(stake, bingo_rooms[10])
    if phone in room['players']:
        room['players'].pop(phone, None)
        room['pot'] -= (refund_amount * 0.80)
        if room['pot'] < 0: room['pot'] = 0.0

    return jsonify({"success": True, "message": "ቲኬቱ ተሰርዟል፣ ብርዎ ተመልሷል!", "new_balance": users_db[phone]['balance']})

@app.route('/update_keno_history', methods=['POST'])
def update_keno_history():
    draws_str = request.form.get('draws', '[]')
    draws = json.loads(draws_str)
    keno_recent_draws.insert(0, draws)
    if len(keno_recent_draws) > 3:
        keno_recent_draws.pop()
    return jsonify({"success": True, "recent": keno_recent_draws})

@app.route('/aviator_history_data')
def aviator_history_data():
    return jsonify({"history": aviator_history_list})

@app.route('/add_aviator_history', methods=['POST'])
def add_aviator_history():
    mult = request.form.get('mult', '2.00x')
    aviator_history_list.insert(0, mult)
    if len(aviator_history_list) > 10:
        aviator_history_list.pop()
    return jsonify({"success": True})

@app.route('/user_history')
def user_history():
    if 'user' not in session: return jsonify({"history": []})
    phone = session['user']
    user_hist = [h for h in global_bet_history if h['phone'] == phone]
    return jsonify({"history": user_hist[::-1]})

@app.route('/deposit', methods=['POST'])
def deposit():
    if 'user' not in session: return jsonify({"success": False, "message": "እባክዎን አስቀድመው ይግቡ!"})
    try:
        amount = float(request.form.get('amount', 0))
    except ValueError:
        return jsonify({"success": False, "message": "እባክዎን ትክክለኛ የብር መጠን ያስገቡ!"})
        
    if amount <= 0: return jsonify({"success": False, "message": "ልክ ያልሆነ መጠን!"})
    deposit_requests.append({"phone": session['user'], "amount": amount})
    return jsonify({"success": True, "message": "የብር ማስገቢያ ጥያቄዎ ተልኳል! በቅርብ ጊዜ ይጸድቃል።"})

@app.route('/withdraw', methods=['POST'])
def withdraw():
    if 'user' not in session: return jsonify({"success": False, "message": "እባክዎን አስቀድመው ይግቡ!"})
    phone = session['user']
    try:
        amount = float(request.form.get('amount', 0))
    except ValueError:
        return jsonify({"success": False, "message": "እባክዎን ትክክለኛ የብር መጠን ያስገቡ!"})
        
    method = request.form.get('method', 'Telebirr')
    account = request.form.get('account', '')
    
    if users_db[phone]['balance'] < amount or amount <= 0:
        return jsonify({"success": False, "message": "በቂ ባላንስ የሎትም!"})
    
    users_db[phone]['balance'] -= amount
    withdraw_requests.append({"phone": phone, "amount": amount, "method": method, "account": account})
    return jsonify({"success": True, "message": "የብር ማውጫ ጥያቄዎ ተሳክቷል!"})

# ==========================================
# ADMIN DASHBOARD & REQUEST HANDLING ROUTES
# ==========================================
@app.route('/admin')
def admin():
    if 'user' not in session or not users_db.get(session['user'], {}).get('is_admin', False):
        return redirect(url_for('index'))
    return render_template_string(
        ADMIN_HTML_TEMPLATE, 
        deposit_requests=deposit_requests, 
        withdraw_requests=withdraw_requests
    )

@app.route('/admin/approve_deposit/<int:req_id>')
def approve_deposit(req_id):
    if 'user' not in session or not users_db.get(session['user'], {}).get('is_admin', False):
        return redirect(url_for('index'))
    if 0 <= req_id < len(deposit_requests):
        req = deposit_requests.pop(req_id)
        phone = req['phone']
        amount = req['amount']
        if phone in users_db:
            users_db[phone]['balance'] += amount
    return redirect(url_for('admin'))

@app.route('/admin/reject_deposit/<int:req_id>')
def reject_deposit(req_id):
    if 'user' not in session or not users_db.get(session['user'], {}).get('is_admin', False):
        return redirect(url_for('index'))
    if 0 <= req_id < len(deposit_requests):
        deposit_requests.pop(req_id)
    return redirect(url_for('admin'))

@app.route('/admin/approve_withdraw/<int:req_id>')
def approve_withdraw(req_id):
    if 'user' not in session or not users_db.get(session['user'], {}).get('is_admin', False):
        return redirect(url_for('index'))
    if 0 <= req_id < len(withdraw_requests):
        withdraw_requests.pop(req_id)
    return redirect(url_for('admin'))

@app.route('/admin/reject_withdraw/<int:req_id>')
def reject_withdraw(req_id):
    if 'user' not in session or not users_db.get(session['user'], {}).get('is_admin', False):
        return redirect(url_for('index'))
    if 0 <= req_id < len(withdraw_requests):
        req = withdraw_requests.pop(req_id)
        phone = req['phone']
        amount = req['amount']
        if phone in users_db:
            users_db[phone]['balance'] += amount
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
        'O': random.sample(range(61, 76), 5)
    }
    card['N'][2] = "FREE"  # Center FREE space
    return card

BINGO_CARDS = {i: generate_bingo_card(i) for i in range(1, 101)}

bingo_rooms = {
    10: {"players": {}, "timer": 30, "status": "WAITING", "drawn": [], "pot": 0.0, "winners": []},
    30: {"players": {}, "timer": 30, "status": "WAITING", "drawn": [], "pot": 0.0, "winners": []},
    50: {"players": {}, "timer": 30, "status": "WAITING", "drawn": [], "pot": 0.0, "winners": []},
    100: {"players": {}, "timer": 30, "status": "WAITING", "drawn": [], "pot": 0.0, "winners": []}
}

KENO_ODDS = {
    1: {1: 3.5},
    2: {1: 1.0, 2: 10.0},
    3: {0: 0.0, 1: 0.0, 2: 2.0, 3: 50.0},
    4: {2: 1.5, 3: 10.0, 4: 80.0},
    5: {2: 1.0, 3: 3.0, 4: 30.0, 5: 150.0},
    6: {3: 2.0, 4: 15.0, 5: 60.0, 6: 500.0},
    7: {0: 1.0, 3: 2.0, 4: 4.0, 5: 20.0, 6: 80.0, 7: 1000.0},
    8: {0: 1.0, 4: 5.0, 5: 15.0, 6: 50.0, 7: 200.0, 8: 2000.0},
    9: {0: 2.0, 4: 2.0, 5: 10.0, 6: 25.0, 7: 125.0, 8: 1000.0, 9: 5000.0},
    10: {0: 2.0, 5: 5.0, 6: 30.0, 7: 100.0, 8: 300.0, 9: 2000.0, 10: 10000.0}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="am">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Ethio Bet - Premium Gaming Platform</title>
    <style>
        :root {
            --bg-dark: #12181f;
            --card-bg: #1a222d;
            --accent-green: #00e676;
            --accent-pink: #e91e63;
            --accent-orange: #ff9800;
            --accent-yellow: #f5a623;
            --text-main: #ffffff;
            --text-muted: #8b949e;
            --border-color: #26323f;
        }

        * { box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 0; }
        body { background-color: var(--bg-dark); color: var(--text-main); padding: 8px; }

        .top-nav { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: #0c1015; border-radius: 8px; margin-bottom: 12px; border: 1px solid var(--border-color); }
        .logo-text { font-weight: 900; font-size: 20px; color: #ffffff; font-style: italic; letter-spacing: 0.5px; cursor: pointer; }
        .logo-text span { color: var(--accent-yellow); }
        .balance-container { display: flex; align-items: center; gap: 6px; }
        .balance-pill { background: #070a0d; border: 1px solid #1f2936; border-radius: 20px; padding: 4px 10px; font-weight: bold; color: var(--accent-green); font-size: 13px; }
        .btn-deposit { background: var(--accent-green); color: #000; border: none; padding: 5px 10px; border-radius: 20px; font-weight: bold; font-size: 11px; cursor: pointer; }
        .btn-withdraw { background: var(--accent-orange); color: #000; border: none; padding: 5px 10px; border-radius: 20px; font-weight: bold; font-size: 11px; cursor: pointer; }
        .btn-logout { background: #ff1744; color: #fff; text-decoration: none; padding: 5px 8px; border-radius: 6px; font-size: 11px; font-weight: bold; }

        .auth-container { max-width: 420px; margin: 20px auto; background: #18222d; border-radius: 10px; overflow: hidden; border: 1px solid var(--border-color); box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
        .auth-header { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: #0e1620; border-bottom: 1px solid var(--border-color); }
        .auth-top-btns { display: flex; gap: 8px; }
        .btn-top-login { background: #2b3644; color: #fff; border: none; padding: 6px 14px; border-radius: 6px; font-weight: bold; font-size: 13px; cursor: pointer; }
        .btn-top-reg { background: var(--accent-yellow); color: #000; border: none; padding: 6px 14px; border-radius: 6px; font-weight: bold; font-size: 13px; cursor: pointer; }

        .auth-title-bar { display: flex; align-items: center; gap: 10px; padding: 14px 16px; font-size: 16px; font-weight: 800; color: #fff; border-bottom: 1px solid var(--border-color); }
        .back-arrow { background: #2b3644; color: #fff; width: 28px; height: 28px; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 14px; cursor: pointer; }

        .auth-tabs { display: grid; grid-template-columns: repeat(4, 1fr); background: #0f1722; border-bottom: 1px solid var(--border-color); }
        .auth-tab { padding: 12px 4px; text-align: center; font-size: 11px; color: var(--text-muted); cursor: pointer; border-bottom: 2px solid transparent; display: flex; flex-direction: column; align-items: center; gap: 4px; }
        .auth-tab.active { color: #fff; background: #18222d; border-bottom: 2px solid var(--accent-yellow); font-weight: bold; }

        .auth-body { padding: 20px 16px; }
        .phone-input-group { display: flex; gap: 8px; margin-bottom: 14px; }
        .country-code-box { background: #ffffff; color: #000; border-radius: 6px; padding: 0 10px; display: flex; align-items: center; gap: 6px; font-weight: bold; font-size: 13px; }
        .flag-icon { width: 20px; height: 14px; object-fit: cover; border-radius: 2px; }
        .auth-input { width: 100%; padding: 12px; background: #ffffff; color: #000; border: 1px solid #ccc; border-radius: 6px; font-size: 14px; font-weight: 600; outline: none; }
        .password-input-wrapper { position: relative; margin-bottom: 14px; }
        .eye-icon { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); color: #555; cursor: pointer; font-size: 16px; }

        .auth-options { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; font-size: 13px; }
        .remember-me { display: flex; align-items: center; gap: 8px; color: #ccc; cursor: pointer; }
        .forgot-pass { color: var(--accent-yellow); text-decoration: underline; cursor: pointer; font-weight: 500; }

        .btn-login-submit { width: 100%; background: var(--accent-yellow); color: #000; border: none; padding: 12px; border-radius: 6px; font-weight: 900; font-size: 15px; cursor: pointer; margin-bottom: 16px; }
        .register-footer { text-align: center; font-size: 13px; color: var(--text-muted); }
        .register-footer a { color: var(--accent-yellow); text-decoration: underline; font-weight: bold; cursor: pointer; }

        .home-game-menu { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 15px; }
        
        .game-banner-card { background: #1e2836; border-radius: 12px; overflow: hidden; border: 2px solid var(--border-color); cursor: pointer; position: relative; box-shadow: 0 8px 20px rgba(0,0,0,0.6); transition: transform 0.2s ease, border-color 0.2s ease; display: flex; flex-direction: column; justify-content: space-between; min-height: 200px; }
        .game-banner-card:hover { transform: translateY(-4px); border-color: var(--accent-yellow); }

        .card-shamo { background: radial-gradient(circle at center, #800000 0%, #300000 100%); }
        .card-birabiro { background: radial-gradient(circle at center, #2e1a00 0%, #110900 100%); }
        .card-bingo { background: radial-gradient(circle at center, #004d40 0%, #001a14 100%); }

        .card-brand-header { padding: 6px 8px; font-size: 10px; font-weight: 800; color: #fff; display: flex; justify-content: space-between; align-items: center; background: rgba(0,0,0,0.3); }
        .card-center-content { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 10px 4px; text-align: center; }

        .shamo-title { font-size: 28px; font-weight: 900; color: #ffe600; text-shadow: 2px 2px 0px #d32f2f; }
        .birabiro-title { font-size: 24px; font-weight: 900; color: #ff9800; }
        .bingo-title { font-size: 26px; font-weight: 900; color: #00e676; text-shadow: 0 0 10px rgba(0,230,118,0.5); }

        .card-footer-btn { background: rgba(0,0,0,0.5); padding: 6px; text-align: center; font-weight: bold; font-size: 10px; color: #fff; border-top: 1px solid rgba(255,255,255,0.1); }

        .game-nav-bar { display: flex; gap: 4px; margin-bottom: 12px; }
        .nav-btn { flex: 1; background: var(--card-bg); color: var(--text-muted); border: 1px solid var(--border-color); padding: 8px 4px; border-radius: 6px; font-weight: bold; font-size: 11px; cursor: pointer; text-align: center; }
        .nav-btn.active { background: #26323f; color: #fff; border-color: var(--accent-yellow); }

        .game-top-bar { display: flex; justify-content: space-between; align-items: center; position: relative; margin-bottom: 8px; padding: 4px 8px; background: #1a222d; border-radius: 8px; border: 1px solid var(--border-color); }
        .menu-btn { background: #26323f; border: 1px solid var(--border-color); color: #fff; font-size: 18px; font-weight: bold; width: 32px; height: 32px; border-radius: 6px; cursor: pointer; display: flex; align-items: center; justify-content: center; }
        .dropdown-menu-box { display: none; position: absolute; top: 40px; right: 8px; background: #1a222d; border: 1px solid var(--border-color); border-radius: 8px; box-shadow: 0 8px 20px rgba(0,0,0,0.8); z-index: 50; width: 180px; overflow: hidden; }
        .dropdown-item { padding: 10px 12px; font-size: 12px; color: #fff; cursor: pointer; display: flex; align-items: center; gap: 8px; border-bottom: 1px solid #26323f; }

        /* BINGO SPECIFIC STYLES */
        .bingo-card-container { background: #12181f; border: 1px solid var(--border-color); border-radius: 8px; padding: 6px; margin-bottom: 10px; }
        .bingo-card-container.winning-card { border: 2px solid var(--accent-yellow) !important; box-shadow: 0 0 15px rgba(245, 166, 35, 0.6); }
        .bingo-card-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px; background: #0c1015; padding: 8px; border-radius: 8px; }
        .bingo-header-cell { background: var(--accent-yellow); color: #000; font-weight: 900; text-align: center; padding: 6px; border-radius: 4px; font-size: 14px; }
        .bingo-cell { background: #1a222d; color: #fff; border: 1px solid var(--border-color); text-align: center; padding: 10px 0; font-weight: bold; font-size: 12px; border-radius: 4px; cursor: pointer; }
        .bingo-cell.marked { background: var(--accent-green); color: #000; font-weight: 900; box-shadow: 0 0 8px var(--accent-green); }
        .bingo-cell.free { background: var(--accent-pink); color: #fff; }

        .history-table { width: 100%; border-collapse: collapse; font-size: 11px; text-align: left; }
        .history-table th { background: #0c1015; padding: 6px; color: var(--text-muted); border-bottom: 1px solid var(--border-color); }
        .history-table td { padding: 6px; border-bottom: 1px solid #1a222d; }
        .badge-win { color: var(--accent-green); font-weight: bold; }
        .badge-loss { color: #ff1744; font-weight: bold; }

        .modal-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); justify-content: center; align-items: center; z-index: 100; }
        .modal-box { background: var(--card-bg); padding: 16px; border-radius: 10px; width: 90%; max-width: 380px; border: 1px solid var(--border-color); text-align: center; }
        .form-control { width: 100%; padding: 10px; background: #0c1015; border: 1px solid var(--border-color); color: #fff; border-radius: 6px; margin-bottom: 10px; font-size: 13px; }
        
        .btn-start-bet { background: linear-gradient(180deg, #00e676 0%, #00a855 100%); color: #000; border: none; border-radius: 8px; font-weight: 900; padding: 10px 0; cursor: pointer; text-align: center; width: 100%; transition: all 0.2s ease; }
        .btn-start-bet.cancel { background: linear-gradient(180deg, #ff1744 0%, #b71c1c 100%) !important; color: #fff !important; }
        .btn-start-bet.flying { background: linear-gradient(180deg, #ffea00 0%, #f57f17 100%) !important; color: #000 !important; }
        .btn-start-bet.won { background: linear-gradient(180deg, #00e676 0%, #00a855 100%) !important; color: #000 !important; }

        .number-picker { background: #0c1015; border-radius: 6px; border: 1px solid var(--border-color); display: flex; align-items: center; justify-content: space-between; padding: 2px 4px; margin-bottom: 6px; }
        .num-btn { background: #26323f; color: #fff; border: none; width: 28px; height: 28px; border-radius: 4px; font-size: 16px; font-weight: bold; cursor: pointer; }
        .num-input { background: transparent; border: none; color: #fff; text-align: center; font-size: 14px; font-weight: bold; width: 60px; outline: none; }
        .bet-card { background: var(--card-bg); border-radius: 10px; border: 1px solid var(--border-color); padding: 10px; }
        .keno-balls-preview { display: flex; gap: 4px; margin-bottom: 6px; }
        .k-ball { width: 20px; height: 20px; background: radial-gradient(circle at 30% 30%, #ffeb3b, #f57f17); color: #000; border-radius: 50%; font-size: 9px; font-weight: 900; display: flex; align-items: center; justify-content: center; }
        .multiplier-bar { display: flex; gap: 6px; overflow-x: auto; padding: 4px 0; margin-bottom: 8px; white-space: nowrap; height: 32px; align-items: center; }
        .mult-tag { background: #1a222d; border-radius: 4px; padding: 2px 8px; font-size: 11px; font-weight: bold; border: 1px solid var(--border-color); display: inline-block; }
        .mult-tag.green { color: var(--accent-green); }
        .mult-tag.pink { color: var(--accent-pink); }
        .mult-tag.blue { color: #29b6f6; }
        
        .aviator-screen { background: radial-gradient(circle at center, #1e2836 0%, #0c1015 100%); height: 140px; border-radius: 12px; border: 1px solid var(--border-color); position: relative; display: flex; flex-direction: column; justify-content: center; align-items: center; margin-bottom: 10px; overflow: hidden; }
        .aviator-mult { font-size: 32px; font-weight: 900; color: #fff; z-index: 2; }
        .plane-img { font-size: 32px; position: absolute; bottom: 10px; left: 10px; transition: transform 0.05s linear; z-index: 3; filter: drop-shadow(0 0 8px rgba(255, 23, 68, 0.9)); }
        .aviator-canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; pointer-events: none; }
        
        .dual-bet-container { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 10px; }
        .auto-controls-row { display: flex; justify-content: space-between; align-items: center; font-size: 10px; color: var(--text-muted); margin-bottom: 6px; background: #0c1015; padding: 4px 6px; border-radius: 4px; }
        .auto-cash-input { background: #1a222d; border: 1px solid var(--border-color); color: #fff; width: 45px; text-align: center; font-size: 10px; border-radius: 3px; }
        .live-bets-panel { background: var(--card-bg); border-radius: 8px; padding: 8px; border: 1px solid var(--border-color); margin-bottom: 10px; }
        .live-bets-title { font-size: 11px; font-weight: bold; color: var(--text-muted); margin-bottom: 6px; display: flex; justify-content: space-between; border-bottom: 1px solid var(--border-color); padding-bottom: 4px; }
        .live-bet-row { display: flex; justify-content: space-between; font-size: 11px; padding: 4px 0; border-bottom: 1px solid #1a222d; align-items: center; }
        .keno-board-container { background: var(--card-bg); border-radius: 10px; padding: 10px; border: 1px solid var(--border-color); margin-bottom: 10px; }
        .keno-header { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 11px; color: var(--text-muted); }
        .keno-grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 3px; }
        .keno-num { background: #12181f; border: 1px solid #232f3e; color: #fff; text-align: center; padding: 6px 0; border-radius: 4px; font-size: 9px; font-weight: bold; cursor: pointer; }
        .keno-num.selected { background: #0288d1; color: #fff; }
        .keno-num.drawn-regular { background: #29b6f6; color: #000; }
        .keno-num.ticket-matched { background: var(--accent-yellow) !important; color: #000 !important; font-weight: 900; }
        .keno-spinning-box-container { display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 10px; background: #0c1015; padding: 8px; border-radius: 8px; border: 1px solid var(--border-color); }
        .spinning-label { font-size: 11px; color: var(--text-muted); font-weight: bold; }
        .spinning-slot { width: 50px; height: 35px; background: #1a222d; border: 2px solid var(--accent-yellow); border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 16px; font-weight: 900; color: var(--accent-yellow); }
        .recent-keno-detailed-box { background: #0c1015; border-radius: 8px; padding: 10px; border: 1px solid var(--border-color); margin-bottom: 10px; }
        .recent-keno-title { font-size: 11px; font-weight: bold; color: var(--accent-yellow); margin-bottom: 6px; display: flex; justify-content: space-between; border-bottom: 1px solid var(--border-color); padding-bottom: 4px; }
        .keno-history-row { font-size: 10px; padding: 4px 0; border-bottom: 1px solid #1a222d; display: flex; flex-direction: column; gap: 3px; }
        .keno-history-balls { display: flex; flex-wrap: wrap; gap: 2px; }
        .kh-ball { background: #1a222d; border: 1px solid #29b6f6; color: #29b6f6; padding: 1px 4px; border-radius: 3px; font-size: 8px; font-weight: bold; }
        
        /* 1. KENO HISTORY HIGHLIGHT STYLES (MATCHING TICKETS/HITS) */
        .kh-ball.hit-match { background: var(--accent-yellow) !important; color: #000 !important; border-color: #fff !important; font-weight: 900 !important; box-shadow: 0 0 6px var(--accent-yellow); }

        .t-num-badge { background: #26323f; border: 1px solid #37474f; color: #fff; padding: 2px 4px; border-radius: 4px; font-size: 9px; display: inline-block; margin: 1px; }
        .t-num-badge.hit { background: var(--accent-yellow) !important; color: #000 !important; font-weight: 900; }
        
        .stat-summary-box { background: #0c1015; border: 1px solid var(--border-color); border-radius: 6px; padding: 6px 10px; margin-bottom: 8px; font-size: 11px; font-weight: bold; color: var(--accent-yellow); display: flex; justify-content: space-between; align-items: center; }
    </style>
</head>
<body>

    {% if not logged_in %}
    <div class="auth-container">
        <div class="auth-header">
            <div class="logo-text">ETHIO<span>BET</span></div>
            <div class="auth-top-btns">
                <button class="btn-top-login">Log in</button>
                <button class="btn-top-reg" onclick="register()">Registration</button>
            </div>
        </div>

        <div class="auth-title-bar">
            <div class="back-arrow">←</div>
            <span>LOG IN</span>
        </div>

        <div class="auth-tabs">
            <div class="auth-tab"><span class="auth-tab-icon">✉️</span><span>Email</span></div>
            <div class="auth-tab active"><span class="auth-tab-icon">📱</span><span>Phone</span></div>
            <div class="auth-tab"><span class="auth-tab-icon">💬</span><span>Code</span></div>
            <div class="auth-tab"><span class="auth-tab-icon">👥</span><span>Social</span></div>
        </div>

        <div class="auth-body">
            <div class="phone-input-group">
                <div class="country-code-box">
                    <img src="https://flagcdn.com/w40/et.png" class="flag-icon" alt="ET Flag">
                    <span>+251</span>
                </div>
                <input type="text" id="auth-phone" class="auth-input" placeholder="Phone number">
            </div>

            <div class="password-input-wrapper">
                <input type="password" id="auth-password" class="auth-input" placeholder="Password*">
                <span class="eye-icon" onclick="togglePasswordVisibility()">👁️</span>
            </div>

            <div class="auth-options">
                <label class="remember-me"><input type="checkbox" checked><span>Remember me</span></label>
                <span class="forgot-pass">Forgot password?</span>
            </div>

            <button class="btn-login-submit" onclick="login()">LOG IN</button>

            <div class="register-footer">
                <span>Don't have an account? </span>
                <a onclick="register()">Register</a>
            </div>
        </div>
    </div>

    {% else %}
    <div class="top-nav">
        <div class="logo-text" onclick="showHomeScreen()">ETHIO<span>BET</span></div>
        <div class="balance-container">
            <div class="balance-pill"><span id="user-balance">{{ "%.2f"|format(balance) }}</span> ETB</div>
            <button class="btn-deposit" onclick="openDepositModal()">+ Dep</button>
            <button class="btn-withdraw" onclick="openWithdrawModal()">- With</button>
            {% if is_admin %}
            <a href="/admin" style="background: #0288d1; color: #fff; text-decoration: none; padding: 5px 8px; border-radius: 6px; font-size: 11px; font-weight: bold;">ADMIN</a>
            {% endif %}
            <a href="/logout" class="btn-logout">ውጣ</a>
        </div>
    </div>

    <div id="home-dashboard-view">
        <h3 style="font-size: 14px; color: var(--text-muted); margin-bottom: 10px; font-weight: bold;">የጨዋታ ምርጫዎች (SELECT GAME)</h3>
        <div class="home-game-menu">
            
            <div class="game-banner-card card-shamo" onclick="switchGame('keno')">
                <div class="card-brand-header">
                    <span>ETHIO<span>BET</span></span>
                </div>
                <div class="card-center-content">
                    <div class="keno-balls-preview">
                        <div class="k-ball">30</div>
                        <div class="k-ball">8</div>
                        <div class="k-ball">67</div>
                    </div>
                    <div class="shamo-title">ሻሞ</div>
                </div>
                <div class="card-footer-btn">PLAY KENO ▶</div>
            </div>

            <div class="game-banner-card card-birabiro" onclick="switchGame('aviator')">
                <div class="card-brand-header">
                    <span>ETHIO<span>BET</span></span>
                </div>
                <div class="card-center-content">
                    <div class="birabiro-title">በራሪው</div>
                    <div style="font-size: 30px;">✈️</div>
                </div>
                <div class="card-footer-btn">PLAY JET ▶</div>
            </div>

            <div class="game-banner-card card-bingo" onclick="switchGame('bingo')">
                <div class="card-brand-header">
                    <span>ETHIO<span>BET</span></span>
                </div>
                <div class="card-center-content">
                    <div class="bingo-title">ቢንጎ</div>
                    <div style="font-size: 30px;">🎱</div>
                </div>
                <div class="card-footer-btn">PLAY BINGO ▶</div>
            </div>

        </div>
    </div>

    <div class="game-nav-bar">
        <div class="nav-btn active" id="btn-nav-home" onclick="showHomeScreen()">🏠 HOME</div>
        <div class="nav-btn" id="btn-nav-keno" onclick="switchGame('keno')">🎱 ሻሞ</div>
        <div class="nav-btn" id="btn-nav-aviator" onclick="switchGame('aviator')">✈️ በራሪው</div>
        <div class="nav-btn" id="btn-nav-bingo" onclick="switchGame('bingo')">🎯 ቢንጎ</div>
        <div class="nav-btn" id="btn-nav-history" onclick="switchGame('history')">📜 HISTORY</div>
    </div>

    <!-- ================= AVIATOR SECTION ================= -->
    <div id="aviator-section" style="display: none;">
        <div class="game-top-bar">
            <span style="font-size: 12px; font-weight: bold; color: var(--accent-yellow);">በራሪው (JET ✈️)</span>
            <button class="menu-btn" onclick="toggleDropdownMenu(event, 'aviator-dropdown-menu')">⋮</button>
            <div class="dropdown-menu-box" id="aviator-dropdown-menu">
                <div class="dropdown-item" onclick="openAviatorLimitsModal()">⚙️ የጨዋታ ገደብ (Limits)</div>
                <div class="dropdown-item" onclick="openAviatorHistoryModal()">📜 የአቪዬተር ሂስትሪ</div>
            </div>
        </div>

        <div class="multiplier-bar" id="aviator-history-bar">
            <div class="mult-tag green">2.10x</div>
            <div class="mult-tag blue">1.45x</div>
            <div class="mult-tag pink">3.20x</div>
        </div>

        <div class="aviator-screen" id="aviator-screen-box">
            <canvas id="aviator-canvas" class="aviator-canvas"></canvas>
            <div class="aviator-mult" id="aviator-mult-display">1.00x</div>
            <!-- 2. JET ICON ✈️ REPLACED HERE -->
            <div class="plane-img" id="plane-icon" style="color: #ff1744;">✈️</div>
        </div>

        <div class="dual-bet-container">
            <div class="bet-card">
                <div class="number-picker">
                    <button class="num-btn" onclick="adjustBet(1, -5)">-</button>
                    <input type="number" class="num-input" id="aviator-bet-val-1" value="10.00" onchange="onManualBetChange(1, this.value)">
                    <button class="num-btn" onclick="adjustBet(1, 5)">+</button>
                </div>
                <div class="auto-controls-row">
                    <label style="display: flex; align-items: center; gap: 4px; cursor: pointer;">
                        <input type="checkbox" id="auto-cash-toggle-1" checked onchange="toggleAutoCashInput(1)"> አውቶ
                    </label>
                    <input type="text" class="auto-cash-input" id="auto-cash-val-1" value="2.00">
                </div>
                <button class="btn-start-bet" id="aviator-bet-btn-1" onclick="handleAviatorBtnClick(1)">
                    <span class="btn-title" id="aviator-btn-title-1">BET #1</span>
                    <span class="btn-sub" id="aviator-btn-sub-1">10.00 ETB</span>
                </button>
            </div>

            <div class="bet-card">
                <div class="number-picker">
                    <button class="num-btn" onclick="adjustBet(2, -5)">-</button>
                    <input type="number" class="num-input" id="aviator-bet-val-2" value="20.00" onchange="onManualBetChange(2, this.value)">
                    <button class="num-btn" onclick="adjustBet(2, 5)">+</button>
                </div>
                <div class="auto-controls-row">
                    <label style="display: flex; align-items: center; gap: 4px; cursor: pointer;">
                        <input type="checkbox" id="auto-cash-toggle-2" checked onchange="toggleAutoCashInput(2)"> አውቶ
                    </label>
                    <input type="text" class="auto-cash-input" id="auto-cash-val-2" value="2.00">
                </div>
                <button class="btn-start-bet" id="aviator-bet-btn-2" onclick="handleAviatorBtnClick(2)">
                    <span class="btn-title" id="aviator-btn-title-2">BET #2</span>
                    <span class="btn-sub" id="aviator-btn-sub-2">20.00 ETB</span>
                </button>
            </div>
        </div>

        <div class="live-bets-panel">
            <div class="stat-summary-box">
                <span>አጠቃላይ/ካሻውት: <span id="aviator-stat-ratio" style="color:#fff;">0/0</span></span>
                <span>የወጣ ብር: <span id="aviator-stat-totalwin" style="color:var(--accent-green);">0.00 ETB</span></span>
            </div>

            <div class="live-bets-title">
                <span>የአቪዬተር የቀጥታ መደቦች (LIVE BETS)</span>
                <span style="color: var(--accent-green);" id="aviator-live-count">0 Bets</span>
            </div>
            <div id="aviator-live-bets-list">
                <p style="font-size: 11px; color: var(--text-muted);">በዚህ ዙር የተመደበ የለም።</p>
            </div>
        </div>
    </div>

    <!-- ================= KENO SECTION ================= -->
    <div id="keno-section" style="display: none;">
        <div class="game-top-bar">
            <span style="font-size: 12px; font-weight: bold; color: var(--accent-yellow);">ሻሞ (KENO - Max 20 Tickets)</span>
            <button class="menu-btn" onclick="toggleDropdownMenu(event, 'keno-dropdown-menu')">⋮</button>
            <div class="dropdown-menu-box" id="keno-dropdown-menu">
                <div class="dropdown-item" onclick="openModal('keno-limits-modal')">⚙️ የጨዋታ ገደብ (Limits)</div>
                <div class="dropdown-item" onclick="openKenoHistoryModal()">📜 የኬኖ ታሪክ (History)</div>
            </div>
        </div>

        <div class="stat-summary-box">
            <span>በዚህ ዙር የተመደቡ አጠቃላይ የጨዋታዎች ብዛት፦</span>
            <span id="keno-total-round-bets" style="font-size: 13px; color: var(--accent-green);">0</span>
        </div>

        <div class="recent-keno-detailed-box">
            <div class="recent-keno-title">
                <span>ያለፉት 3 የኬኖ ጨዋታዎች ውጤት</span>
            </div>
            <div id="recent-keno-detailed-list">
                <div class="keno-history-row"><span>ጨዋታ #1: ጫን...</span></div>
                <div class="keno-history-row"><span>ጨዋታ #2: ጫን...</span></div>
                <div class="keno-history-row"><span>ጨዋታ #3: ጫን...</span></div>
            </div>
        </div>

        <div class="keno-spinning-box-container">
            <span class="spinning-label">እየተሽከረከረ የሚወጣ እጣ:</span>
            <div class="spinning-slot" id="keno-spinner-slot">--</div>
        </div>

        <div class="keno-board-container">
            <div class="keno-header">
                <span>1 እስከ 80 ቁጥሮችን ይምረጡ (ከ1 እስከ 10)</span>
                <span>ቀጣይ እጣ: <b id="keno-timer-display" style="color: var(--accent-pink);">45s</b></span>
            </div>
            <div class="keno-grid" id="keno-grid-board"></div>
        </div>

        <div class="bet-card" style="margin-bottom: 10px;">
            <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 8px;">
                <button style="flex: 1; padding: 10px; background: #29b6f6; color: #000; font-weight: 900; border:none; border-radius:6px; cursor:pointer;" onclick="selectRandomKenoNumbers()">
                    🎲 RANDOM PICK (በዘፍቀድ)
                </button>
                <button style="padding: 10px 14px; background: #ff1744; color: #fff; font-weight: bold; border:none; border-radius:6px; cursor:pointer;" onclick="clearKenoSelection()">
                    🧹 CLEAR
                </button>
            </div>
            <div style="display: flex; gap: 8px; align-items: center;">
                <div class="number-picker" style="flex: 1; margin-bottom: 0;">
                    <button class="num-btn" onclick="adjustKenoBet(-5)">-</button>
                    <input type="number" class="num-input" id="keno-bet-val" value="10.00" min="5" max="12000" onchange="onManualKenoBetChange(this.value)" style="width: 80px;">
                    <button class="num-btn" onclick="adjustKenoBet(5)">+</button>
                </div>
                <button style="flex: 1; padding: 10px; background: var(--accent-yellow); color: #000; font-weight: bold; border:none; border-radius:6px; cursor:pointer;" onclick="addKenoTicket()">
                    + ADD TICKET
                </button>
            </div>
        </div>

        <div class="live-bets-panel">
            <div class="live-bets-title">
                <span>የኬኖ የተመደቡ ቲኬቶች (<span id="keno-tickets-count">0</span>/20)</span>
                <button class="btn-start-bet" id="keno-place-all-btn" style="width: 100px; padding: 4px 0;" onclick="placeAllKenoBets()">
                    <span class="btn-title">PLACE ALL</span>
                </button>
            </div>
            <div id="keno-tickets-list">
                <p style="font-size: 11px; color: var(--text-muted);">ምንም የተዘጋጀ ቲኬት የለም።</p>
            </div>
        </div>
    </div>

    <!-- ================= BINGO SECTION ================= -->
    <div id="bingo-section" style="display: none;">
        <div class="game-top-bar">
            <span style="font-size: 12px; font-weight: bold; color: var(--accent-green);">75-BALL BINGO (ቢንጎ)</span>
            <button class="menu-btn" onclick="showHomeScreen()">❌</button>
        </div>

        <!-- BINGO MENU VIEW -->
        <div id="bingo-menu-view">
            <h3 style="font-size: 13px; color: var(--accent-yellow); margin-bottom: 8px;">1. የመደብ መጠን ይምረጡ (50 & 100 Added)</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px;">
                <button style="padding: 10px; background: #1a222d; border: 2px solid var(--accent-green); color: #fff; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 11px;" onclick="selectBingoStake(10)">
                    10 ETB Room
                </button>
                <button style="padding: 10px; background: #1a222d; border: 2px solid var(--accent-yellow); color: #fff; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 11px;" onclick="selectBingoStake(30)">
                    30 ETB Room
                </button>
                <button style="padding: 10px; background: #1a222d; border: 2px solid var(--accent-orange); color: #fff; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 11px;" onclick="selectBingoStake(50)">
                    50 ETB Room (New)
                </button>
                <button style="padding: 10px; background: #1a222d; border: 2px solid var(--accent-pink); color: #fff; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 11px;" onclick="selectBingoStake(100)">
                    100 ETB Room (New)
                </button>
            </div>

            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <h3 style="font-size: 13px; color: var(--accent-yellow);">2. ካርድ ይምረጡ (የተመረጡ: <span id="bingo-selected-count">0</span>)</h3>
                <div style="display: flex; gap: 6px;">
                    <button style="padding: 4px 8px; background: #0288d1; color: #fff; border: none; border-radius: 4px; font-weight: bold; font-size: 11px; cursor: pointer;" onclick="pickRandomBingoCard()">🎲 RANDOM</button>
                    <button style="padding: 4px 8px; background: #ff1744; color: #fff; border: none; border-radius: 4px; font-weight: bold; font-size: 11px; cursor: pointer;" onclick="clearAllBingoCards()">🧹 CLEAR</button>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; max-height: 180px; overflow-y: auto; background: #0c1015; padding: 8px; border-radius: 8px; border: 1px solid var(--border-color); margin-bottom: 12px;" id="bingo-card-selector">
            </div>

            <button class="btn-start-bet" style="padding: 12px;" onclick="joinBingoGame()">JOIN BINGO GAME ▶</button>
        </div>

        <!-- BINGO GAMEPLAY VIEW -->
        <div id="bingo-game-view" style="display: none;">
            <div style="display: flex; justify-content: space-between; align-items: center; background: #0c1015; padding: 8px; border-radius: 6px; margin-bottom: 8px; font-size: 11px;">
                <span>ካርዶች: <b id="bingo-player-count" style="color: var(--accent-green);">0</b></span>
                <span>ሁኔታ: <b id="bingo-room-status" style="color: var(--accent-yellow);">በቂ ተጫዋች በመጠባበቅ ላይ...</b></span>
                <span>ቆጠራ: <b id="bingo-room-timer" style="color: var(--accent-pink);">--</b></span>
            </div>

            <div style="text-align: center; margin-bottom: 8px; background: #1a222d; padding: 6px; border-radius: 6px;">
                <span style="font-size: 11px; color: var(--text-muted);">የወጣ ቁጥር / ፖት (POT):</span>
                <div id="bingo-current-call" style="font-size: 24px; font-weight: 900; color: var(--accent-yellow);">--</div>
                <div style="font-size: 11px; color: var(--accent-green);" id="bingo-pot-display">POT: 0 ETB</div>
            </div>

            <div id="bingo-cards-wrapper" style="max-height: 300px; overflow-y: auto;"></div>

            <div style="display: flex; gap: 8px; margin-top: 8px;">
                <button class="btn-start-bet" style="padding: 10px; background: var(--accent-yellow); color: #000;" onclick="switchGame('bingo'); resetBingoToMenu();">
                    ➕ JOIN (ተጨማሪ ግባ)
                </button>
                <button class="btn-start-bet" id="btn-cancel-bingo" style="padding: 10px; background: #ff1744; color: #fff;" onclick="cancelBingoSelection()">
                    ✖ CANCEL (ሰርዝ)
                </button>
            </div>
        </div>
    </div>

    <!-- ================= HISTORY SECTION ================= -->
    <div id="history-section" class="bet-card" style="display: none;">
        <h3 style="margin-bottom: 10px; color: var(--accent-orange); font-size: 14px;">የእርስዎ የጨዋታ ሂስትሪ (BET HISTORY)</h3>
        <table class="history-table">
            <thead>
                <tr>
                    <th>ጨዋታ</th>
                    <th>መደብ</th>
                    <th>ውጤት</th>
                    <th>ያሸነፉት</th>
                </tr>
            </thead>
            <tbody id="user-history-tbody">
                <tr><td colspan="4" style="text-align: center; color: var(--text-muted);">ምንም ሂስትሪ የለም</td></tr>
            </tbody>
        </table>
    </div>

    <!-- ================= MODALS ================= -->
    <div class="modal-overlay" id="bingo-winner-modal">
        <div class="modal-box">
            <h2 style="color: var(--accent-yellow); margin-bottom: 10px; font-size: 24px;">🎉 BINGO WINNER! 🎉</h2>
            <div id="bingo-winner-details" style="font-size: 14px; margin-bottom: 15px; color: #fff;"></div>
            <button style="width: 100%; padding: 10px; background: var(--accent-green); color: #000; border: none; border-radius: 6px; font-weight: 900; cursor: pointer;" onclick="closeModal('bingo-winner-modal')">OK / ቀጥል</button>
        </div>
    </div>

    <div class="modal-overlay" id="keno-limits-modal">
        <div class="modal-box">
            <h3 style="color: var(--accent-yellow); margin-bottom: 12px;">⚙️ የኬኖ (Keno) መደብ ገደብ</h3>
            <div style="background: #0c1015; padding: 12px; border-radius: 6px; border: 1px solid var(--border-color); font-size: 13px; line-height: 1.8; margin-bottom: 12px;">
                <div>• <b>አነስተኛ መደብ:</b> <span style="color: var(--accent-green);">5.00 ETB</span></div>
                <div>• <b>ከፍተኛ መደብ:</b> <span style="color: var(--accent-pink);">12,000.00 ETB</span></div>
                <div>• <b>የቲኬት ገደብ:</b> <span style="color: var(--accent-yellow);">ከ20 በላይ ቲኬት መቁረጥ አይቻልም</span></div>
            </div>
            <button style="width: 100%; padding: 8px; background: #26323f; color: #fff; border: none; border-radius: 4px; cursor: pointer;" onclick="closeModal('keno-limits-modal')">ዝጋ</button>
        </div>
    </div>

    <div class="modal-overlay" id="keno-history-modal">
        <div class="modal-box" style="max-width: 420px;">
            <h3 style="color: var(--accent-yellow); margin-bottom: 12px;">📜 የኬኖ ታሪክ (Keno History)</h3>
            <div style="max-height: 250px; overflow-y: auto; margin-bottom: 12px;">
                <table class="history-table">
                    <thead>
                        <tr>
                            <th>መደብ</th>
                            <th>የወጡት/ቁጥሮች</th>
                            <th>ያሸነፉት</th>
                        </tr>
                    </thead>
                    <tbody id="keno-only-history-tbody">
                        <tr><td colspan="3" style="text-align: center; color: var(--text-muted);">ምንም የኬኖ ታሪክ የለም</td></tr>
                    </tbody>
                </table>
            </div>
            <button style="width: 100%; padding: 8px; background: #26323f; color: #fff; border: none; border-radius: 4px; cursor: pointer;" onclick="closeModal('keno-history-modal')">ዝጋ</button>
        </div>
    </div>

    <div class="modal-overlay" id="aviator-limits-modal">
        <div class="modal-box">
            <h3 style="color: var(--accent-yellow); margin-bottom: 12px;">⚙️ የአቪዬተር መደብ ገደብ</h3>
            <div style="background: #0c1015; padding: 12px; border-radius: 6px; border: 1px solid var(--border-color); font-size: 13px; line-height: 1.8; margin-bottom: 12px;">
                <div>• <b>አነስተኛ መደብ:</b> <span style="color: var(--accent-green);">5.00 ETB</span></div>
                <div>• <b>ከፍተኛ መደብ:</b> <span style="color: var(--accent-pink);">12,000.00 ETB</span></div>
            </div>
            <button style="width: 100%; padding: 8px; background: #26323f; color: #fff; border: none; border-radius: 4px; cursor: pointer;" onclick="closeModal('aviator-limits-modal')">ዝጋ</button>
        </div>
    </div>

    <div class="modal-overlay" id="aviator-history-modal">
        <div class="modal-box" style="max-width: 420px;">
            <h3 style="color: var(--accent-orange); margin-bottom: 12px;">📜 የአቪዬተር ብቻ ሂስትሪ</h3>
            <div style="max-height: 250px; overflow-y: auto; margin-bottom: 12px;">
                <table class="history-table">
                    <thead>
                        <tr>
                            <th>መደብ</th>
                            <th>ኤክስ (Multiplier)</th>
                            <th>ያሸነፉት</th>
                        </tr>
                    </thead>
                    <tbody id="aviator-only-history-tbody">
                        <tr><td colspan="3" style="text-align: center; color: var(--text-muted);">ምንም ሂስትሪ የለም</td></tr>
                    </tbody>
                </table>
            </div>
            <button style="width: 100%; padding: 8px; background: #26323f; color: #fff; border: none; border-radius: 4px; cursor: pointer;" onclick="closeModal('aviator-history-modal')">ዝጋ</button>
        </div>
    </div>

    <div class="modal-overlay" id="deposit-modal">
        <div class="modal-box">
            <h3 style="color: var(--accent-green); margin-bottom: 10px;">ብር ማስገቢያ (Deposit)</h3>
            <div style="background: #0c1015; border: 1px solid var(--accent-green); border-radius: 6px; padding: 10px; margin-bottom: 12px; font-size: 12px; line-height: 1.6;">
                <div style="color: var(--accent-yellow); font-weight: bold; margin-bottom: 4px;">📱 በቴሌብር (Telebirr) ገቢ ማድረጊያ:</div>
                <div><b>ስልክ ቁጥር:</b> <span style="color: var(--accent-green); font-weight: bold;">0997384093</span></div>
                <div><b>ስም:</b> <span style="color: #fff; font-weight: bold;">አብድል ዋሂድ</span></div>
            </div>
            <input type="number" id="dep-amount-input" class="form-control" placeholder="የላኩት ብር መጠን (ETB)">
            <button class="btn-start-bet" style="width: 100%; height: 40px; margin-bottom: 6px;" onclick="submitDepositForm()">SUBMIT DEPOSIT</button>
            <button style="width: 100%; padding: 8px; background: #26323f; color: #fff; border: none; border-radius: 4px; cursor: pointer;" onclick="closeModal('deposit-modal')">ዝጋ</button>
        </div>
    </div>

    <div class="modal-overlay" id="withdraw-modal">
        <div class="modal-box">
            <h3 style="color: var(--accent-orange); margin-bottom: 10px;">ብር ማውጫ (Withdraw)</h3>
            <select id="with-method" class="form-control">
                <option value="Telebirr">Telebirr</option>
                <option value="CBE Birr">CBE Birr</option>
            </select>
            <input type="text" id="with-account" class="form-control" placeholder="የመቀበያ ስልክ / አካውንት">
            <input type="number" id="with-amount" class="form-control" placeholder="የምታወጡት ብር መጠን">
            <button class="btn-start-bet" style="width: 100%; height: 40px; margin-bottom: 6px; background: linear-gradient(180deg, #ff9800 0%, #e65100 100%);" onclick="submitWithdrawForm()">WITHDRAW</button>
            <button style="width: 100%; padding: 8px; background: #26323f; color: #fff; border: none; border-radius: 4px; cursor: pointer;" onclick="closeModal('withdraw-modal')">ዝጋ</button>
        </div>
    </div>
    {% endif %}

    <!-- ================= JAVASCRIPT LOGIC ================= -->
    <script>
        let currentMultiplier = 1.00;
        let isGameRunning = false;
        let drawnKenoNumbers = [];
        let flightPoints = [];
        let isKenoDrawingActive = false;

        const KENO_ODDS = {
            1: {1: 3.5}, 2: {1: 1.0, 2: 10.0}, 3: {0: 0.0, 1: 0.0, 2: 2.0, 3: 50.0},
            4: {2: 1.5, 3: 10.0, 4: 80.0}, 5: {2: 1.0, 3: 3.0, 4: 30.0, 5: 150.0},
            6: {3: 2.0, 4: 15.0, 5: 60.0, 6: 500.0}, 7: {0: 1.0, 3: 2.0, 4: 4.0, 5: 20.0, 6: 80.0, 7: 1000.0},
            8: {0: 1.0, 4: 5.0, 5: 15.0, 6: 50.0, 7: 200.0, 8: 2000.0}, 9: {0: 2.0, 4: 2.0, 5: 10.0, 6: 25.0, 7: 125.0, 8: 1000.0, 9: 5000.0},
            10: {0: 2.0, 5: 5.0, 6: 30.0, 7: 100.0, 8: 300.0, 9: 2000.0, 10: 10000.0}
        };

        function showHomeScreen() {
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            document.getElementById('btn-nav-home').classList.add('active');

            document.getElementById('home-dashboard-view').style.display = 'block';
            document.getElementById('aviator-section').style.display = 'none';
            document.getElementById('keno-section').style.display = 'none';
            document.getElementById('bingo-section').style.display = 'none';
            document.getElementById('history-section').style.display = 'none';
        }

        function switchGame(game) {
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            document.getElementById('home-dashboard-view').style.display = 'none';
            document.getElementById('aviator-section').style.display = 'none';
            document.getElementById('keno-section').style.display = 'none';
            document.getElementById('bingo-section').style.display = 'none';
            document.getElementById('history-section').style.display = 'none';

            document.getElementById('btn-nav-' + game).classList.add('active');
            document.getElementById(game + '-section').style.display = 'block';

            if(game === 'history') fetchUserHistory();
            if(game === 'bingo') resetBingoToMenu();
            if(game === 'aviator') resizeCanvas();
        }

        function togglePasswordVisibility() {
            let pwd = document.getElementById('auth-password');
            pwd.type = (pwd.type === 'password') ? 'text' : 'password';
        }

        function toggleDropdownMenu(e, menuId) {
            e.stopPropagation();
            let menu = document.getElementById(menuId);
            let isVisible = menu.style.display === 'block';
            document.querySelectorAll('.dropdown-menu-box').forEach(m => m.style.display = 'none');
            menu.style.display = isVisible ? 'none' : 'block';
        }

        document.addEventListener('click', function() {
            document.querySelectorAll('.dropdown-menu-box').forEach(m => m.style.display = 'none');
        });

        function openAviatorLimitsModal() { document.getElementById('aviator-limits-modal').style.display = 'flex'; }
        
        function openKenoHistoryModal() {
            fetch('/user_history').then(r=>r.json()).then(d=>{
                let tbody = document.getElementById('keno-only-history-tbody');
                let kenoHist = d.history ? d.history.filter(h => h.game.includes('Keno') || h.game.includes('ሻሞ')) : [];
                
                if(kenoHist.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="3" style="text-align: center; color: var(--text-muted);">ምንም የኬኖ ታሪክ የለም</td></tr>`;
                } else {
                    let html = "";
                    kenoHist.forEach(h => {
                        let isWin = h.win_amount > 0;
                        html += `<tr>
                            <td><b>${h.bet_amount} ETB</b></td>
                            <td>${h.result_info}</td>
                            <td class="${isWin ? 'badge-win' : 'badge-loss'}">${isWin ? '+' + h.win_amount + ' ETB' : '0.00 ETB'}</td>
                        </tr>`;
                    });
                    tbody.innerHTML = html;
                }
                document.getElementById('keno-history-modal').style.display = 'flex';
            });
        }

        function openAviatorHistoryModal() {
            fetch('/user_history').then(r=>r.json()).then(d=>{
                let tbody = document.getElementById('aviator-only-history-tbody');
                let aviatorHist = d.history ? d.history.filter(h => h.game === 'Aviator') : [];
                
                if(aviatorHist.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="3" style="text-align: center; color: var(--text-muted);">ምንም የአቪዬተር ሂስትሪ የለም</td></tr>`;
                } else {
                    let html = "";
                    aviatorHist.forEach(h => {
                        let isWin = h.win_amount > 0;
                        html += `<tr>
                            <td><b>${h.bet_amount} ETB</b></td>
                            <td>${h.result_info}</td>
                            <td class="${isWin ? 'badge-win' : 'badge-loss'}">${isWin ? '+' + h.win_amount + ' ETB' : '0.00 ETB'}</td>
                        </tr>`;
                    });
                    tbody.innerHTML = html;
                }
                document.getElementById('aviator-history-modal').style.display = 'flex';
            });
        }

        /* ================= BINGO SYSTEM LOGIC (3. CONTINUOUS TIMER FIX) ================= */
        let selectedBingoStake = 10;
        let selectedBingoCardIds = [];
        let currentBingoCardsData = [];
        let bingoTimerInterval = null;
        let bingoCallInterval = null;
        let bingoCallsList = [];
        let bingoStatusPollInterval = null;
        let bingoCurrentTimeLeft = 30;
        let bingoHasWonCurrentGame = false;

        const cardSelectorContainer = document.getElementById('bingo-card-selector');
        if(cardSelectorContainer) {
            let html = "";
            for(let i = 1; i <= 100; i++) {
                html += `<div id="b-card-btn-${i}" onclick="toggleBingoCardNum(${i})" style="background: #1a222d; color: #fff; text-align: center; padding: 8px 0; border-radius: 4px; font-weight: bold; cursor: pointer; border: 1px solid var(--border-color); font-size: 11px;">#${i}</div>`;
            }
            cardSelectorContainer.innerHTML = html;
        }

        function selectBingoStake(amount) {
            selectedBingoStake = amount;
            alert(amount + " ETB Room ተመርጧል!");
        }

        function toggleBingoCardNum(cardId) {
            if(selectedBingoCardIds.includes(cardId)) {
                selectedBingoCardIds = selectedBingoCardIds.filter(id => id !== cardId);
            } else {
                selectedBingoCardIds.push(cardId);
            }
            updateBingoCardSelectionUI();
        }

        function pickRandomBingoCard() {
            let r = Math.floor(Math.random() * 100) + 1;
            if(!selectedBingoCardIds.includes(r)) {
                selectedBingoCardIds.push(r);
            }
            updateBingoCardSelectionUI();
        }

        function clearAllBingoCards() {
            selectedBingoCardIds = [];
            updateBingoCardSelectionUI();
        }

        function updateBingoCardSelectionUI() {
            document.getElementById('bingo-selected-count').innerText = selectedBingoCardIds.length;
            for(let i = 1; i <= 100; i++) {
                let el = document.getElementById('b-card-btn-' + i);
                if(el) {
                    if(selectedBingoCardIds.includes(i)) {
                        el.style.background = 'var(--accent-yellow)';
                        el.style.color = '#000';
                    } else {
                        el.style.background = '#1a222d';
                        el.style.color = '#fff';
                    }
                }
            }
        }

        function resetBingoToMenu() {
            clearInterval(bingoTimerInterval);
            clearInterval(bingoCallInterval);
            clearInterval(bingoStatusPollInterval);
            bingoTimerInterval = null;
            bingoHasWonCurrentGame = false;
            document.getElementById('bingo-menu-view').style.display = 'block';
            document.getElementById('bingo-game-view').style.display = 'none';
            document.getElementById('btn-cancel-bingo').style.display = 'block';
        }

        function joinBingoGame() {
            if(selectedBingoCardIds.length === 0) {
                alert("እባክዎን ቢያንስ አንድ ካርድ ይምረጡ!");
                return;
            }

            let fd = new FormData();
            fd.append('stake', selectedBingoStake);
            fd.append('card_ids', JSON.stringify(selectedBingoCardIds));

            fetch('/join_bingo', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{
                if(!d.success) { alert(d.message); return; }
                
                document.getElementById('user-balance').innerText = d.new_balance.toFixed(2);
                currentBingoCardsData = d.cards;
                renderAllBingoCards(d.cards);

                document.getElementById('bingo-menu-view').style.display = 'none';
                document.getElementById('bingo-game-view').style.display = 'block';
                
                startBingoLobbyPolling();
            });
        }

        function cancelBingoSelection() {
            if(bingoCurrentTimeLeft <= 15) {
                alert("ጨዋታው ለመጀመር 15 ሰከንድ ወይም ከዚያ በታች ስለቀረው ካንሰል ማድረግ አይቻልም!");
                return;
            }

            let fd = new FormData();
            fd.append('stake', selectedBingoStake);
            fd.append('card_count', currentBingoCardsData ? currentBingoCardsData.length : selectedBingoCardIds.length);

            fetch('/cancel_bingo', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{
                if(d.success) {
                    alert(d.message);
                    document.getElementById('user-balance').innerText = d.new_balance.toFixed(2);
                    resetBingoToMenu();
                } else {
                    alert(d.message);
                }
            });
        }

        function startBingoLobbyPolling() {
            if (bingoStatusPollInterval) clearInterval(bingoStatusPollInterval);
            bingoStatusPollInterval = setInterval(() => {
                fetch(`/bingo_room_status?stake=${selectedBingoStake}`).then(r=>r.json()).then(data => {
                    document.getElementById('bingo-player-count').innerText = data.player_count;
                    document.getElementById('bingo-pot-display').innerText = "POT: " + data.pot.toFixed(2) + " ETB";

                    // Continuously ensure timer engine stays active without resetting prematurely
                    if(data.player_count < 2) {
                        document.getElementById('bingo-room-status').innerText = "ቢያንስ 2 ተጫዋች ያስፈልጋል...";
                        document.getElementById('bingo-room-timer').innerText = "መጠባበቅ";
                    } else {
                        document.getElementById('bingo-room-status').innerText = "ተጫዋች ተሟልቷል! ቆጠራ ላይ...";
                        if(!bingoTimerInterval && data.status === "WAITING") {
                            startBingoTimerEngine();
                        }
                    }
                });
            }, 1000);
        }

        function renderAllBingoCards(cards) {
            let wrapper = document.getElementById('bingo-cards-wrapper');
            wrapper.innerHTML = "";

            cards.forEach((cardObj) => {
                let cardEl = document.createElement('div');
                cardEl.className = 'bingo-card-container';
                cardEl.id = `bingo-card-container-${cardObj.id}`;

                let headers = ['B', 'I', 'N', 'G', 'O'];
                let html = `<div style="font-size:11px; font-weight:bold; color:var(--accent-yellow); margin-bottom:4px;">ካርድ #${cardObj.id}</div><div class="bingo-card-grid">`;

                headers.forEach(h => html += `<div class="bingo-header-cell">${h}</div>`);

                for(let r = 0; r < 5; r++) {
                    headers.forEach(h => {
                        let val = cardObj.card[h][r];
                        if(val === "FREE") {
                            html += `<div class="bingo-cell free marked" id="b-cell-${cardObj.id}-${h}-${r}" data-val="FREE">FREE</div>`;
                        } else {
                            html += `<div class="bingo-cell" id="b-cell-${cardObj.id}-${h}-${r}" data-val="${val}">${val}</div>`;
                        }
                    });
                }
                html += `</div>`;
                cardEl.innerHTML = html;
                wrapper.appendChild(cardEl);
            });
        }

        function autoMarkBingoNumber(num) {
            currentBingoCardsData.forEach((cardObj) => {
                let headers = ['B', 'I', 'N', 'G', 'O'];
                headers.forEach(h => {
                    for(let r = 0; r < 5; r++) {
                        let val = cardObj.card[h][r];
                        if(parseInt(val) === num) {
                            let cell = document.getElementById(`b-cell-${cardObj.id}-${h}-${r}`);
                            if(cell) {
                                cell.classList.add('marked');
                            }
                        }
                    }
                });
                checkBingoWinPattern(cardObj.id);
            });
        }

        function startBingoTimerEngine() {
            if(bingoTimerInterval) return; // Prevent duplicate interval loops
            bingoCurrentTimeLeft = 30;
            let timerEl = document.getElementById('bingo-room-timer');

            bingoTimerInterval = setInterval(() => {
                bingoCurrentTimeLeft--;
                timerEl.innerText = bingoCurrentTimeLeft + "s";

                if(bingoCurrentTimeLeft <= 15) {
                    let cancelBtn = document.getElementById('btn-cancel-bingo');
                    if(cancelBtn) cancelBtn.style.display = 'none';
                }

                if(bingoCurrentTimeLeft <= 0) {
                    clearInterval(bingoTimerInterval);
                    bingoTimerInterval = null;
                    if(bingoStatusPollInterval) clearInterval(bingoStatusPollInterval);
                    timerEl.innerText = "ተጀምሯል!";
                    document.getElementById('bingo-room-status').innerText = "ጨዋታው እየተካሄደ ነው!";
                    start75BingoCalls();
                }
            }, 1000);
        }

        function start75BingoCalls() {
            bingoCallsList = [];
            let pool = Array.from({length: 75}, (_, i) => i + 1);
            pool.sort(() => Math.random() - 0.5);

            let idx = 0;
            bingoCallInterval = setInterval(() => {
                if(idx < pool.length && !bingoHasWonCurrentGame) {
                    let num = pool[idx];
                    bingoCallsList.push(num);
                    
                    let letter = num <= 15 ? 'B' : (num <= 30 ? 'I' : (num <= 45 ? 'N' : (num <= 60 ? 'G' : 'O')));
                    document.getElementById('bingo-current-call').innerText = letter + "-" + num;
                    
                    autoMarkBingoNumber(num);
                    idx++;
                } else if (!bingoHasWonCurrentGame) {
                    clearInterval(bingoCallInterval);
                    alert("75ቱ ቁጥሮች ወጥተው አልቀዋል!");
                    resetBingoToMenu();
                }
            }, 2000);
        }

        function checkBingoWinPattern(cardId) {
            if (bingoHasWonCurrentGame) return;

            let headers = ['B', 'I', 'N', 'G', 'O'];
            let isWon = false;

            for(let r = 0; r < 5; r++) {
                let rowWin = true;
                headers.forEach(h => {
                    let cell = document.getElementById(`b-cell-${cardId}-${h}-${r}`);
                    if(!cell || !cell.classList.contains('marked')) rowWin = false;
                });
                if(rowWin) isWon = true;
            }

            headers.forEach(h => {
                let colWin = true;
                for(let r = 0; r < 5; r++) {
                    let cell = document.getElementById(`b-cell-${cardId}-${h}-${r}`);
                    if(!cell || !cell.classList.contains('marked')) colWin = false;
                }
                if(colWin) isWon = true;
            });

            let diag1Win = true;
            let diag2Win = true;
            for(let i = 0; i < 5; i++) {
                let cell1 = document.getElementById(`b-cell-${cardId}-${headers[i]}-${i}`);
                let cell2 = document.getElementById(`b-cell-${cardId}-${headers[4-i]}-${i}`);
                if(!cell1 || !cell1.classList.contains('marked')) diag1Win = false;
                if(!cell2 || !cell2.classList.contains('marked')) diag2Win = false;
            }
            if(diag1Win || diag2Win) isWon = true;

            if(isWon) {
                bingoHasWonCurrentGame = true;
                clearInterval(bingoCallInterval);
                
                let winContainer = document.getElementById(`bingo-card-container-${cardId}`);
                if(winContainer) winContainer.classList.add('winning-card');

                triggerBingoWinClaim(cardId);
            }
        }

        function triggerBingoWinClaim(winningCardId) {
            let fd = new FormData();
            fd.append('stake', selectedBingoStake);
            fd.append('card_id', winningCardId);

            fetch('/claim_bingo', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{
                if(d.success) {
                    document.getElementById('user-balance').innerText = d.new_balance.toFixed(2);
                    
                    let winDetails = document.getElementById('bingo-winner-details');
                    winDetails.innerHTML = `
                        <div>ያሸነፉበት ካርድ፡ <b>Card #${winningCardId}</b></div>
                        <div style="font-size: 20px; color: var(--accent-green); font-weight: 900; margin-top: 8px;">የሽልማት መጠን፡ ${d.win_amount.toFixed(2)} ETB</div>
                    `;
                    document.getElementById('bingo-winner-modal').style.display = 'flex';
                }
            });
        }

        /* ================= AVIATOR ENGINE ================= */
        let aviatorBets = {
            1: { amount: 10.00, status: 'NONE', winAmt: 0 },
            2: { amount: 20.00, status: 'NONE', winAmt: 0 }
        };

        let aviatorStats = { total: 0, cashedOut: 0, totalWinAmt: 0.0 };
        let canvas, ctx;

        function resizeCanvas() {
            let screenBox = document.getElementById('aviator-screen-box');
            canvas = document.getElementById('aviator-canvas');
            if(canvas && screenBox) {
                canvas.width = screenBox.clientWidth;
                canvas.height = screenBox.clientHeight;
                ctx = canvas.getContext('2d');
            }
        }

        function drawAviatorTrajectory() {
            if(!ctx || !canvas) return;
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            if(flightPoints.length > 1) {
                ctx.beginPath();
                ctx.moveTo(flightPoints[0].x, flightPoints[0].y);
                for(let i = 1; i < flightPoints.length; i++) {
                    ctx.lineTo(flightPoints[i].x, flightPoints[i].y);
                }
                ctx.strokeStyle = "rgba(255, 23, 68, 0.9)";
                ctx.lineWidth = 3;
                ctx.setLineDash([6, 4]);
                ctx.stroke();
                ctx.setLineDash([]);
            }
        }

        function toggleAutoCashInput(id) {
            let isChecked = document.getElementById(`auto-cash-toggle-${id}`).checked;
            document.getElementById(`auto-cash-val-${id}`).style.display = isChecked ? 'inline-block' : 'none';
        }

        function adjustBet(id, val) {
            if(aviatorBets[id].status !== 'NONE' && aviatorBets[id].status !== 'WAITING') return;
            let newAmt = Math.min(12000, Math.max(5, aviatorBets[id].amount + val));
            aviatorBets[id].amount = newAmt;
            document.getElementById(`aviator-bet-val-${id}`).value = aviatorBets[id].amount.toFixed(2);
            document.getElementById(`aviator-btn-sub-${id}`).innerText = aviatorBets[id].amount.toFixed(2) + " ETB";
        }

        function onManualBetChange(id, val) {
            if(aviatorBets[id].status !== 'NONE' && aviatorBets[id].status !== 'WAITING') return;
            let num = parseFloat(val);
            if(isNaN(num) || num < 5) num = 5.00;
            if(num > 12000) num = 12000.00;
            aviatorBets[id].amount = num;
            document.getElementById(`aviator-bet-val-${id}`).value = num.toFixed(2);
            document.getElementById(`aviator-btn-sub-${id}`).innerText = num.toFixed(2) + " ETB";
        }

        function handleAviatorBtnClick(id) {
            let state = aviatorBets[id].status;

            if(state === 'NONE') {
                if(isGameRunning) {
                    let fd = new FormData();
                    fd.append('amount', aviatorBets[id].amount);

                    fetch('/place_bet', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{
                        if(!d.success) { alert(d.message); return; }
                        document.getElementById('user-balance').innerText = d.new_balance.toFixed(2);
                        
                        aviatorBets[id].status = 'WAITING';
                        let btn = document.getElementById(`aviator-bet-btn-${id}`);
                        btn.className = 'btn-start-bet cancel';
                        document.getElementById(`aviator-btn-title-${id}`).innerText = "CANCEL";
                        document.getElementById(`aviator-btn-sub-${id}`).innerText = "ይሰረዝ (" + aviatorBets[id].amount.toFixed(2) + " ETB)";
                        renderAviatorLiveBets();
                    });
                    return;
                }

                let fd = new FormData();
                fd.append('amount', aviatorBets[id].amount);

                fetch('/place_bet', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{
                    if(!d.success) { alert(d.message); return; }
                    document.getElementById('user-balance').innerText = d.new_balance.toFixed(2);
                    
                    aviatorBets[id].status = 'BET';
                    let btn = document.getElementById(`aviator-bet-btn-${id}`);
                    btn.className = 'btn-start-bet cancel';
                    document.getElementById(`aviator-btn-title-${id}`).innerText = "CANCEL";
                    document.getElementById(`aviator-btn-sub-${id}`).innerText = "ሰርዝ (" + aviatorBets[id].amount.toFixed(2) + " ETB)";
                    renderAviatorLiveBets();
                });
            } 
            else if(state === 'BET' || state === 'WAITING') {
                let fd = new FormData();
                fd.append('amount', aviatorBets[id].amount);

                fetch('/cancel_bet', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{
                    if(d.success) {
                        document.getElementById('user-balance').innerText = d.new_balance.toFixed(2);
                        aviatorBets[id].status = 'NONE';
                        
                        let btn = document.getElementById(`aviator-bet-btn-${id}`);
                        btn.className = 'btn-start-bet';
                        document.getElementById(`aviator-btn-title-${id}`).innerText = `BET #${id}`;
                        document.getElementById(`aviator-btn-sub-${id}`).innerText = aviatorBets[id].amount.toFixed(2) + " ETB";
                        renderAviatorLiveBets();
                    }
                });
            }
            else if(state === 'RUNNING') {
                executeCashout(id);
            }
        }

        function executeCashout(id) {
            let b = aviatorBets[id];
            if(b.status !== 'RUNNING') return;

            let cashoutVal = (b.amount * currentMultiplier).toFixed(2);
            let fd = new FormData();
            fd.append('game', 'Aviator');
            fd.append('bet_amount', b.amount);
            fd.append('win_amount', cashoutVal);
            fd.append('result_info', currentMultiplier.toFixed(2) + "x");

            fetch('/cashout', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{
                if(d.success) {
                    document.getElementById('user-balance').innerText = d.new_balance.toFixed(2);
                    b.status = 'WON';
                    b.winAmt = cashoutVal;

                    aviatorStats.cashedOut += 1;
                    aviatorStats.totalWinAmt += parseFloat(cashoutVal);

                    let btn = document.getElementById(`aviator-bet-btn-${id}`);
                    btn.className = 'btn-start-bet won';
                    btn.disabled = false;
                    document.getElementById(`aviator-btn-title-${id}`).innerText = "CASHED OUT";
                    document.getElementById(`aviator-btn-sub-${id}`).innerText = cashoutVal + " ETB";
                    renderAviatorLiveBets();
                }
            });
        }

        function renderAviatorLiveBets() {
            let list = document.getElementById('aviator-live-bets-list');
            let countSpan = document.getElementById('aviator-live-count');
            if(!list) return;

            let activeBets = Object.keys(aviatorBets).filter(k => aviatorBets[k].status !== 'NONE');
            countSpan.innerText = activeBets.length + " Bets";

            document.getElementById('aviator-stat-ratio').innerText = `${aviatorStats.total}/${aviatorStats.cashedOut}`;
            document.getElementById('aviator-stat-totalwin').innerText = aviatorStats.totalWinAmt.toFixed(2) + " ETB";

            if(activeBets.length === 0) {
                list.innerHTML = `<p style="font-size: 11px; color: var(--text-muted);">በዚህ ዙር የተመደበ የለም።</p>`;
                return;
            }

            let html = "";
            activeBets.forEach(k => {
                let b = aviatorBets[k];
                if(b.status === 'RUNNING') {
                    let totalVal = (b.amount * currentMultiplier).toFixed(2);
                    let btn = document.getElementById(`aviator-bet-btn-${k}`);
                    btn.className = 'btn-start-bet flying';
                    document.getElementById(`aviator-btn-title-${k}`).innerText = "CASH OUT";
                    document.getElementById(`aviator-btn-sub-${k}`).innerText = `${totalVal} ETB (${currentMultiplier.toFixed(2)}x)`;
                }

                let statusText = "";
                if(b.status === 'WON') statusText = `<span style="color: var(--accent-green); font-weight: 900;">+${b.winAmt} ETB</span>`;
                else if(b.status === 'BET') statusText = `<span style="color: var(--accent-yellow);">ሳይጀምር የተያዘ</span>`;
                else if(b.status === 'WAITING') statusText = `<span style="color: var(--accent-orange);">ቀጣይ ዙር የሚጠብቅ</span>`;
                else if(b.status === 'RUNNING') statusText = `<span style="color: var(--accent-green); font-weight:bold;">${(b.amount * currentMultiplier).toFixed(2)} ETB 🚀</span>`;

                html += `<div class="live-bet-row"><span>መደብ #${k}: <b>${b.amount.toFixed(2)} ETB</b></span>${statusText}</div>`;
            });
            list.innerHTML = html;
        }

        function updateAviatorHistoryBar() {
            fetch('/aviator_history_data').then(r => r.json()).then(d => {
                let bar = document.getElementById('aviator-history-bar');
                if(!bar) return;
                let html = "";
                d.history.forEach(m => {
                    let colorClass = parseFloat(m) > 2.0 ? 'green' : (parseFloat(m) > 1.5 ? 'blue' : 'pink');
                    html += `<div class="mult-tag ${colorClass}">${m}</div>`;
                });
                bar.innerHTML = html;
            });
        }

        function runAviatorAutoEngine() {
            let multDisplay = document.getElementById('aviator-mult-display');
            let plane = document.getElementById('plane-icon');
            if(!multDisplay) return;

            resizeCanvas();
            flightPoints = [];
            currentMultiplier = 1.00;
            isGameRunning = true;
            multDisplay.style.color = "#fff";
            multDisplay.innerText = "1.00x";
            plane.innerText = "✈️";

            aviatorStats = { total: 0, cashedOut: 0, totalWinAmt: 0.0 };

            let rand = Math.random();
            let crashPoint = rand < 0.75 ? (Math.random() * 0.98 + 1.01).toFixed(2) : (Math.random() * 10.0 + 2.0).toFixed(2);

            setTimeout(() => {
                [1, 2].forEach(id => {
                    if(aviatorBets[id].status === 'BET') {
                        aviatorBets[id].status = 'RUNNING';
                        aviatorStats.total += 1;
                        let btn = document.getElementById(`aviator-bet-btn-${id}`);
                        btn.className = 'btn-start-bet flying';
                        btn.disabled = false;
                    }
                });
                renderAviatorLiveBets();
            }, 300);

            let timer = setInterval(() => {
                currentMultiplier += currentMultiplier > 5 ? 0.08 : 0.025;
                multDisplay.innerText = currentMultiplier.toFixed(2) + "x";
                
                let curX = Math.min((currentMultiplier - 1) * 28, canvas.width - 40);
                let curY = canvas.height - Math.min((currentMultiplier - 1) * 18, canvas.height - 40) - 20;

                flightPoints.push({x: curX + 15, y: curY + 15});
                drawAviatorTrajectory();

                if(plane) {
                    plane.style.transform = `translate(${curX}px, -${canvas.height - curY - 20}px)`;
                }

                [1, 2].forEach(id => {
                    if(aviatorBets[id].status === 'RUNNING') {
                        let isAutoCashEnabled = document.getElementById(`auto-cash-toggle-${id}`).checked;
                        if(isAutoCashEnabled) {
                            let autoCashInput = document.getElementById(`auto-cash-val-${id}`).value;
                            let targetMult = parseFloat(autoCashInput);
                            if(!isNaN(targetMult) && currentMultiplier >= targetMult) {
                                executeCashout(parseInt(id));
                            }
                        }
                    }
                });
                renderAviatorLiveBets();

                if(currentMultiplier >= parseFloat(crashPoint)) {
                    clearInterval(timer);
                    isGameRunning = false;
                    multDisplay.style.color = "var(--accent-pink)";
                    multDisplay.innerText = "FLEW AWAY @ " + crashPoint + "x";

                    plane.innerText = "💥🔥";

                    fetch('/add_aviator_history', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                        body: 'mult=' + crashPoint + 'x'
                    }).then(() => updateAviatorHistoryBar());

                    [1, 2].forEach(id => {
                        if(aviatorBets[id].status === 'RUNNING') {
                            let fd = new FormData();
                            fd.append('game', 'Aviator');
                            fd.append('bet_amount', aviatorBets[id].amount);
                            fd.append('win_amount', 0);
                            fd.append('result_info', crashPoint + "x (Crashed)");
                            fetch('/record_loss', {method: 'POST', body: fd});
                        }
                        
                        if(aviatorBets[id].status === 'WAITING') {
                            aviatorBets[id].status = 'BET';
                            let btn = document.getElementById(`aviator-bet-btn-${id}`);
                            btn.className = 'btn-start-bet cancel';
                            document.getElementById(`aviator-btn-title-${id}`).innerText = "CANCEL";
                            document.getElementById(`aviator-btn-sub-${id}`).innerText = "ሰርዝ (" + aviatorBets[id].amount.toFixed(2) + " ETB)";
                        } else {
                            aviatorBets[id].status = 'NONE';
                            let btn = document.getElementById(`aviator-bet-btn-${id}`);
                            btn.className = 'btn-start-bet';
                            btn.disabled = false;
                            document.getElementById(`aviator-btn-title-${id}`).innerText = `BET #${id}`;
                            document.getElementById(`aviator-btn-sub-${id}`).innerText = aviatorBets[id].amount.toFixed(2) + " ETB";
                        }
                    });

                    let countdown = 5;
                    let cdTimer = setInterval(() => {
                        multDisplay.innerText = "NEXT IN " + countdown + "s";
                        countdown--;
                        if(countdown < 0) {
                            clearInterval(cdTimer);
                            if(plane) plane.style.transform = `translate(0px, 0px)`;
                            runAviatorAutoEngine();
                        }
                    }, 1000);
                }
            }, 80);
        }

        /* ================= KENO ENGINE ================= */
        let selectedKenoList = [];
        let kenoTickets = [];
        let kenoBetAmount = 10.00;
        let kenoTotalRoundBetsCount = 0;
        const gridBoard = document.getElementById('keno-grid-board');

        if(gridBoard) {
            for(let i = 1; i <= 80; i++) {
                let cell = document.createElement('div');
                cell.className = 'keno-num';
                cell.innerText = i;
                cell.id = 'keno-cell-' + i;
                cell.onclick = () => selectKenoNum(i, cell);
                gridBoard.appendChild(cell);
            }
        }

        function selectKenoNum(num, el) {
            if(selectedKenoList.includes(num)) {
                selectedKenoList = selectedKenoList.filter(n => n !== num);
                el.classList.remove('selected');
            } else {
                if(selectedKenoList.length < 10) {
                    selectedKenoList.push(num);
                    el.classList.add('selected');
                } else { alert("ከ10 በላይ ቁጥሮችን መምረጥ አይችሉም!"); }
            }
        }

        function selectRandomKenoNumbers() {
            clearKenoSelection();
            let count = Math.floor(Math.random() * 5) + 4;
            let nums = [];
            while(nums.length < count) {
                let r = Math.floor(Math.random() * 80) + 1;
                if(!nums.includes(r)) nums.push(r);
            }
            nums.forEach(n => {
                let cell = document.getElementById('keno-cell-' + n);
                if(cell) selectKenoNum(n, cell);
            });
        }

        function clearKenoSelection() {
            selectedKenoList = [];
            document.querySelectorAll('.keno-num').forEach(e => e.classList.remove('selected'));
        }

        function adjustKenoBet(val) {
            let newBet = Math.min(12000, Math.max(5, kenoBetAmount + val));
            kenoBetAmount = newBet;
            document.getElementById('keno-bet-val').value = kenoBetAmount.toFixed(2);
        }

        function onManualKenoBetChange(val) {
            let num = parseFloat(val);
            if(isNaN(num) || num < 5) num = 5.00;
            if(num > 12000) num = 12000.00;
            kenoBetAmount = num;
            document.getElementById('keno-bet-val').value = num.toFixed(2);
        }

        function addKenoTicket() {
            if(isKenoDrawingActive) {
                alert("ጨዋታው ስለተጀመረ አሁን ቲኬት መጨመር አይቻልም!");
                return;
            }
            if(kenoTickets.length >= 20) {
                alert("በአንድ ዙር ከ 20 ቲኬት በላይ መቁረጥ አይቻልም!");
                return;
            }
            if(selectedKenoList.length === 0) { alert("ቢያንስ 1 ቁጥር ይምረጡ!"); return; }
            kenoTickets.push({ numbers: [...selectedKenoList], amount: kenoBetAmount, placed: false });
            clearKenoSelection();
            renderKenoTicketsUI();
        }

        function renderKenoTicketsUI() {
            let list = document.getElementById('keno-tickets-list');
            if(!list) return;
            document.getElementById('keno-tickets-count').innerText = kenoTickets.length;
            document.getElementById('keno-total-round-bets').innerText = kenoTotalRoundBetsCount;
            
            if(kenoTickets.length === 0) {
                list.innerHTML = `<p style="font-size: 11px; color: var(--text-muted);">ምንም የተዘጋጀ ቲኬት የለም።</p>`;
                return;
            }

            let html = "";
            kenoTickets.forEach((t, i) => {
                let numBadges = t.numbers.map(n => {
                    let isHit = drawnKenoNumbers.includes(n);
                    return `<span class="t-num-badge ${isHit ? 'hit' : ''}">${n}</span>`;
                }).join('');

                html += `<div class="live-bet-row" style="flex-direction: column; align-items: flex-start; gap: 4px;">
                    <div>ቲኬት #${i+1} (${t.numbers.length} ቁጥሮች) - <b>${t.amount.toFixed(2)} ETB</b> ${t.placed ? '✅ (ቆይቷል)' : ''}</div>
                    <div>${numBadges}</div>
                </div>`;
            });
            list.innerHTML = html;
        }

        function placeAllKenoBets() {
            let unplaced = kenoTickets.filter(t => !t.placed);
            if(unplaced.length === 0) { alert("የተመደበ አዲስ ቲኬት የለም!"); return; }

            let totalAmt = unplaced.reduce((acc, t) => acc + t.amount, 0);
            let fd = new FormData();
            fd.append('amount', totalAmt);

            fetch('/place_bet', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{
                if(!d.success) { alert(d.message); return; }
                document.getElementById('user-balance').innerText = d.new_balance.toFixed(2);
                
                unplaced.forEach(t => t.placed = true);
                kenoTotalRoundBetsCount += unplaced.length;
                renderKenoTicketsUI();
                alert("ቲኬቶች በትክክል ተመድበዋል!");
            });
        }

        function runKenoTimerEngine() {
            let timeLeft = 45;
            let timerDisplay = document.getElementById('keno-timer-display');
            let spinnerSlot = document.getElementById('keno-spinner-slot');
            
            setInterval(() => {
                timeLeft--;
                if(timerDisplay) timerDisplay.innerText = timeLeft + "s";

                if(timeLeft <= 5) {
                    isKenoDrawingActive = true;
                }

                if(timeLeft <= 0) {
                    timeLeft = 45;
                    isKenoDrawingActive = true;
                    drawnKenoNumbers = [];
                    
                    document.querySelectorAll('.keno-num').forEach(el => {
                        el.classList.remove('drawn-regular', 'ticket-matched', 'selected');
                    });
                    selectedKenoList = [];
                    renderKenoTicketsUI();
                    
                    fetch('/draw_keno_numbers').then(r=>r.json()).then(dData => {
                        let drawn = dData.drawn;
                        let index = 0;
                        let drawInterval = setInterval(() => {
                            if(index < drawn.length) {
                                let n = drawn[index];
                                drawnKenoNumbers.push(n);
                                
                                let spinCount = 0;
                                let spinTimer = setInterval(() => {
                                    if(spinnerSlot) spinnerSlot.innerText = Math.floor(Math.random() * 80) + 1;
                                    spinCount++;
                                    if(spinCount > 6) {
                                        clearInterval(spinTimer);
                                        if(spinnerSlot) spinnerSlot.innerText = n;
                                    }
                                }, 60);

                                let cell = document.getElementById('keno-cell-' + n);
                                if(cell) {
                                    cell.classList.add('drawn-regular');
                                    kenoTickets.forEach(t => {
                                        if(t.placed && t.numbers.includes(n)) {
                                            cell.classList.add('ticket-matched');
                                        }
                                    });
                                }
                                renderKenoTicketsUI();
                                index++;
                            } else {
                                clearInterval(drawInterval);
                                if(spinnerSlot) spinnerSlot.innerText = "✓";
                                evaluateKenoResults(drawn);
                                isKenoDrawingActive = false;
                            }
                        }, 650);
                    });
                }
            }, 1000);
        }

        function evaluateKenoResults(drawn) {
            fetch('/update_keno_history', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: 'draws=' + JSON.stringify(drawn)
            }).then(r => r.json()).then(d => {
                let listContainer = document.getElementById('recent-keno-detailed-list');
                if(listContainer && d.recent) {
                    let html = "";
                    d.recent.forEach((item, idx) => {
                        let ballsHtml = item.map(num => {
                            let isMatchedHit = drawnKenoNumbers.includes(num);
                            return `<span class="kh-ball ${isMatchedHit ? 'hit-match' : ''}">${num}</span>`;
                        }).join('');

                        html += `<div class="keno-history-row">
                            <span><b>ጨዋታ #${idx+1}</b> (ወጥተዋል: ${item.length} ቁጥሮች)</span>
                            <div class="keno-history-balls">${ballsHtml}</div>
                        </div>`;
                    });
                    listContainer.innerHTML = html;
                }
            });

            kenoTickets.forEach(t => {
                if(t.placed) {
                    let selectedCount = t.numbers.length;
                    let hits = t.numbers.filter(n => drawn.includes(n)).length;
                    
                    let multiplier = (KENO_ODDS[selectedCount] && KENO_ODDS[selectedCount][hits] !== undefined) 
                                     ? KENO_ODDS[selectedCount][hits] 
                                     : 0.0;

                    let winAmt = t.amount * multiplier;

                    if(winAmt > 0) {
                        let fd = new FormData();
                        fd.append('game', 'Keno (ሻሞ)');
                        fd.append('bet_amount', t.amount);
                        fd.append('win_amount', winAmt.toFixed(2));
                        fd.append('result_info', `${hits}/${selectedCount} Hits (${multiplier}x)`);
                        fetch('/cashout', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{
                            if(d.success) document.getElementById('user-balance').innerText = d.new_balance.toFixed(2);
                        });
                    } else {
                        let fd = new FormData();
                        fd.append('game', 'Keno (ሻሞ)');
                        fd.append('bet_amount', t.amount);
                        fd.append('result_info', `${hits}/${selectedCount} Hits (0x)`);
                        fetch('/record_loss', {method: 'POST', body: fd});
                    }
                }
            });
            
            kenoTickets = [];
            kenoTotalRoundBetsCount = 0;
            renderKenoTicketsUI();

            setTimeout(() => {
                document.querySelectorAll('.keno-num').forEach(el => {
                    el.classList.remove('drawn-regular', 'ticket-matched');
                });
            }, 3000);
        }

        function fetchUserHistory() {
            fetch('/user_history').then(r=>r.json()).then(d=>{
                let tbody = document.getElementById('user-history-tbody');
                if(!d.history || d.history.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: var(--text-muted);">ምንም ሂስትሪ የለም</td></tr>`;
                    return;
                }
                let html = "";
                d.history.forEach(h => {
                    let isWin = h.win_amount > 0;
                    html += `<tr>
                        <td><b>${h.game}</b></td>
                        <td>${h.bet_amount} ETB</td>
                        <td>${h.result_info}</td>
                        <td class="${isWin ? 'badge-win' : 'badge-loss'}">${isWin ? '+' + h.win_amount + ' ETB' : '0.00 ETB'}</td>
                    </tr>`;
                });
                tbody.innerHTML = html;
            });
        }

        window.onload = function() {
            runAviatorAutoEngine();
            runKenoTimerEngine();
            window.addEventListener('resize', resizeCanvas);
        };

        function login() {
            let fd = new FormData();
            fd.append('phone', document.getElementById('auth-phone').value);
            fd.append('password', document.getElementById('auth-password').value);
            fetch('/login', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{ if(d.success) location.reload(); else alert(d.message); });
        }
        function register() {
            let fd = new FormData();
            fd.append('phone', document.getElementById('auth-phone').value);
            fd.append('password', document.getElementById('auth-password').value);
            fetch('/register', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{ if(d.success) location.reload(); else alert(d.message); });
        }

        function openDepositModal() { document.getElementById('deposit-modal').style.display = 'flex'; }
        function openWithdrawModal() { document.getElementById('withdraw-modal').style.display = 'flex'; }
        function closeModal(id) { document.getElementById(id).style.display = 'none'; }
        
        function submitDepositForm() {
            let amount = document.getElementById('dep-amount-input').value;
            if(!amount) { alert("እባክዎን የብር መጠን ያስገቡ!"); return; }

            let fd = new FormData();
            fd.append('amount', amount);
            fetch('/deposit', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{
                alert(d.message); if(d.success) closeModal('deposit-modal');
            });
        }

        function submitWithdrawForm() {
            let method = document.getElementById('with-method').value;
            let account = document.getElementById('with-account').value;
            let amount = document.getElementById('with-amount').value;

            let fd = new FormData();
            fd.append('method', method); fd.append('account', account); fd.append('amount', amount);
            fetch('/withdraw', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{
                alert(d.message); if(d.success) closeModal('withdraw-modal');
            });
        }
    </script>
</body>
</html>
"""

ADMIN_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="am">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="5"> <!-- Auto refresh every 5 seconds -->
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ethio Bet - Admin Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; background: #12181f; color: #fff; padding: 20px; }
        h1, h2 { color: #f5a623; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 30px; background: #1a222d; }
        th, td { border: 1px solid #26323f; padding: 10px; text-align: left; }
        th { background: #0c1015; color: #8b949e; }
        .btn-approve { background: #00e676; color: #000; border: none; padding: 6px 12px; font-weight: bold; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }
        .btn-reject { background: #ff1744; color: #fff; border: none; padding: 6px 12px; font-weight: bold; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }
        .nav-home { color: #00e676; text-decoration: none; font-weight: bold; display: inline-block; margin-bottom: 20px; }
    </style>
</head>
<body>
    <a href="/" class="nav-home">← ወደ ዋናው ገጽ ተመለስ (Back to Home)</a>
    <h1>Admin Control Panel</h1>
    <p style="font-size: 12px; color: #8b949e;">ይህ ገጽ በየ 5 ሰከንዱ ራሱን ያድሳል (Auto-refreshes every 5s)</p>
    <hr style="border-color: #26323f; margin-bottom: 20px;">

    <h2>1. የዲፖዚት ጥያቄዎች (Deposit Requests)</h2>
    <table>
        <thead>
            <tr>
                <th>ተራ ቁጥር</th>
                <th>ስልክ ቁጥር</th>
                <th>መጠን (ETB)</th>
                <th>እርምጃ (Action)</th>
            </tr>
        </thead>
        <tbody>
            {% if not deposit_requests %}
            <tr><td colspan="4" style="text-align: center; color: #8b949e;">ምንም የዲፖዚት ጥያቄ የለም</td></tr>
            {% endif %}
            {% for req in deposit_requests %}
            <tr>
                <td>{{ loop.index }}</td>
                <td><b>{{ req.phone }}</b></td>
                <td style="color: #00e676; font-weight: bold;">{{ "%.2f"|format(req.amount) }} ETB</td>
                <td>
                    <a href="/admin/approve_deposit/{{ loop.index0 }}" class="btn-approve">አፅድቅ (Approve)</a>
                    <a href="/admin/reject_deposit/{{ loop.index0 }}" class="btn-reject">ሰርዝ (Reject)</a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <h2>2. የብር ማውጫ ጥያቄዎች (Withdraw Requests)</h2>
    <table>
        <thead>
            <tr>
                <th>ተራ ቁጥር</th>
                <th>ስልክ ቁጥር</th>
                <th>አካውንት/ስልክ</th>
                <th>ዘዴ</th>
                <th>መጠን (ETB)</th>
                <th>እርምጃ (Action)</th>
            </tr>
        </thead>
        <tbody>
            {% if not withdraw_requests %}
            <tr><td colspan="6" style="text-align: center; color: #8b949e;">ምንም የብር ማውጫ ጥያቄ የለም</td></tr>
            {% endif %}
            {% for req in withdraw_requests %}
            <tr>
                <td>{{ loop.index }}</td>
                <td><b>{{ req.phone }}</b></td>
                <td>{{ req.account }}</td>
                <td>{{ req.method }}</td>
                <td style="color: #ff9800; font-weight: bold;">{{ "%.2f"|format(req.amount) }} ETB</td>
                <td>
                    <a href="/admin/approve_withdraw/{{ loop.index0 }}" class="btn-approve">ተፈፅሟል (Complete)</a>
                    <a href="/admin/reject_withdraw/{{ loop.index0 }}" class="btn-reject">መልስ/ሰርዝ (Reject)</a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

@app.route('/')
def index():
    if 'user' not in session:
        return render_template_string(HTML_TEMPLATE, logged_in=False)
    
    phone = session['user']
    user_data = users_db.get(phone, {"balance": 0.0, "is_admin": False})
    return render_template_string(HTML_TEMPLATE, 
                                  logged_in=True, 
                                  phone=phone, 
                                  balance=user_data['balance'], 
                                  is_admin=user_data.get('is_admin', False))

@app.route('/register', methods=['POST'])
def register():
    phone = request.form.get('phone', '').strip()
    password = request.form.get('password', '').strip()
    if not phone or not password or phone in users_db:
        return jsonify({"success": False, "message": "መረጃው ተሳስቷል ወይም አስቀድሞ አለ!"})
    
    users_db[phone] = { "password": generate_password_hash(password), "balance": 0.0, "is_admin": False }
    session['user'] = phone
    return jsonify({"success": True})

@app.route('/login', methods=['POST'])
def login():
    phone = request.form.get('phone', '').strip()
    password = request.form.get('password', '').strip()
    user = users_db.get(phone)
    if user and check_password_hash(user['password'], password):
        session['user'] = phone
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "የተሳሳተ መረጃ!"})

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/place_bet', methods=['POST'])
def place_bet():
    if 'user' not in session: return jsonify({"success": False})
    phone = session['user']
    bet_amount = float(request.form.get('amount', 0))
    if users_db[phone]['balance'] < bet_amount or bet_amount <= 0:
        return jsonify({"success": False, "message": "በቂ ባላንስ የሎትም!"})
    users_db[phone]['balance'] -= bet_amount
    return jsonify({"success": True, "new_balance": users_db[phone]['balance']})

@app.route('/cancel_bet', methods=['POST'])
def cancel_bet():
    if 'user' not in session: return jsonify({"success": False})
    phone = session['user']
    amount = float(request.form.get('amount', 0))
    users_db[phone]['balance'] += amount
    return jsonify({"success": True, "new_balance": users_db[phone]['balance']})

@app.route('/cashout', methods=['POST'])
def cashout():
    if 'user' not in session: return jsonify({"success": False})
    phone = session['user']
    win_amount = float(request.form.get('win_amount', 0))
    bet_amount = float(request.form.get('bet_amount', 0))
    game = request.form.get('game', 'Game')
    result_info = request.form.get('result_info', '')

    users_db[phone]['balance'] += win_amount
    global_bet_history.append({"phone": phone, "game": game, "bet_amount": bet_amount, "win_amount": win_amount, "result_info": result_info})
    return jsonify({"success": True, "new_balance": users_db[phone]['balance']})

@app.route('/record_loss', methods=['POST'])
def record_loss():
    if 'user' not in session: return jsonify({"success": False})
    phone = session['user']
    bet_amount = float(request.form.get('bet_amount', 0))
    game = request.form.get('game', 'Game')
    result_info = request.form.get('result_info', '')

    global_bet_history.append({"phone": phone, "game": game, "bet_amount": bet_amount, "win_amount": 0, "result_info": result_info})
    return jsonify({"success": True})

@app.route('/draw_keno_numbers')
def draw_keno_numbers():
    drawn = random.sample(range(1, 81), 20)
    return jsonify({"drawn": drawn})

@app.route('/join_bingo', methods=['POST'])
def join_bingo():
    if 'user' not in session: return jsonify({"success": False, "message": "እባክዎን አስቀድመው ይግቡ!"})
    phone = session['user']
    stake = int(request.form.get('stake', 10))
    card_ids_str = request.form.get('card_ids', '[]')
    card_ids = json.loads(card_ids_str)

    total_stake = stake * len(card_ids)

    if users_db[phone]['balance'] < total_stake:
        return jsonify({"success": False, "message": "በቂ ባላንስ የሎትም!"})

    users_db[phone]['balance'] -= total_stake
    
    net_stake = total_stake * 0.80
    room = bingo_rooms.get(stake, bingo_rooms[10])
    
    if phone not in room['players']:
        room['players'][phone] = []
    
    room['players'][phone].extend(card_ids)
    room['pot'] += net_stake

    selected_cards = [{"id": cid, "card": BINGO_CARDS.get(cid)} for cid in card_ids]
    return jsonify({
        "success": True, 
        "new_balance": users_db[phone]['balance'], 
        "cards": selected_cards
    })

@app.route('/bingo_room_status')
def bingo_room_status():
    stake = int(request.args.get('stake', 10))
    room = bingo_rooms.get(stake, bingo_rooms[10])
    player_count = sum(len(cards) for cards in room['players'].values())
    return jsonify({
        "player_count": player_count,
        "pot": room['pot'],
        "status": room['status']
    })

@app.route('/claim_bingo', methods=['POST'])
def claim_bingo():
    if 'user' not in session: return jsonify({"success": False})
    phone = session['user']
    stake = int(request.form.get('stake', 10))
    room = bingo_rooms.get(stake, bingo_rooms[10])
    
    win_amount = room['pot'] if room['pot'] > 0 else stake * 2
    users_db[phone]['balance'] += win_amount
    room['pot'] = 0.0

    global_bet_history.append({"phone": phone, "game": f"Bingo ({stake} ETB Room)", "bet_amount": stake, "win_amount": win_amount, "result_info": "Bingo Won!"})
    return jsonify({"success": True, "new_balance": users_db[phone]['balance'], "win_amount": win_amount})

@app.route('/cancel_bingo', methods=['POST'])
def cancel_bingo():
    if 'user' not in session: return jsonify({"success": False})
    phone = session['user']
    stake = int(request.form.get('stake', 10))
    card_count = int(request.form.get('card_count', 1))
    
    refund_amount = stake * card_count
    users_db[phone]['balance'] += refund_amount
    
    room = bingo_rooms.get(stake, bingo_rooms[10])
    if phone in room['players']:
        room['players'].pop(phone, None)
        room['pot'] -= (refund_amount * 0.80)
        if room['pot'] < 0: room['pot'] = 0.0

    return jsonify({"success": True, "message": "ቲኬቱ ተሰርዟል፣ ብርዎ ተመልሷል!", "new_balance": users_db[phone]['balance']})

@app.route('/update_keno_history', methods=['POST'])
def update_keno_history():
    draws_str = request.form.get('draws', '[]')
    draws = json.loads(draws_str)
    keno_recent_draws.insert(0, draws)
    if len(keno_recent_draws) > 3:
        keno_recent_draws.pop()
    return jsonify({"success": True, "recent": keno_recent_draws})

@app.route('/aviator_history_data')
def aviator_history_data():
    return jsonify({"history": aviator_history_list})

@app.route('/add_aviator_history', methods=['POST'])
def add_aviator_history():
    mult = request.form.get('mult', '2.00x')
    aviator_history_list.insert(0, mult)
    if len(aviator_history_list) > 10:
        aviator_history_list.pop()
    return jsonify({"success": True})

@app.route('/user_history')
def user_history():
    if 'user' not in session: return jsonify({"history": []})
    phone = session['user']
    user_hist = [h for h in global_bet_history if h['phone'] == phone]
    return jsonify({"history": user_hist[::-1]})

@app.route('/deposit', methods=['POST'])
def deposit():
    if 'user' not in session: return jsonify({"success": False, "message": "እባክዎን አስቀድመው ይግቡ!"})
    try:
        amount = float(request.form.get('amount', 0))
    except ValueError:
        return jsonify({"success": False, "message": "እባክዎን ትክክለኛ የብር መጠን ያስገቡ!"})
        
    if amount <= 0: return jsonify({"success": False, "message": "ልክ ያልሆነ መጠን!"})
    deposit_requests.append({"phone": session['user'], "amount": amount})
    return jsonify({"success": True, "message": "የብር ማስገቢያ ጥያቄዎ ተልኳል! በቅርብ ጊዜ ይጸድቃል።"})

@app.route('/withdraw', methods=['POST'])
def withdraw():
    if 'user' not in session: return jsonify({"success": False, "message": "እባክዎን አስቀድመው ይግቡ!"})
    phone = session['user']
    try:
        amount = float(request.form.get('amount', 0))
    except ValueError:
        return jsonify({"success": False, "message": "እባክዎን ትክክለኛ የብር መጠን ያስገቡ!"})
        
    method = request.form.get('method', 'Telebirr')
    account = request.form.get('account', '')
    
    if users_db[phone]['balance'] < amount or amount <= 0:
        return jsonify({"success": False, "message": "በቂ ባላንስ የሎትም!"})
    
    users_db[phone]['balance'] -= amount
    withdraw_requests.append({"phone": phone, "amount": amount, "method": method, "account": account})
    return jsonify({"success": True, "message": "የብር ማውጫ ጥያቄዎ ተሳክቷል!"})

# ==========================================
# ADMIN DASHBOARD & REQUEST HANDLING ROUTES
# ==========================================
@app.route('/admin')
def admin():
    if 'user' not in session or not users_db.get(session['user'], {}).get('is_admin', False):
        return redirect(url_for('index'))
    return render_template_string(
        ADMIN_HTML_TEMPLATE, 
        deposit_requests=deposit_requests, 
        withdraw_requests=withdraw_requests
    )

@app.route('/admin/approve_deposit/<int:req_id>')
def approve_deposit(req_id):
    if 'user' not in session or not users_db.get(session['user'], {}).get('is_admin', False):
        return redirect(url_for('index'))
    if 0 <= req_id < len(deposit_requests):
        req = deposit_requests.pop(req_id)
        phone = req['phone']
        amount = req['amount']
        if phone in users_db:
            users_db[phone]['balance'] += amount
    return redirect(url_for('admin'))

@app.route('/admin/reject_deposit/<int:req_id>')
def reject_deposit(req_id):
    if 'user' not in session or not users_db.get(session['user'], {}).get('is_admin', False):
        return redirect(url_for('index'))
    if 0 <= req_id < len(deposit_requests):
        deposit_requests.pop(req_id)
    return redirect(url_for('admin'))

@app.route('/admin/approve_withdraw/<int:req_id>')
def approve_withdraw(req_id):
    if 'user' not in session or not users_db.get(session['user'], {}).get('is_admin', False):
        return redirect(url_for('index'))
    if 0 <= req_id < len(withdraw_requests):
        withdraw_requests.pop(req_id)
    return redirect(url_for('admin'))

@app.route('/admin/reject_withdraw/<int:req_id>')
def reject_withdraw(req_id):
    if 'user' not in session or not users_db.get(session['user'], {}).get('is_admin', False):
        return redirect(url_for('index'))
    if 0 <= req_id < len(withdraw_requests):
        req = withdraw_requests.pop(req_id)
        phone = req['phone']
        amount = req['amount']
        if phone in users_db:
            users_db[phone]['balance'] += amount
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    return card

BINGO_CARDS = {i: generate_bingo_card(i) for i in range(1, 101)}

bingo_rooms = {
    10: {"players": {}, "timer": 30, "status": "WAITING", "drawn": [], "pot": 0.0, "winners": []},
    30: {"players": {}, "timer": 30, "status": "WAITING", "drawn": [], "pot": 0.0, "winners": []},
    50: {"players": {}, "timer": 30, "status": "WAITING", "drawn": [], "pot": 0.0, "winners": []},
    100: {"players": {}, "timer": 30, "status": "WAITING", "drawn": [], "pot": 0.0, "winners": []}
}

KENO_ODDS = {
    1: {1: 3.5},
    2: {1: 1.0, 2: 10.0},
    3: {0: 0.0, 1: 0.0, 2: 2.0, 3: 50.0},
    4: {2: 1.5, 3: 10.0, 4: 80.0},
    5: {2: 1.0, 3: 3.0, 4: 30.0, 5: 150.0},
    6: {3: 2.0, 4: 15.0, 5: 60.0, 6: 500.0},
    7: {0: 1.0, 3: 2.0, 4: 4.0, 5: 20.0, 6: 80.0, 7: 1000.0},
    8: {0: 1.0, 4: 5.0, 5: 15.0, 6: 50.0, 7: 200.0, 8: 2000.0},
    9: {0: 2.0, 4: 2.0, 5: 10.0, 6: 25.0, 7: 125.0, 8: 1000.0, 9: 5000.0},
    10: {0: 2.0, 5: 5.0, 6: 30.0, 7: 100.0, 8: 300.0, 9: 2000.0, 10: 10000.0}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="am">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Ethio Bet - Premium Gaming Platform</title>
    <style>
        :root {
            --bg-dark: #12181f;
            --card-bg: #1a222d;
            --accent-green: #00e676;
            --accent-pink: #e91e63;
            --accent-orange: #ff9800;
            --accent-yellow: #f5a623;
            --text-main: #ffffff;
            --text-muted: #8b949e;
            --border-color: #26323f;
        }

        * { box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 0; }
        body { background-color: var(--bg-dark); color: var(--text-main); padding: 8px; }

        .top-nav { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: #0c1015; border-radius: 8px; margin-bottom: 12px; border: 1px solid var(--border-color); }
        .logo-text { font-weight: 900; font-size: 20px; color: #ffffff; font-style: italic; letter-spacing: 0.5px; cursor: pointer; }
        .logo-text span { color: var(--accent-yellow); }
        .balance-container { display: flex; align-items: center; gap: 6px; }
        .balance-pill { background: #070a0d; border: 1px solid #1f2936; border-radius: 20px; padding: 4px 10px; font-weight: bold; color: var(--accent-green); font-size: 13px; }
        .btn-deposit { background: var(--accent-green); color: #000; border: none; padding: 5px 10px; border-radius: 20px; font-weight: bold; font-size: 11px; cursor: pointer; }
        .btn-withdraw { background: var(--accent-orange); color: #000; border: none; padding: 5px 10px; border-radius: 20px; font-weight: bold; font-size: 11px; cursor: pointer; }
        .btn-logout { background: #ff1744; color: #fff; text-decoration: none; padding: 5px 8px; border-radius: 6px; font-size: 11px; font-weight: bold; }

        .auth-container { max-width: 420px; margin: 20px auto; background: #18222d; border-radius: 10px; overflow: hidden; border: 1px solid var(--border-color); box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
        .auth-header { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: #0e1620; border-bottom: 1px solid var(--border-color); }
        .auth-top-btns { display: flex; gap: 8px; }
        .btn-top-login { background: #2b3644; color: #fff; border: none; padding: 6px 14px; border-radius: 6px; font-weight: bold; font-size: 13px; cursor: pointer; }
        .btn-top-reg { background: var(--accent-yellow); color: #000; border: none; padding: 6px 14px; border-radius: 6px; font-weight: bold; font-size: 13px; cursor: pointer; }

        .auth-title-bar { display: flex; align-items: center; gap: 10px; padding: 14px 16px; font-size: 16px; font-weight: 800; color: #fff; border-bottom: 1px solid var(--border-color); }
        .back-arrow { background: #2b3644; color: #fff; width: 28px; height: 28px; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 14px; cursor: pointer; }

        .auth-tabs { display: grid; grid-template-columns: repeat(4, 1fr); background: #0f1722; border-bottom: 1px solid var(--border-color); }
        .auth-tab { padding: 12px 4px; text-align: center; font-size: 11px; color: var(--text-muted); cursor: pointer; border-bottom: 2px solid transparent; display: flex; flex-direction: column; align-items: center; gap: 4px; }
        .auth-tab.active { color: #fff; background: #18222d; border-bottom: 2px solid var(--accent-yellow); font-weight: bold; }

        .auth-body { padding: 20px 16px; }
        .phone-input-group { display: flex; gap: 8px; margin-bottom: 14px; }
        .country-code-box { background: #ffffff; color: #000; border-radius: 6px; padding: 0 10px; display: flex; align-items: center; gap: 6px; font-weight: bold; font-size: 13px; }
        .flag-icon { width: 20px; height: 14px; object-fit: cover; border-radius: 2px; }
        .auth-input { width: 100%; padding: 12px; background: #ffffff; color: #000; border: 1px solid #ccc; border-radius: 6px; font-size: 14px; font-weight: 600; outline: none; }
        .password-input-wrapper { position: relative; margin-bottom: 14px; }
        .eye-icon { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); color: #555; cursor: pointer; font-size: 16px; }

        .auth-options { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; font-size: 13px; }
        .remember-me { display: flex; align-items: center; gap: 8px; color: #ccc; cursor: pointer; }
        .forgot-pass { color: var(--accent-yellow); text-decoration: underline; cursor: pointer; font-weight: 500; }

        .btn-login-submit { width: 100%; background: var(--accent-yellow); color: #000; border: none; padding: 12px; border-radius: 6px; font-weight: 900; font-size: 15px; cursor: pointer; margin-bottom: 16px; }
        .register-footer { text-align: center; font-size: 13px; color: var(--text-muted); }
        .register-footer a { color: var(--accent-yellow); text-decoration: underline; font-weight: bold; cursor: pointer; }

        .home-game-menu { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 15px; }
        
        .game-banner-card { background: #1e2836; border-radius: 12px; overflow: hidden; border: 2px solid var(--border-color); cursor: pointer; position: relative; box-shadow: 0 8px 20px rgba(0,0,0,0.6); transition: transform 0.2s ease, border-color 0.2s ease; display: flex; flex-direction: column; justify-content: space-between; min-height: 200px; }
        .game-banner-card:hover { transform: translateY(-4px); border-color: var(--accent-yellow); }

        .card-shamo { background: radial-gradient(circle at center, #800000 0%, #300000 100%); }
        .card-birabiro { background: radial-gradient(circle at center, #2e1a00 0%, #110900 100%); }
        .card-bingo { background: radial-gradient(circle at center, #004d40 0%, #001a14 100%); }

        .card-brand-header { padding: 6px 8px; font-size: 10px; font-weight: 800; color: #fff; display: flex; justify-content: space-between; align-items: center; background: rgba(0,0,0,0.3); }
        .card-center-content { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 10px 4px; text-align: center; }

        .shamo-title { font-size: 28px; font-weight: 900; color: #ffe600; text-shadow: 2px 2px 0px #d32f2f; }
        .birabiro-title { font-size: 24px; font-weight: 900; color: #ff9800; }
        .bingo-title { font-size: 26px; font-weight: 900; color: #00e676; text-shadow: 0 0 10px rgba(0,230,118,0.5); }

        .card-footer-btn { background: rgba(0,0,0,0.5); padding: 6px; text-align: center; font-weight: bold; font-size: 10px; color: #fff; border-top: 1px solid rgba(255,255,255,0.1); }

        .game-nav-bar { display: flex; gap: 4px; margin-bottom: 12px; }
        .nav-btn { flex: 1; background: var(--card-bg); color: var(--text-muted); border: 1px solid var(--border-color); padding: 8px 4px; border-radius: 6px; font-weight: bold; font-size: 11px; cursor: pointer; text-align: center; }
        .nav-btn.active { background: #26323f; color: #fff; border-color: var(--accent-yellow); }

        .game-top-bar { display: flex; justify-content: space-between; align-items: center; position: relative; margin-bottom: 8px; padding: 4px 8px; background: #1a222d; border-radius: 8px; border: 1px solid var(--border-color); }
        .menu-btn { background: #26323f; border: 1px solid var(--border-color); color: #fff; font-size: 18px; font-weight: bold; width: 32px; height: 32px; border-radius: 6px; cursor: pointer; display: flex; align-items: center; justify-content: center; }
        .dropdown-menu-box { display: none; position: absolute; top: 40px; right: 8px; background: #1a222d; border: 1px solid var(--border-color); border-radius: 8px; box-shadow: 0 8px 20px rgba(0,0,0,0.8); z-index: 50; width: 180px; overflow: hidden; }
        .dropdown-item { padding: 10px 12px; font-size: 12px; color: #fff; cursor: pointer; display: flex; align-items: center; gap: 8px; border-bottom: 1px solid #26323f; }

        /* BINGO SPECIFIC STYLES */
        .bingo-card-container { background: #12181f; border: 1px solid var(--border-color); border-radius: 8px; padding: 6px; margin-bottom: 10px; }
        .bingo-card-container.winning-card { border: 2px solid var(--accent-yellow) !important; box-shadow: 0 0 15px rgba(245, 166, 35, 0.6); }
        .bingo-card-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px; background: #0c1015; padding: 8px; border-radius: 8px; }
        .bingo-header-cell { background: var(--accent-yellow); color: #000; font-weight: 900; text-align: center; padding: 6px; border-radius: 4px; font-size: 14px; }
        .bingo-cell { background: #1a222d; color: #fff; border: 1px solid var(--border-color); text-align: center; padding: 10px 0; font-weight: bold; font-size: 12px; border-radius: 4px; cursor: pointer; }
        .bingo-cell.marked { background: var(--accent-green); color: #000; font-weight: 900; box-shadow: 0 0 8px var(--accent-green); }
        .bingo-cell.free { background: var(--accent-pink); color: #fff; }

        .history-table { width: 100%; border-collapse: collapse; font-size: 11px; text-align: left; }
        .history-table th { background: #0c1015; padding: 6px; color: var(--text-muted); border-bottom: 1px solid var(--border-color); }
        .history-table td { padding: 6px; border-bottom: 1px solid #1a222d; }
        .badge-win { color: var(--accent-green); font-weight: bold; }
        .badge-loss { color: #ff1744; font-weight: bold; }

        .modal-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); justify-content: center; align-items: center; z-index: 100; }
        .modal-box { background: var(--card-bg); padding: 16px; border-radius: 10px; width: 90%; max-width: 380px; border: 1px solid var(--border-color); text-align: center; }
        .form-control { width: 100%; padding: 10px; background: #0c1015; border: 1px solid var(--border-color); color: #fff; border-radius: 6px; margin-bottom: 10px; font-size: 13px; }
        
        .btn-start-bet { background: linear-gradient(180deg, #00e676 0%, #00a855 100%); color: #000; border: none; border-radius: 8px; font-weight: 900; padding: 10px 0; cursor: pointer; text-align: center; width: 100%; transition: all 0.2s ease; }
        .btn-start-bet.cancel { background: linear-gradient(180deg, #ff1744 0%, #b71c1c 100%) !important; color: #fff !important; }
        .btn-start-bet.flying { background: linear-gradient(180deg, #ffea00 0%, #f57f17 100%) !important; color: #000 !important; }
        .btn-start-bet.won { background: linear-gradient(180deg, #00e676 0%, #00a855 100%) !important; color: #000 !important; }

        .number-picker { background: #0c1015; border-radius: 6px; border: 1px solid var(--border-color); display: flex; align-items: center; justify-content: space-between; padding: 2px 4px; margin-bottom: 6px; }
        .num-btn { background: #26323f; color: #fff; border: none; width: 28px; height: 28px; border-radius: 4px; font-size: 16px; font-weight: bold; cursor: pointer; }
        .num-input { background: transparent; border: none; color: #fff; text-align: center; font-size: 14px; font-weight: bold; width: 60px; outline: none; }
        .bet-card { background: var(--card-bg); border-radius: 10px; border: 1px solid var(--border-color); padding: 10px; }
        .keno-balls-preview { display: flex; gap: 4px; margin-bottom: 6px; }
        .k-ball { width: 20px; height: 20px; background: radial-gradient(circle at 30% 30%, #ffeb3b, #f57f17); color: #000; border-radius: 50%; font-size: 9px; font-weight: 900; display: flex; align-items: center; justify-content: center; }
        .multiplier-bar { display: flex; gap: 6px; overflow-x: auto; padding: 4px 0; margin-bottom: 8px; white-space: nowrap; height: 32px; align-items: center; }
        .mult-tag { background: #1a222d; border-radius: 4px; padding: 2px 8px; font-size: 11px; font-weight: bold; border: 1px solid var(--border-color); display: inline-block; }
        .mult-tag.green { color: var(--accent-green); }
        .mult-tag.pink { color: var(--accent-pink); }
        .mult-tag.blue { color: #29b6f6; }
        
        .aviator-screen { background: radial-gradient(circle at center, #1e2836 0%, #0c1015 100%); height: 140px; border-radius: 12px; border: 1px solid var(--border-color); position: relative; display: flex; flex-direction: column; justify-content: center; align-items: center; margin-bottom: 10px; overflow: hidden; }
        .aviator-mult { font-size: 32px; font-weight: 900; color: #fff; z-index: 2; }
        .plane-img { font-size: 32px; position: absolute; bottom: 10px; left: 10px; transition: transform 0.05s linear; z-index: 3; filter: drop-shadow(0 0 8px rgba(255, 23, 68, 0.9)); }
        .aviator-canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; pointer-events: none; }
        
        .dual-bet-container { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 10px; }
        .auto-controls-row { display: flex; justify-content: space-between; align-items: center; font-size: 10px; color: var(--text-muted); margin-bottom: 6px; background: #0c1015; padding: 4px 6px; border-radius: 4px; }
        .auto-cash-input { background: #1a222d; border: 1px solid var(--border-color); color: #fff; width: 45px; text-align: center; font-size: 10px; border-radius: 3px; }
        .live-bets-panel { background: var(--card-bg); border-radius: 8px; padding: 8px; border: 1px solid var(--border-color); margin-bottom: 10px; }
        .live-bets-title { font-size: 11px; font-weight: bold; color: var(--text-muted); margin-bottom: 6px; display: flex; justify-content: space-between; border-bottom: 1px solid var(--border-color); padding-bottom: 4px; }
        .live-bet-row { display: flex; justify-content: space-between; font-size: 11px; padding: 4px 0; border-bottom: 1px solid #1a222d; align-items: center; }
        .keno-board-container { background: var(--card-bg); border-radius: 10px; padding: 10px; border: 1px solid var(--border-color); margin-bottom: 10px; }
        .keno-header { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 11px; color: var(--text-muted); }
        .keno-grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 3px; }
        .keno-num { background: #12181f; border: 1px solid #232f3e; color: #fff; text-align: center; padding: 6px 0; border-radius: 4px; font-size: 9px; font-weight: bold; cursor: pointer; }
        .keno-num.selected { background: #0288d1; color: #fff; }
        .keno-num.drawn-regular { background: #29b6f6; color: #000; }
        .keno-num.ticket-matched { background: var(--accent-yellow) !important; color: #000 !important; font-weight: 900; }
        .keno-spinning-box-container { display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 10px; background: #0c1015; padding: 8px; border-radius: 8px; border: 1px solid var(--border-color); }
        .spinning-label { font-size: 11px; color: var(--text-muted); font-weight: bold; }
        .spinning-slot { width: 50px; height: 35px; background: #1a222d; border: 2px solid var(--accent-yellow); border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 16px; font-weight: 900; color: var(--accent-yellow); }
        .recent-keno-detailed-box { background: #0c1015; border-radius: 8px; padding: 10px; border: 1px solid var(--border-color); margin-bottom: 10px; }
        .recent-keno-title { font-size: 11px; font-weight: bold; color: var(--accent-yellow); margin-bottom: 6px; display: flex; justify-content: space-between; border-bottom: 1px solid var(--border-color); padding-bottom: 4px; }
        .keno-history-row { font-size: 10px; padding: 4px 0; border-bottom: 1px solid #1a222d; display: flex; flex-direction: column; gap: 3px; }
        .keno-history-balls { display: flex; flex-wrap: wrap; gap: 2px; }
        .kh-ball { background: #1a222d; border: 1px solid #29b6f6; color: #29b6f6; padding: 1px 4px; border-radius: 3px; font-size: 8px; font-weight: bold; }
        
        /* 1. KENO HISTORY HIGHLIGHT STYLES (MATCHING TICKETS/HITS) */
        .kh-ball.hit-match { background: var(--accent-yellow) !important; color: #000 !important; border-color: #fff !important; font-weight: 900 !important; box-shadow: 0 0 6px var(--accent-yellow); }

        .t-num-badge { background: #26323f; border: 1px solid #37474f; color: #fff; padding: 2px 4px; border-radius: 4px; font-size: 9px; display: inline-block; margin: 1px; }
        .t-num-badge.hit { background: var(--accent-yellow) !important; color: #000 !important; font-weight: 900; }
        
        .stat-summary-box { background: #0c1015; border: 1px solid var(--border-color); border-radius: 6px; padding: 6px 10px; margin-bottom: 8px; font-size: 11px; font-weight: bold; color: var(--accent-yellow); display: flex; justify-content: space-between; align-items: center; }
    </style>
</head>
<body>

    {% if not logged_in %}
    <div class="auth-container">
        <div class="auth-header">
            <div class="logo-text">ETHIO<span>BET</span></div>
            <div class="auth-top-btns">
                <button class="btn-top-login">Log in</button>
                <button class="btn-top-reg" onclick="register()">Registration</button>
            </div>
        </div>

        <div class="auth-title-bar">
            <div class="back-arrow">←</div>
            <span>LOG IN</span>
        </div>

        <div class="auth-tabs">
            <div class="auth-tab"><span class="auth-tab-icon">✉️</span><span>Email</span></div>
            <div class="auth-tab active"><span class="auth-tab-icon">📱</span><span>Phone</span></div>
            <div class="auth-tab"><span class="auth-tab-icon">💬</span><span>Code</span></div>
            <div class="auth-tab"><span class="auth-tab-icon">👥</span><span>Social</span></div>
        </div>

        <div class="auth-body">
            <div class="phone-input-group">
                <div class="country-code-box">
                    <img src="https://flagcdn.com/w40/et.png" class="flag-icon" alt="ET Flag">
                    <span>+251</span>
                </div>
                <input type="text" id="auth-phone" class="auth-input" placeholder="Phone number">
            </div>

            <div class="password-input-wrapper">
                <input type="password" id="auth-password" class="auth-input" placeholder="Password*">
                <span class="eye-icon" onclick="togglePasswordVisibility()">👁️</span>
            </div>

            <div class="auth-options">
                <label class="remember-me"><input type="checkbox" checked><span>Remember me</span></label>
                <span class="forgot-pass">Forgot password?</span>
            </div>

            <button class="btn-login-submit" onclick="login()">LOG IN</button>

            <div class="register-footer">
                <span>Don't have an account? </span>
                <a onclick="register()">Register</a>
            </div>
        </div>
    </div>

    {% else %}
    <div class="top-nav">
        <div class="logo-text" onclick="showHomeScreen()">ETHIO<span>BET</span></div>
        <div class="balance-container">
            <div class="balance-pill"><span id="user-balance">{{ "%.2f"|format(balance) }}</span> ETB</div>
            <button class="btn-deposit" onclick="openDepositModal()">+ Dep</button>
            <button class="btn-withdraw" onclick="openWithdrawModal()">- With</button>
            {% if is_admin %}
            <a href="/admin" style="background: #0288d1; color: #fff; text-decoration: none; padding: 5px 8px; border-radius: 6px; font-size: 11px; font-weight: bold;">ADMIN</a>
            {% endif %}
            <a href="/logout" class="btn-logout">ውጣ</a>
        </div>
    </div>

    <div id="home-dashboard-view">
        <h3 style="font-size: 14px; color: var(--text-muted); margin-bottom: 10px; font-weight: bold;">የጨዋታ ምርጫዎች (SELECT GAME)</h3>
        <div class="home-game-menu">
            
            <div class="game-banner-card card-shamo" onclick="switchGame('keno')">
                <div class="card-brand-header">
                    <span>ETHIO<span>BET</span></span>
                </div>
                <div class="card-center-content">
                    <div class="keno-balls-preview">
                        <div class="k-ball">30</div>
                        <div class="k-ball">8</div>
                        <div class="k-ball">67</div>
                    </div>
                    <div class="shamo-title">ሻሞ</div>
                </div>
                <div class="card-footer-btn">PLAY KENO ▶</div>
            </div>

            <div class="game-banner-card card-birabiro" onclick="switchGame('aviator')">
                <div class="card-brand-header">
                    <span>ETHIO<span>BET</span></span>
                </div>
                <div class="card-center-content">
                    <div class="birabiro-title">በራሪው</div>
                    <div style="font-size: 30px;">✈️</div>
                </div>
                <div class="card-footer-btn">PLAY JET ▶</div>
            </div>

            <div class="game-banner-card card-bingo" onclick="switchGame('bingo')">
                <div class="card-brand-header">
                    <span>ETHIO<span>BET</span></span>
                </div>
                <div class="card-center-content">
                    <div class="bingo-title">ቢንጎ</div>
                    <div style="font-size: 30px;">🎱</div>
                </div>
                <div class="card-footer-btn">PLAY BINGO ▶</div>
            </div>

        </div>
    </div>

    <div class="game-nav-bar">
        <div class="nav-btn active" id="btn-nav-home" onclick="showHomeScreen()">🏠 HOME</div>
        <div class="nav-btn" id="btn-nav-keno" onclick="switchGame('keno')">🎱 ሻሞ</div>
        <div class="nav-btn" id="btn-nav-aviator" onclick="switchGame('aviator')">✈️ በራሪው</div>
        <div class="nav-btn" id="btn-nav-bingo" onclick="switchGame('bingo')">🎯 ቢንጎ</div>
        <div class="nav-btn" id="btn-nav-history" onclick="switchGame('history')">📜 HISTORY</div>
    </div>

    <!-- ================= AVIATOR SECTION ================= -->
    <div id="aviator-section" style="display: none;">
        <div class="game-top-bar">
            <span style="font-size: 12px; font-weight: bold; color: var(--accent-yellow);">በራሪው (JET ✈️)</span>
            <button class="menu-btn" onclick="toggleDropdownMenu(event, 'aviator-dropdown-menu')">⋮</button>
            <div class="dropdown-menu-box" id="aviator-dropdown-menu">
                <div class="dropdown-item" onclick="openAviatorLimitsModal()">⚙️ የጨዋታ ገደብ (Limits)</div>
                <div class="dropdown-item" onclick="openAviatorHistoryModal()">📜 የአቪዬተር ሂስትሪ</div>
            </div>
        </div>

        <div class="multiplier-bar" id="aviator-history-bar">
            <div class="mult-tag green">2.10x</div>
            <div class="mult-tag blue">1.45x</div>
            <div class="mult-tag pink">3.20x</div>
        </div>

        <div class="aviator-screen" id="aviator-screen-box">
            <canvas id="aviator-canvas" class="aviator-canvas"></canvas>
            <div class="aviator-mult" id="aviator-mult-display">1.00x</div>
            <!-- 2. JET ICON ✈️ REPLACED HERE -->
            <div class="plane-img" id="plane-icon" style="color: #ff1744;">✈️</div>
        </div>

        <div class="dual-bet-container">
            <div class="bet-card">
                <div class="number-picker">
                    <button class="num-btn" onclick="adjustBet(1, -5)">-</button>
                    <input type="number" class="num-input" id="aviator-bet-val-1" value="10.00" onchange="onManualBetChange(1, this.value)">
                    <button class="num-btn" onclick="adjustBet(1, 5)">+</button>
                </div>
                <div class="auto-controls-row">
                    <label style="display: flex; align-items: center; gap: 4px; cursor: pointer;">
                        <input type="checkbox" id="auto-cash-toggle-1" checked onchange="toggleAutoCashInput(1)"> አውቶ
                    </label>
                    <input type="text" class="auto-cash-input" id="auto-cash-val-1" value="2.00">
                </div>
                <button class="btn-start-bet" id="aviator-bet-btn-1" onclick="handleAviatorBtnClick(1)">
                    <span class="btn-title" id="aviator-btn-title-1">BET #1</span>
                    <span class="btn-sub" id="aviator-btn-sub-1">10.00 ETB</span>
                </button>
            </div>

            <div class="bet-card">
                <div class="number-picker">
                    <button class="num-btn" onclick="adjustBet(2, -5)">-</button>
                    <input type="number" class="num-input" id="aviator-bet-val-2" value="20.00" onchange="onManualBetChange(2, this.value)">
                    <button class="num-btn" onclick="adjustBet(2, 5)">+</button>
                </div>
                <div class="auto-controls-row">
                    <label style="display: flex; align-items: center; gap: 4px; cursor: pointer;">
                        <input type="checkbox" id="auto-cash-toggle-2" checked onchange="toggleAutoCashInput(2)"> አውቶ
                    </label>
                    <input type="text" class="auto-cash-input" id="auto-cash-val-2" value="2.00">
                </div>
                <button class="btn-start-bet" id="aviator-bet-btn-2" onclick="handleAviatorBtnClick(2)">
                    <span class="btn-title" id="aviator-btn-title-2">BET #2</span>
                    <span class="btn-sub" id="aviator-btn-sub-2">20.00 ETB</span>
                </button>
            </div>
        </div>

        <div class="live-bets-panel">
            <div class="stat-summary-box">
                <span>አጠቃላይ/ካሻውት: <span id="aviator-stat-ratio" style="color:#fff;">0/0</span></span>
                <span>የወጣ ብር: <span id="aviator-stat-totalwin" style="color:var(--accent-green);">0.00 ETB</span></span>
            </div>

            <div class="live-bets-title">
                <span>የአቪዬተር የቀጥታ መደቦች (LIVE BETS)</span>
                <span style="color: var(--accent-green);" id="aviator-live-count">0 Bets</span>
            </div>
            <div id="aviator-live-bets-list">
                <p style="font-size: 11px; color: var(--text-muted);">በዚህ ዙር የተመደበ የለም።</p>
            </div>
        </div>
    </div>

    <!-- ================= KENO SECTION ================= -->
    <div id="keno-section" style="display: none;">
        <div class="game-top-bar">
            <span style="font-size: 12px; font-weight: bold; color: var(--accent-yellow);">ሻሞ (KENO - Max 20 Tickets)</span>
            <button class="menu-btn" onclick="toggleDropdownMenu(event, 'keno-dropdown-menu')">⋮</button>
            <div class="dropdown-menu-box" id="keno-dropdown-menu">
                <div class="dropdown-item" onclick="openModal('keno-limits-modal')">⚙️ የጨዋታ ገደብ (Limits)</div>
                <div class="dropdown-item" onclick="openKenoHistoryModal()">📜 የኬኖ ታሪክ (History)</div>
            </div>
        </div>

        <div class="stat-summary-box">
            <span>በዚህ ዙር የተመደቡ አጠቃላይ የጨዋታዎች ብዛት፦</span>
            <span id="keno-total-round-bets" style="font-size: 13px; color: var(--accent-green);">0</span>
        </div>

        <div class="recent-keno-detailed-box">
            <div class="recent-keno-title">
                <span>ያለፉት 3 የኬኖ ጨዋታዎች ውጤት</span>
            </div>
            <div id="recent-keno-detailed-list">
                <div class="keno-history-row"><span>ጨዋታ #1: ጫን...</span></div>
                <div class="keno-history-row"><span>ጨዋታ #2: ጫን...</span></div>
                <div class="keno-history-row"><span>ጨዋታ #3: ጫን...</span></div>
            </div>
        </div>

        <div class="keno-spinning-box-container">
            <span class="spinning-label">እየተሽከረከረ የሚወጣ እጣ:</span>
            <div class="spinning-slot" id="keno-spinner-slot">--</div>
        </div>

        <div class="keno-board-container">
            <div class="keno-header">
                <span>1 እስከ 80 ቁጥሮችን ይምረጡ (ከ1 እስከ 10)</span>
                <span>ቀጣይ እጣ: <b id="keno-timer-display" style="color: var(--accent-pink);">45s</b></span>
            </div>
            <div class="keno-grid" id="keno-grid-board"></div>
        </div>

        <div class="bet-card" style="margin-bottom: 10px;">
            <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 8px;">
                <button style="flex: 1; padding: 10px; background: #29b6f6; color: #000; font-weight: 900; border:none; border-radius:6px; cursor:pointer;" onclick="selectRandomKenoNumbers()">
                    🎲 RANDOM PICK (በዘፍቀድ)
                </button>
                <button style="padding: 10px 14px; background: #ff1744; color: #fff; font-weight: bold; border:none; border-radius:6px; cursor:pointer;" onclick="clearKenoSelection()">
                    🧹 CLEAR
                </button>
            </div>
            <div style="display: flex; gap: 8px; align-items: center;">
                <div class="number-picker" style="flex: 1; margin-bottom: 0;">
                    <button class="num-btn" onclick="adjustKenoBet(-5)">-</button>
                    <input type="number" class="num-input" id="keno-bet-val" value="10.00" min="5" max="12000" onchange="onManualKenoBetChange(this.value)" style="width: 80px;">
                    <button class="num-btn" onclick="adjustKenoBet(5)">+</button>
                </div>
                <button style="flex: 1; padding: 10px; background: var(--accent-yellow); color: #000; font-weight: bold; border:none; border-radius:6px; cursor:pointer;" onclick="addKenoTicket()">
                    + ADD TICKET
                </button>
            </div>
        </div>

        <div class="live-bets-panel">
            <div class="live-bets-title">
                <span>የኬኖ የተመደቡ ቲኬቶች (<span id="keno-tickets-count">0</span>/20)</span>
                <button class="btn-start-bet" id="keno-place-all-btn" style="width: 100px; padding: 4px 0;" onclick="placeAllKenoBets()">
                    <span class="btn-title">PLACE ALL</span>
                </button>
            </div>
            <div id="keno-tickets-list">
                <p style="font-size: 11px; color: var(--text-muted);">ምንም የተዘጋጀ ቲኬት የለም።</p>
            </div>
        </div>
    </div>

    <!-- ================= BINGO SECTION ================= -->
    <div id="bingo-section" style="display: none;">
        <div class="game-top-bar">
            <span style="font-size: 12px; font-weight: bold; color: var(--accent-green);">75-BALL BINGO (ቢንጎ)</span>
            <button class="menu-btn" onclick="showHomeScreen()">❌</button>
        </div>

        <!-- BINGO MENU VIEW -->
        <div id="bingo-menu-view">
            <h3 style="font-size: 13px; color: var(--accent-yellow); margin-bottom: 8px;">1. የመደብ መጠን ይምረጡ (50 & 100 Added)</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px;">
                <button style="padding: 10px; background: #1a222d; border: 2px solid var(--accent-green); color: #fff; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 11px;" onclick="selectBingoStake(10)">
                    10 ETB Room
                </button>
                <button style="padding: 10px; background: #1a222d; border: 2px solid var(--accent-yellow); color: #fff; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 11px;" onclick="selectBingoStake(30)">
                    30 ETB Room
                </button>
                <button style="padding: 10px; background: #1a222d; border: 2px solid var(--accent-orange); color: #fff; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 11px;" onclick="selectBingoStake(50)">
                    50 ETB Room (New)
                </button>
                <button style="padding: 10px; background: #1a222d; border: 2px solid var(--accent-pink); color: #fff; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 11px;" onclick="selectBingoStake(100)">
                    100 ETB Room (New)
                </button>
            </div>

            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <h3 style="font-size: 13px; color: var(--accent-yellow);">2. ካርድ ይምረጡ (የተመረጡ: <span id="bingo-selected-count">0</span>)</h3>
                <div style="display: flex; gap: 6px;">
                    <button style="padding: 4px 8px; background: #0288d1; color: #fff; border: none; border-radius: 4px; font-weight: bold; font-size: 11px; cursor: pointer;" onclick="pickRandomBingoCard()">🎲 RANDOM</button>
                    <button style="padding: 4px 8px; background: #ff1744; color: #fff; border: none; border-radius: 4px; font-weight: bold; font-size: 11px; cursor: pointer;" onclick="clearAllBingoCards()">🧹 CLEAR</button>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; max-height: 180px; overflow-y: auto; background: #0c1015; padding: 8px; border-radius: 8px; border: 1px solid var(--border-color); margin-bottom: 12px;" id="bingo-card-selector">
            </div>

            <button class="btn-start-bet" style="padding: 12px;" onclick="joinBingoGame()">JOIN BINGO GAME ▶</button>
        </div>

        <!-- BINGO GAMEPLAY VIEW -->
        <div id="bingo-game-view" style="display: none;">
            <div style="display: flex; justify-content: space-between; align-items: center; background: #0c1015; padding: 8px; border-radius: 6px; margin-bottom: 8px; font-size: 11px;">
                <span>ካርዶች: <b id="bingo-player-count" style="color: var(--accent-green);">0</b></span>
                <span>ሁኔታ: <b id="bingo-room-status" style="color: var(--accent-yellow);">በቂ ተጫዋች በመጠባበቅ ላይ...</b></span>
                <span>ቆጠራ: <b id="bingo-room-timer" style="color: var(--accent-pink);">--</b></span>
            </div>

            <div style="text-align: center; margin-bottom: 8px; background: #1a222d; padding: 6px; border-radius: 6px;">
                <span style="font-size: 11px; color: var(--text-muted);">የወጣ ቁጥር / ፖት (POT):</span>
                <div id="bingo-current-call" style="font-size: 24px; font-weight: 900; color: var(--accent-yellow);">--</div>
                <div style="font-size: 11px; color: var(--accent-green);" id="bingo-pot-display">POT: 0 ETB</div>
            </div>

            <div id="bingo-cards-wrapper" style="max-height: 300px; overflow-y: auto;"></div>

            <div style="display: flex; gap: 8px; margin-top: 8px;">
                <button class="btn-start-bet" style="padding: 10px; background: var(--accent-yellow); color: #000;" onclick="switchGame('bingo'); resetBingoToMenu();">
                    ➕ JOIN (ተጨማሪ ግባ)
                </button>
                <button class="btn-start-bet" id="btn-cancel-bingo" style="padding: 10px; background: #ff1744; color: #fff;" onclick="cancelBingoSelection()">
                    ✖ CANCEL (ሰርዝ)
                </button>
            </div>
        </div>
    </div>

    <!-- ================= HISTORY SECTION ================= -->
    <div id="history-section" class="bet-card" style="display: none;">
        <h3 style="margin-bottom: 10px; color: var(--accent-orange); font-size: 14px;">የእርስዎ የጨዋታ ሂስትሪ (BET HISTORY)</h3>
        <table class="history-table">
            <thead>
                <tr>
                    <th>ጨዋታ</th>
                    <th>መደብ</th>
                    <th>ውጤት</th>
                    <th>ያሸነፉት</th>
                </tr>
            </thead>
            <tbody id="user-history-tbody">
                <tr><td colspan="4" style="text-align: center; color: var(--text-muted);">ምንም ሂስትሪ የለም</td></tr>
            </tbody>
        </table>
    </div>

    <!-- ================= MODALS ================= -->
    <div class="modal-overlay" id="bingo-winner-modal">
        <div class="modal-box">
            <h2 style="color: var(--accent-yellow); margin-bottom: 10px; font-size: 24px;">🎉 BINGO WINNER! 🎉</h2>
            <div id="bingo-winner-details" style="font-size: 14px; margin-bottom: 15px; color: #fff;"></div>
            <button style="width: 100%; padding: 10px; background: var(--accent-green); color: #000; border: none; border-radius: 6px; font-weight: 900; cursor: pointer;" onclick="closeModal('bingo-winner-modal')">OK / ቀጥል</button>
        </div>
    </div>

    <div class="modal-overlay" id="keno-limits-modal">
        <div class="modal-box">
            <h3 style="color: var(--accent-yellow); margin-bottom: 12px;">⚙️ የኬኖ (Keno) መደብ ገደብ</h3>
            <div style="background: #0c1015; padding: 12px; border-radius: 6px; border: 1px solid var(--border-color); font-size: 13px; line-height: 1.8; margin-bottom: 12px;">
                <div>• <b>አነስተኛ መደብ:</b> <span style="color: var(--accent-green);">5.00 ETB</span></div>
                <div>• <b>ከፍተኛ መደብ:</b> <span style="color: var(--accent-pink);">12,000.00 ETB</span></div>
                <div>• <b>የቲኬት ገደብ:</b> <span style="color: var(--accent-yellow);">ከ20 በላይ ቲኬት መቁረጥ አይቻልም</span></div>
            </div>
            <button style="width: 100%; padding: 8px; background: #26323f; color: #fff; border: none; border-radius: 4px; cursor: pointer;" onclick="closeModal('keno-limits-modal')">ዝጋ</button>
        </div>
    </div>

    <div class="modal-overlay" id="keno-history-modal">
        <div class="modal-box" style="max-width: 420px;">
            <h3 style="color: var(--accent-yellow); margin-bottom: 12px;">📜 የኬኖ ታሪክ (Keno History)</h3>
            <div style="max-height: 250px; overflow-y: auto; margin-bottom: 12px;">
                <table class="history-table">
                    <thead>
                        <tr>
                            <th>መደብ</th>
                            <th>የወጡት/ቁጥሮች</th>
                            <th>ያሸነፉት</th>
                        </tr>
                    </thead>
                    <tbody id="keno-only-history-tbody">
                        <tr><td colspan="3" style="text-align: center; color: var(--text-muted);">ምንም የኬኖ ታሪክ የለም</td></tr>
                    </tbody>
                </table>
            </div>
            <button style="width: 100%; padding: 8px; background: #26323f; color: #fff; border: none; border-radius: 4px; cursor: pointer;" onclick="closeModal('keno-history-modal')">ዝጋ</button>
        </div>
    </div>

    <div class="modal-overlay" id="aviator-limits-modal">
        <div class="modal-box">
            <h3 style="color: var(--accent-yellow); margin-bottom: 12px;">⚙️ የአቪዬተር መደብ ገደብ</h3>
            <div style="background: #0c1015; padding: 12px; border-radius: 6px; border: 1px solid var(--border-color); font-size: 13px; line-height: 1.8; margin-bottom: 12px;">
                <div>• <b>አነስተኛ መደብ:</b> <span style="color: var(--accent-green);">5.00 ETB</span></div>
                <div>• <b>ከፍተኛ መደብ:</b> <span style="color: var(--accent-pink);">12,000.00 ETB</span></div>
            </div>
            <button style="width: 100%; padding: 8px; background: #26323f; color: #fff; border: none; border-radius: 4px; cursor: pointer;" onclick="closeModal('aviator-limits-modal')">ዝጋ</button>
        </div>
    </div>

    <div class="modal-overlay" id="aviator-history-modal">
        <div class="modal-box" style="max-width: 420px;">
            <h3 style="color: var(--accent-orange); margin-bottom: 12px;">📜 የአቪዬተር ብቻ ሂስትሪ</h3>
            <div style="max-height: 250px; overflow-y: auto; margin-bottom: 12px;">
                <table class="history-table">
                    <thead>
                        <tr>
                            <th>መደብ</th>
                            <th>ኤክስ (Multiplier)</th>
                            <th>ያሸነፉት</th>
                        </tr>
                    </thead>
                    <tbody id="aviator-only-history-tbody">
                        <tr><td colspan="3" style="text-align: center; color: var(--text-muted);">ምንም ሂስትሪ የለም</td></tr>
                    </tbody>
                </table>
            </div>
            <button style="width: 100%; padding: 8px; background: #26323f; color: #fff; border: none; border-radius: 4px; cursor: pointer;" onclick="closeModal('aviator-history-modal')">ዝጋ</button>
        </div>
    </div>

    <div class="modal-overlay" id="deposit-modal">
        <div class="modal-box">
            <h3 style="color: var(--accent-green); margin-bottom: 10px;">ብር ማስገቢያ (Deposit)</h3>
            <div style="background: #0c1015; border: 1px solid var(--accent-green); border-radius: 6px; padding: 10px; margin-bottom: 12px; font-size: 12px; line-height: 1.6;">
                <div style="color: var(--accent-yellow); font-weight: bold; margin-bottom: 4px;">📱 በቴሌብር (Telebirr) ገቢ ማድረጊያ:</div>
                <div><b>ስልክ ቁጥር:</b> <span style="color: var(--accent-green); font-weight: bold;">0997384093</span></div>
                <div><b>ስም:</b> <span style="color: #fff; font-weight: bold;">አብድል ዋሂድ</span></div>
            </div>
            <input type="number" id="dep-amount-input" class="form-control" placeholder="የላኩት ብር መጠን (ETB)">
            <button class="btn-start-bet" style="width: 100%; height: 40px; margin-bottom: 6px;" onclick="submitDepositForm()">SUBMIT DEPOSIT</button>
            <button style="width: 100%; padding: 8px; background: #26323f; color: #fff; border: none; border-radius: 4px; cursor: pointer;" onclick="closeModal('deposit-modal')">ዝጋ</button>
        </div>
    </div>

    <div class="modal-overlay" id="withdraw-modal">
        <div class="modal-box">
            <h3 style="color: var(--accent-orange); margin-bottom: 10px;">ብር ማውጫ (Withdraw)</h3>
            <select id="with-method" class="form-control">
                <option value="Telebirr">Telebirr</option>
                <option value="CBE Birr">CBE Birr</option>
            </select>
            <input type="text" id="with-account" class="form-control" placeholder="የመቀበያ ስልክ / አካውንት">
            <input type="number" id="with-amount" class="form-control" placeholder="የምታወጡት ብር መጠን">
            <button class="btn-start-bet" style="width: 100%; height: 40px; margin-bottom: 6px; background: linear-gradient(180deg, #ff9800 0%, #e65100 100%);" onclick="submitWithdrawForm()">WITHDRAW</button>
            <button style="width: 100%; padding: 8px; background: #26323f; color: #fff; border: none; border-radius: 4px; cursor: pointer;" onclick="closeModal('withdraw-modal')">ዝጋ</button>
        </div>
    </div>
    {% endif %}

    <!-- ================= JAVASCRIPT LOGIC ================= -->
    <script>
        let currentMultiplier = 1.00;
        let isGameRunning = false;
        let drawnKenoNumbers = [];
        let flightPoints = [];
        let isKenoDrawingActive = false;

        const KENO_ODDS = {
            1: {1: 3.5}, 2: {1: 1.0, 2: 10.0}, 3: {0: 0.0, 1: 0.0, 2: 2.0, 3: 50.0},
            4: {2: 1.5, 3: 10.0, 4: 80.0}, 5: {2: 1.0, 3: 3.0, 4: 30.0, 5: 150.0},
            6: {3: 2.0, 4: 15.0, 5: 60.0, 6: 500.0}, 7: {0: 1.0, 3: 2.0, 4: 4.0, 5: 20.0, 6: 80.0, 7: 1000.0},
            8: {0: 1.0, 4: 5.0, 5: 15.0, 6: 50.0, 7: 200.0, 8: 2000.0}, 9: {0: 2.0, 4: 2.0, 5: 10.0, 6: 25.0, 7: 125.0, 8: 1000.0, 9: 5000.0},
            10: {0: 2.0, 5: 5.0, 6: 30.0, 7: 100.0, 8: 300.0, 9: 2000.0, 10: 10000.0}
        };

        function showHomeScreen() {
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            document.getElementById('btn-nav-home').classList.add('active');

            document.getElementById('home-dashboard-view').style.display = 'block';
            document.getElementById('aviator-section').style.display = 'none';
            document.getElementById('keno-section').style.display = 'none';
            document.getElementById('bingo-section').style.display = 'none';
            document.getElementById('history-section').style.display = 'none';
        }

        function switchGame(game) {
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            document.getElementById('home-dashboard-view').style.display = 'none';
            document.getElementById('aviator-section').style.display = 'none';
            document.getElementById('keno-section').style.display = 'none';
            document.getElementById('bingo-section').style.display = 'none';
            document.getElementById('history-section').style.display = 'none';

            document.getElementById('btn-nav-' + game).classList.add('active');
            document.getElementById(game + '-section').style.display = 'block';

            if(game === 'history') fetchUserHistory();
            if(game === 'bingo') resetBingoToMenu();
            if(game === 'aviator') resizeCanvas();
        }

        function togglePasswordVisibility() {
            let pwd = document.getElementById('auth-password');
            pwd.type = (pwd.type === 'password') ? 'text' : 'password';
        }

        function toggleDropdownMenu(e, menuId) {
            e.stopPropagation();
            let menu = document.getElementById(menuId);
            let isVisible = menu.style.display === 'block';
            document.querySelectorAll('.dropdown-menu-box').forEach(m => m.style.display = 'none');
            menu.style.display = isVisible ? 'none' : 'block';
        }

        document.addEventListener('click', function() {
            document.querySelectorAll('.dropdown-menu-box').forEach(m => m.style.display = 'none');
        });

        function openAviatorLimitsModal() { document.getElementById('aviator-limits-modal').style.display = 'flex'; }
        
        function openKenoHistoryModal() {
            fetch('/user_history').then(r=>r.json()).then(d=>{
                let tbody = document.getElementById('keno-only-history-tbody');
                let kenoHist = d.history ? d.history.filter(h => h.game.includes('Keno') || h.game.includes('ሻሞ')) : [];
                
                if(kenoHist.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="3" style="text-align: center; color: var(--text-muted);">ምንም የኬኖ ታሪክ የለም</td></tr>`;
                } else {
                    let html = "";
                    kenoHist.forEach(h => {
                        let isWin = h.win_amount > 0;
                        html += `<tr>
                            <td><b>${h.bet_amount} ETB</b></td>
                            <td>${h.result_info}</td>
                            <td class="${isWin ? 'badge-win' : 'badge-loss'}">${isWin ? '+' + h.win_amount + ' ETB' : '0.00 ETB'}</td>
                        </tr>`;
                    });
                    tbody.innerHTML = html;
                }
                document.getElementById('keno-history-modal').style.display = 'flex';
            });
        }

        function openAviatorHistoryModal() {
            fetch('/user_history').then(r=>r.json()).then(d=>{
                let tbody = document.getElementById('aviator-only-history-tbody');
                let aviatorHist = d.history ? d.history.filter(h => h.game === 'Aviator') : [];
                
                if(aviatorHist.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="3" style="text-align: center; color: var(--text-muted);">ምንም የአቪዬተር ሂስትሪ የለም</td></tr>`;
                } else {
                    let html = "";
                    aviatorHist.forEach(h => {
                        let isWin = h.win_amount > 0;
                        html += `<tr>
                            <td><b>${h.bet_amount} ETB</b></td>
                            <td>${h.result_info}</td>
                            <td class="${isWin ? 'badge-win' : 'badge-loss'}">${isWin ? '+' + h.win_amount + ' ETB' : '0.00 ETB'}</td>
                        </tr>`;
                    });
                    tbody.innerHTML = html;
                }
                document.getElementById('aviator-history-modal').style.display = 'flex';
            });
        }

        /* ================= BINGO SYSTEM LOGIC (3. CONTINUOUS TIMER FIX) ================= */
        let selectedBingoStake = 10;
        let selectedBingoCardIds = [];
        let currentBingoCardsData = [];
        let bingoTimerInterval = null;
        let bingoCallInterval = null;
        let bingoCallsList = [];
        let bingoStatusPollInterval = null;
        let bingoCurrentTimeLeft = 30;
        let bingoHasWonCurrentGame = false;

        const cardSelectorContainer = document.getElementById('bingo-card-selector');
        if(cardSelectorContainer) {
            let html = "";
            for(let i = 1; i <= 100; i++) {
                html += `<div id="b-card-btn-${i}" onclick="toggleBingoCardNum(${i})" style="background: #1a222d; color: #fff; text-align: center; padding: 8px 0; border-radius: 4px; font-weight: bold; cursor: pointer; border: 1px solid var(--border-color); font-size: 11px;">#${i}</div>`;
            }
            cardSelectorContainer.innerHTML = html;
        }

        function selectBingoStake(amount) {
            selectedBingoStake = amount;
            alert(amount + " ETB Room ተመርጧል!");
        }

        function toggleBingoCardNum(cardId) {
            if(selectedBingoCardIds.includes(cardId)) {
                selectedBingoCardIds = selectedBingoCardIds.filter(id => id !== cardId);
            } else {
                selectedBingoCardIds.push(cardId);
            }
            updateBingoCardSelectionUI();
        }

        function pickRandomBingoCard() {
            let r = Math.floor(Math.random() * 100) + 1;
            if(!selectedBingoCardIds.includes(r)) {
                selectedBingoCardIds.push(r);
            }
            updateBingoCardSelectionUI();
        }

        function clearAllBingoCards() {
            selectedBingoCardIds = [];
            updateBingoCardSelectionUI();
        }

        function updateBingoCardSelectionUI() {
            document.getElementById('bingo-selected-count').innerText = selectedBingoCardIds.length;
            for(let i = 1; i <= 100; i++) {
                let el = document.getElementById('b-card-btn-' + i);
                if(el) {
                    if(selectedBingoCardIds.includes(i)) {
                        el.style.background = 'var(--accent-yellow)';
                        el.style.color = '#000';
                    } else {
                        el.style.background = '#1a222d';
                        el.style.color = '#fff';
                    }
                }
            }
        }

        function resetBingoToMenu() {
            clearInterval(bingoTimerInterval);
            clearInterval(bingoCallInterval);
            clearInterval(bingoStatusPollInterval);
            bingoTimerInterval = null;
            bingoHasWonCurrentGame = false;
            document.getElementById('bingo-menu-view').style.display = 'block';
            document.getElementById('bingo-game-view').style.display = 'none';
            document.getElementById('btn-cancel-bingo').style.display = 'block';
        }

        function joinBingoGame() {
            if(selectedBingoCardIds.length === 0) {
                alert("እባክዎን ቢያንስ አንድ ካርድ ይምረጡ!");
                return;
            }

            let fd = new FormData();
            fd.append('stake', selectedBingoStake);
            fd.append('card_ids', JSON.stringify(selectedBingoCardIds));

            fetch('/join_bingo', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{
                if(!d.success) { alert(d.message); return; }
                
                document.getElementById('user-balance').innerText = d.new_balance.toFixed(2);
                currentBingoCardsData = d.cards;
                renderAllBingoCards(d.cards);

                document.getElementById('bingo-menu-view').style.display = 'none';
                document.getElementById('bingo-game-view').style.display = 'block';
                
                startBingoLobbyPolling();
            });
        }

        function cancelBingoSelection() {
            if(bingoCurrentTimeLeft <= 15) {
                alert("ጨዋታው ለመጀመር 15 ሰከንድ ወይም ከዚያ በታች ስለቀረው ካንሰል ማድረግ አይቻልም!");
                return;
            }

            let fd = new FormData();
            fd.append('stake', selectedBingoStake);
            fd.append('card_count', currentBingoCardsData ? currentBingoCardsData.length : selectedBingoCardIds.length);

            fetch('/cancel_bingo', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{
                if(d.success) {
                    alert(d.message);
                    document.getElementById('user-balance').innerText = d.new_balance.toFixed(2);
                    resetBingoToMenu();
                } else {
                    alert(d.message);
                }
            });
        }

        function startBingoLobbyPolling() {
            if (bingoStatusPollInterval) clearInterval(bingoStatusPollInterval);
            bingoStatusPollInterval = setInterval(() => {
                fetch(`/bingo_room_status?stake=${selectedBingoStake}`).then(r=>r.json()).then(data => {
                    document.getElementById('bingo-player-count').innerText = data.player_count;
                    document.getElementById('bingo-pot-display').innerText = "POT: " + data.pot.toFixed(2) + " ETB";

                    // Continuously ensure timer engine stays active without resetting prematurely
                    if(data.player_count < 2) {
                        document.getElementById('bingo-room-status').innerText = "ቢያንስ 2 ተጫዋች ያስፈልጋል...";
                        document.getElementById('bingo-room-timer').innerText = "መጠባበቅ";
                    } else {
                        document.getElementById('bingo-room-status').innerText = "ተጫዋች ተሟልቷል! ቆጠራ ላይ...";
                        if(!bingoTimerInterval && data.status === "WAITING") {
                            startBingoTimerEngine();
                        }
                    }
                });
            }, 1000);
        }

        function renderAllBingoCards(cards) {
            let wrapper = document.getElementById('bingo-cards-wrapper');
            wrapper.innerHTML = "";

            cards.forEach((cardObj) => {
                let cardEl = document.createElement('div');
                cardEl.className = 'bingo-card-container';
                cardEl.id = `bingo-card-container-${cardObj.id}`;

                let headers = ['B', 'I', 'N', 'G', 'O'];
                let html = `<div style="font-size:11px; font-weight:bold; color:var(--accent-yellow); margin-bottom:4px;">ካርድ #${cardObj.id}</div><div class="bingo-card-grid">`;

                headers.forEach(h => html += `<div class="bingo-header-cell">${h}</div>`);

                for(let r = 0; r < 5; r++) {
                    headers.forEach(h => {
                        let val = cardObj.card[h][r];
                        if(val === "FREE") {
                            html += `<div class="bingo-cell free marked" id="b-cell-${cardObj.id}-${h}-${r}" data-val="FREE">FREE</div>`;
                        } else {
                            html += `<div class="bingo-cell" id="b-cell-${cardObj.id}-${h}-${r}" data-val="${val}">${val}</div>`;
                        }
                    });
                }
                html += `</div>`;
                cardEl.innerHTML = html;
                wrapper.appendChild(cardEl);
            });
        }

        function autoMarkBingoNumber(num) {
            currentBingoCardsData.forEach((cardObj) => {
                let headers = ['B', 'I', 'N', 'G', 'O'];
                headers.forEach(h => {
                    for(let r = 0; r < 5; r++) {
                        let val = cardObj.card[h][r];
                        if(parseInt(val) === num) {
                            let cell = document.getElementById(`b-cell-${cardObj.id}-${h}-${r}`);
                            if(cell) {
                                cell.classList.add('marked');
                            }
                        }
                    }
                });
                checkBingoWinPattern(cardObj.id);
            });
        }

        function startBingoTimerEngine() {
            if(bingoTimerInterval) return; // Prevent duplicate interval loops
            bingoCurrentTimeLeft = 30;
            let timerEl = document.getElementById('bingo-room-timer');

            bingoTimerInterval = setInterval(() => {
                bingoCurrentTimeLeft--;
                timerEl.innerText = bingoCurrentTimeLeft + "s";

                if(bingoCurrentTimeLeft <= 15) {
                    let cancelBtn = document.getElementById('btn-cancel-bingo');
                    if(cancelBtn) cancelBtn.style.display = 'none';
                }

                if(bingoCurrentTimeLeft <= 0) {
                    clearInterval(bingoTimerInterval);
                    bingoTimerInterval = null;
                    if(bingoStatusPollInterval) clearInterval(bingoStatusPollInterval);
                    timerEl.innerText = "ተጀምሯል!";
                    document.getElementById('bingo-room-status').innerText = "ጨዋታው እየተካሄደ ነው!";
                    start75BingoCalls();
                }
            }, 1000);
        }

        function start75BingoCalls() {
            bingoCallsList = [];
            let pool = Array.from({length: 75}, (_, i) => i + 1);
            pool.sort(() => Math.random() - 0.5);

            let idx = 0;
            bingoCallInterval = setInterval(() => {
                if(idx < pool.length && !bingoHasWonCurrentGame) {
                    let num = pool[idx];
                    bingoCallsList.push(num);
                    
                    let letter = num <= 15 ? 'B' : (num <= 30 ? 'I' : (num <= 45 ? 'N' : (num <= 60 ? 'G' : 'O')));
                    document.getElementById('bingo-current-call').innerText = letter + "-" + num;
                    
                    autoMarkBingoNumber(num);
                    idx++;
                } else if (!bingoHasWonCurrentGame) {
                    clearInterval(bingoCallInterval);
                    alert("75ቱ ቁጥሮች ወጥተው አልቀዋል!");
                    resetBingoToMenu();
                }
            }, 2000);
        }

        function checkBingoWinPattern(cardId) {
            if (bingoHasWonCurrentGame) return;

            let headers = ['B', 'I', 'N', 'G', 'O'];
            let isWon = false;

            for(let r = 0; r < 5; r++) {
                let rowWin = true;
                headers.forEach(h => {
                    let cell = document.getElementById(`b-cell-${cardId}-${h}-${r}`);
                    if(!cell || !cell.classList.contains('marked')) rowWin = false;
                });
                if(rowWin) isWon = true;
            }

            headers.forEach(h => {
                let colWin = true;
                for(let r = 0; r < 5; r++) {
                    let cell = document.getElementById(`b-cell-${cardId}-${h}-${r}`);
                    if(!cell || !cell.classList.contains('marked')) colWin = false;
                }
                if(colWin) isWon = true;
            });

            let diag1Win = true;
            let diag2Win = true;
            for(let i = 0; i < 5; i++) {
                let cell1 = document.getElementById(`b-cell-${cardId}-${headers[i]}-${i}`);
                let cell2 = document.getElementById(`b-cell-${cardId}-${headers[4-i]}-${i}`);
                if(!cell1 || !cell1.classList.contains('marked')) diag1Win = false;
                if(!cell2 || !cell2.classList.contains('marked')) diag2Win = false;
            }
            if(diag1Win || diag2Win) isWon = true;

            if(isWon) {
                bingoHasWonCurrentGame = true;
                clearInterval(bingoCallInterval);
                
                let winContainer = document.getElementById(`bingo-card-container-${cardId}`);
                if(winContainer) winContainer.classList.add('winning-card');

                triggerBingoWinClaim(cardId);
            }
        }

        function triggerBingoWinClaim(winningCardId) {
            let fd = new FormData();
            fd.append('stake', selectedBingoStake);
            fd.append('card_id', winningCardId);

            fetch('/claim_bingo', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{
                if(d.success) {
                    document.getElementById('user-balance').innerText = d.new_balance.toFixed(2);
                    
                    let winDetails = document.getElementById('bingo-winner-details');
                    winDetails.innerHTML = `
                        <div>ያሸነፉበት ካርድ፡ <b>Card #${winningCardId}</b></div>
                        <div style="font-size: 20px; color: var(--accent-green); font-weight: 900; margin-top: 8px;">የሽልማት መጠን፡ ${d.win_amount.toFixed(2)} ETB</div>
                    `;
                    document.getElementById('bingo-winner-modal').style.display = 'flex';
                }
            });
        }

        /* ================= AVIATOR ENGINE ================= */
        let aviatorBets = {
            1: { amount: 10.00, status: 'NONE', winAmt: 0 },
            2: { amount: 20.00, status: 'NONE', winAmt: 0 }
        };

        let aviatorStats = { total: 0, cashedOut: 0, totalWinAmt: 0.0 };
        let canvas, ctx;

        function resizeCanvas() {
            let screenBox = document.getElementById('aviator-screen-box');
            canvas = document.getElementById('aviator-canvas');
            if(canvas && screenBox) {
                canvas.width = screenBox.clientWidth;
                canvas.height = screenBox.clientHeight;
                ctx = canvas.getContext('2d');
            }
        }

        function drawAviatorTrajectory() {
            if(!ctx || !canvas) return;
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            if(flightPoints.length > 1) {
                ctx.beginPath();
                ctx.moveTo(flightPoints[0].x, flightPoints[0].y);
                for(let i = 1; i < flightPoints.length; i++) {
                    ctx.lineTo(flightPoints[i].x, flightPoints[i].y);
                }
                ctx.strokeStyle = "rgba(255, 23, 68, 0.9)";
                ctx.lineWidth = 3;
                ctx.setLineDash([6, 4]);
                ctx.stroke();
                ctx.setLineDash([]);
            }
        }

        function toggleAutoCashInput(id) {
            let isChecked = document.getElementById(`auto-cash-toggle-${id}`).checked;
            document.getElementById(`auto-cash-val-${id}`).style.display = isChecked ? 'inline-block' : 'none';
        }

        function adjustBet(id, val) {
            if(aviatorBets[id].status !== 'NONE' && aviatorBets[id].status !== 'WAITING') return;
            let newAmt = Math.min(12000, Math.max(5, aviatorBets[id].amount + val));
            aviatorBets[id].amount = newAmt;
            document.getElementById(`aviator-bet-val-${id}`).value = aviatorBets[id].amount.toFixed(2);
            document.getElementById(`aviator-btn-sub-${id}`).innerText = aviatorBets[id].amount.toFixed(2) + " ETB";
        }

        function onManualBetChange(id, val) {
            if(aviatorBets[id].status !== 'NONE' && aviatorBets[id].status !== 'WAITING') return;
            let num = parseFloat(val);
            if(isNaN(num) || num < 5) num = 5.00;
            if(num > 12000) num = 12000.00;
            aviatorBets[id].amount = num;
            document.getElementById(`aviator-bet-val-${id}`).value = num.toFixed(2);
            document.getElementById(`aviator-btn-sub-${id}`).innerText = num.toFixed(2) + " ETB";
        }

        function handleAviatorBtnClick(id) {
            let state = aviatorBets[id].status;

            if(state === 'NONE') {
                if(isGameRunning) {
                    let fd = new FormData();
                    fd.append('amount', aviatorBets[id].amount);

                    fetch('/place_bet', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{
                        if(!d.success) { alert(d.message); return; }
                        document.getElementById('user-balance').innerText = d.new_balance.toFixed(2);
                        
                        aviatorBets[id].status = 'WAITING';
                        let btn = document.getElementById(`aviator-bet-btn-${id}`);
                        btn.className = 'btn-start-bet cancel';
                        document.getElementById(`aviator-btn-title-${id}`).innerText = "CANCEL";
                        document.getElementById(`aviator-btn-sub-${id}`).innerText = "ይሰረዝ (" + aviatorBets[id].amount.toFixed(2) + " ETB)";
                        renderAviatorLiveBets();
                    });
                    return;
                }

                let fd = new FormData();
                fd.append('amount', aviatorBets[id].amount);

                fetch('/place_bet', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{
                    if(!d.success) { alert(d.message); return; }
                    document.getElementById('user-balance').innerText = d.new_balance.toFixed(2);
                    
                    aviatorBets[id].status = 'BET';
                    let btn = document.getElementById(`aviator-bet-btn-${id}`);
                    btn.className = 'btn-start-bet cancel';
                    document.getElementById(`aviator-btn-title-${id}`).innerText = "CANCEL";
                    document.getElementById(`aviator-btn-sub-${id}`).innerText = "ሰርዝ (" + aviatorBets[id].amount.toFixed(2) + " ETB)";
                    renderAviatorLiveBets();
                });
            } 
            else if(state === 'BET' || state === 'WAITING') {
                let fd = new FormData();
                fd.append('amount', aviatorBets[id].amount);

                fetch('/cancel_bet', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{
                    if(d.success) {
                        document.getElementById('user-balance').innerText = d.new_balance.toFixed(2);
                        aviatorBets[id].status = 'NONE';
                        
                        let btn = document.getElementById(`aviator-bet-btn-${id}`);
                        btn.className = 'btn-start-bet';
                        document.getElementById(`aviator-btn-title-${id}`).innerText = `BET #${id}`;
                        document.getElementById(`aviator-btn-sub-${id}`).innerText = aviatorBets[id].amount.toFixed(2) + " ETB";
                        renderAviatorLiveBets();
                    }
                });
            }
            else if(state === 'RUNNING') {
                executeCashout(id);
            }
        }

        function executeCashout(id) {
            let b = aviatorBets[id];
            if(b.status !== 'RUNNING') return;

            let cashoutVal = (b.amount * currentMultiplier).toFixed(2);
            let fd = new FormData();
            fd.append('game', 'Aviator');
            fd.append('bet_amount', b.amount);
            fd.append('win_amount', cashoutVal);
            fd.append('result_info', currentMultiplier.toFixed(2) + "x");

            fetch('/cashout', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{
                if(d.success) {
                    document.getElementById('user-balance').innerText = d.new_balance.toFixed(2);
                    b.status = 'WON';
                    b.winAmt = cashoutVal;

                    aviatorStats.cashedOut += 1;
                    aviatorStats.totalWinAmt += parseFloat(cashoutVal);

                    let btn = document.getElementById(`aviator-bet-btn-${id}`);
                    btn.className = 'btn-start-bet won';
                    btn.disabled = false;
                    document.getElementById(`aviator-btn-title-${id}`).innerText = "CASHED OUT";
                    document.getElementById(`aviator-btn-sub-${id}`).innerText = cashoutVal + " ETB";
                    renderAviatorLiveBets();
                }
            });
        }

        function renderAviatorLiveBets() {
            let list = document.getElementById('aviator-live-bets-list');
            let countSpan = document.getElementById('aviator-live-count');
            if(!list) return;

            let activeBets = Object.keys(aviatorBets).filter(k => aviatorBets[k].status !== 'NONE');
            countSpan.innerText = activeBets.length + " Bets";

            document.getElementById('aviator-stat-ratio').innerText = `${aviatorStats.total}/${aviatorStats.cashedOut}`;
            document.getElementById('aviator-stat-totalwin').innerText = aviatorStats.totalWinAmt.toFixed(2) + " ETB";

            if(activeBets.length === 0) {
                list.innerHTML = `<p style="font-size: 11px; color: var(--text-muted);">በዚህ ዙር የተመደበ የለም።</p>`;
                return;
            }

            let html = "";
            activeBets.forEach(k => {
                let b = aviatorBets[k];
                if(b.status === 'RUNNING') {
                    let totalVal = (b.amount * currentMultiplier).toFixed(2);
                    let btn = document.getElementById(`aviator-bet-btn-${k}`);
                    btn.className = 'btn-start-bet flying';
                    document.getElementById(`aviator-btn-title-${k}`).innerText = "CASH OUT";
                    document.getElementById(`aviator-btn-sub-${k}`).innerText = `${totalVal} ETB (${currentMultiplier.toFixed(2)}x)`;
                }

                let statusText = "";
                if(b.status === 'WON') statusText = `<span style="color: var(--accent-green); font-weight: 900;">+${b.winAmt} ETB</span>`;
                else if(b.status === 'BET') statusText = `<span style="color: var(--accent-yellow);">ሳይጀምር የተያዘ</span>`;
                else if(b.status === 'WAITING') statusText = `<span style="color: var(--accent-orange);">ቀጣይ ዙር የሚጠብቅ</span>`;
                else if(b.status === 'RUNNING') statusText = `<span style="color: var(--accent-green); font-weight:bold;">${(b.amount * currentMultiplier).toFixed(2)} ETB 🚀</span>`;

                html += `<div class="live-bet-row"><span>መደብ #${k}: <b>${b.amount.toFixed(2)} ETB</b></span>${statusText}</div>`;
            });
            list.innerHTML = html;
        }

        function updateAviatorHistoryBar() {
            fetch('/aviator_history_data').then(r => r.json()).then(d => {
                let bar = document.getElementById('aviator-history-bar');
                if(!bar) return;
                let html = "";
                d.history.forEach(m => {
                    let colorClass = parseFloat(m) > 2.0 ? 'green' : (parseFloat(m) > 1.5 ? 'blue' : 'pink');
                    html += `<div class="mult-tag ${colorClass}">${m}</div>`;
                });
                bar.innerHTML = html;
            });
        }

        function runAviatorAutoEngine() {
            let multDisplay = document.getElementById('aviator-mult-display');
            let plane = document.getElementById('plane-icon');
            if(!multDisplay) return;

            resizeCanvas();
            flightPoints = [];
            currentMultiplier = 1.00;
            isGameRunning = true;
            multDisplay.style.color = "#fff";
            multDisplay.innerText = "1.00x";
            plane.innerText = "✈️";

            aviatorStats = { total: 0, cashedOut: 0, totalWinAmt: 0.0 };

            let rand = Math.random();
            let crashPoint = rand < 0.75 ? (Math.random() * 0.98 + 1.01).toFixed(2) : (Math.random() * 10.0 + 2.0).toFixed(2);

            setTimeout(() => {
                [1, 2].forEach(id => {
                    if(aviatorBets[id].status === 'BET') {
                        aviatorBets[id].status = 'RUNNING';
                        aviatorStats.total += 1;
                        let btn = document.getElementById(`aviator-bet-btn-${id}`);
                        btn.className = 'btn-start-bet flying';
                        btn.disabled = false;
                    }
                });
                renderAviatorLiveBets();
            }, 300);

            let timer = setInterval(() => {
                currentMultiplier += currentMultiplier > 5 ? 0.08 : 0.025;
                multDisplay.innerText = currentMultiplier.toFixed(2) + "x";
                
                let curX = Math.min((currentMultiplier - 1) * 28, canvas.width - 40);
                let curY = canvas.height - Math.min((currentMultiplier - 1) * 18, canvas.height - 40) - 20;

                flightPoints.push({x: curX + 15, y: curY + 15});
                drawAviatorTrajectory();

                if(plane) {
                    plane.style.transform = `translate(${curX}px, -${canvas.height - curY - 20}px)`;
                }

                [1, 2].forEach(id => {
                    if(aviatorBets[id].status === 'RUNNING') {
                        let isAutoCashEnabled = document.getElementById(`auto-cash-toggle-${id}`).checked;
                        if(isAutoCashEnabled) {
                            let autoCashInput = document.getElementById(`auto-cash-val-${id}`).value;
                            let targetMult = parseFloat(autoCashInput);
                            if(!isNaN(targetMult) && currentMultiplier >= targetMult) {
                                executeCashout(parseInt(id));
                            }
                        }
                    }
                });
                renderAviatorLiveBets();

                if(currentMultiplier >= parseFloat(crashPoint)) {
                    clearInterval(timer);
                    isGameRunning = false;
                    multDisplay.style.color = "var(--accent-pink)";
                    multDisplay.innerText = "FLEW AWAY @ " + crashPoint + "x";

                    plane.innerText = "💥🔥";

                    fetch('/add_aviator_history', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                        body: 'mult=' + crashPoint + 'x'
                    }).then(() => updateAviatorHistoryBar());

                    [1, 2].forEach(id => {
                        if(aviatorBets[id].status === 'RUNNING') {
                            let fd = new FormData();
                            fd.append('game', 'Aviator');
                            fd.append('bet_amount', aviatorBets[id].amount);
                            fd.append('win_amount', 0);
                            fd.append('result_info', crashPoint + "x (Crashed)");
                            fetch('/record_loss', {method: 'POST', body: fd});
                        }
                        
                        if(aviatorBets[id].status === 'WAITING') {
                            aviatorBets[id].status = 'BET';
                            let btn = document.getElementById(`aviator-bet-btn-${id}`);
                            btn.className = 'btn-start-bet cancel';
                            document.getElementById(`aviator-btn-title-${id}`).innerText = "CANCEL";
                            document.getElementById(`aviator-btn-sub-${id}`).innerText = "ሰርዝ (" + aviatorBets[id].amount.toFixed(2) + " ETB)";
                        } else {
                            aviatorBets[id].status = 'NONE';
                            let btn = document.getElementById(`aviator-bet-btn-${id}`);
                            btn.className = 'btn-start-bet';
                            btn.disabled = false;
                            document.getElementById(`aviator-btn-title-${id}`).innerText = `BET #${id}`;
                            document.getElementById(`aviator-btn-sub-${id}`).innerText = aviatorBets[id].amount.toFixed(2) + " ETB";
                        }
                    });

                    let countdown = 5;
                    let cdTimer = setInterval(() => {
                        multDisplay.innerText = "NEXT IN " + countdown + "s";
                        countdown--;
                        if(countdown < 0) {
                            clearInterval(cdTimer);
                            if(plane) plane.style.transform = `translate(0px, 0px)`;
                            runAviatorAutoEngine();
                        }
                    }, 1000);
                }
            }, 80);
        }

        /* ================= KENO ENGINE ================= */
        let selectedKenoList = [];
        let kenoTickets = [];
        let kenoBetAmount = 10.00;
        let kenoTotalRoundBetsCount = 0;
        const gridBoard = document.getElementById('keno-grid-board');

        if(gridBoard) {
            for(let i = 1; i <= 80; i++) {
                let cell = document.createElement('div');
                cell.className = 'keno-num';
                cell.innerText = i;
                cell.id = 'keno-cell-' + i;
                cell.onclick = () => selectKenoNum(i, cell);
                gridBoard.appendChild(cell);
            }
        }

        function selectKenoNum(num, el) {
            if(selectedKenoList.includes(num)) {
                selectedKenoList = selectedKenoList.filter(n => n !== num);
                el.classList.remove('selected');
            } else {
                if(selectedKenoList.length < 10) {
                    selectedKenoList.push(num);
                    el.classList.add('selected');
                } else { alert("ከ10 በላይ ቁጥሮችን መምረጥ አይችሉም!"); }
            }
        }

        function selectRandomKenoNumbers() {
            clearKenoSelection();
            let count = Math.floor(Math.random() * 5) + 4;
            let nums = [];
            while(nums.length < count) {
                let r = Math.floor(Math.random() * 80) + 1;
                if(!nums.includes(r)) nums.push(r);
            }
            nums.forEach(n => {
                let cell = document.getElementById('keno-cell-' + n);
                if(cell) selectKenoNum(n, cell);
            });
        }

        function clearKenoSelection() {
            selectedKenoList = [];
            document.querySelectorAll('.keno-num').forEach(e => e.classList.remove('selected'));
        }

        function adjustKenoBet(val) {
            let newBet = Math.min(12000, Math.max(5, kenoBetAmount + val));
            kenoBetAmount = newBet;
            document.getElementById('keno-bet-val').value = kenoBetAmount.toFixed(2);
        }

        function onManualKenoBetChange(val) {
            let num = parseFloat(val);
            if(isNaN(num) || num < 5) num = 5.00;
            if(num > 12000) num = 12000.00;
            kenoBetAmount = num;
            document.getElementById('keno-bet-val').value = num.toFixed(2);
        }

        function addKenoTicket() {
            if(isKenoDrawingActive) {
                alert("ጨዋታው ስለተጀመረ አሁን ቲኬት መጨመር አይቻልም!");
                return;
            }
            if(kenoTickets.length >= 20) {
                alert("በአንድ ዙር ከ 20 ቲኬት በላይ መቁረጥ አይቻልም!");
                return;
            }
            if(selectedKenoList.length === 0) { alert("ቢያንስ 1 ቁጥር ይምረጡ!"); return; }
            kenoTickets.push({ numbers: [...selectedKenoList], amount: kenoBetAmount, placed: false });
            clearKenoSelection();
            renderKenoTicketsUI();
        }

        function renderKenoTicketsUI() {
            let list = document.getElementById('keno-tickets-list');
            if(!list) return;
            document.getElementById('keno-tickets-count').innerText = kenoTickets.length;
            document.getElementById('keno-total-round-bets').innerText = kenoTotalRoundBetsCount;
            
            if(kenoTickets.length === 0) {
                list.innerHTML = `<p style="font-size: 11px; color: var(--text-muted);">ምንም የተዘጋጀ ቲኬት የለም።</p>`;
                return;
            }

            let html = "";
            kenoTickets.forEach((t, i) => {
                let numBadges = t.numbers.map(n => {
                    let isHit = drawnKenoNumbers.includes(n);
                    return `<span class="t-num-badge ${isHit ? 'hit' : ''}">${n}</span>`;
                }).join('');

                html += `<div class="live-bet-row" style="flex-direction: column; align-items: flex-start; gap: 4px;">
                    <div>ቲኬት #${i+1} (${t.numbers.length} ቁጥሮች) - <b>${t.amount.toFixed(2)} ETB</b> ${t.placed ? '✅ (ቆይቷል)' : ''}</div>
                    <div>${numBadges}</div>
                </div>`;
            });
            list.innerHTML = html;
        }

        function placeAllKenoBets() {
            let unplaced = kenoTickets.filter(t => !t.placed);
            if(unplaced.length === 0) { alert("የተመደበ አዲስ ቲኬት የለም!"); return; }

            let totalAmt = unplaced.reduce((acc, t) => acc + t.amount, 0);
            let fd = new FormData();
            fd.append('amount', totalAmt);

            fetch('/place_bet', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{
                if(!d.success) { alert(d.message); return; }
                document.getElementById('user-balance').innerText = d.new_balance.toFixed(2);
                
                unplaced.forEach(t => t.placed = true);
                kenoTotalRoundBetsCount += unplaced.length;
                renderKenoTicketsUI();
                alert("ቲኬቶች በትክክል ተመድበዋል!");
            });
        }

        function runKenoTimerEngine() {
            let timeLeft = 45;
            let timerDisplay = document.getElementById('keno-timer-display');
            let spinnerSlot = document.getElementById('keno-spinner-slot');
            
            setInterval(() => {
                timeLeft--;
                if(timerDisplay) timerDisplay.innerText = timeLeft + "s";

                if(timeLeft <= 5) {
                    isKenoDrawingActive = true;
                }

                if(timeLeft <= 0) {
                    timeLeft = 45;
                    isKenoDrawingActive = true;
                    drawnKenoNumbers = [];
                    
                    document.querySelectorAll('.keno-num').forEach(el => {
                        el.classList.remove('drawn-regular', 'ticket-matched', 'selected');
                    });
                    selectedKenoList = [];
                    renderKenoTicketsUI();
                    
                    fetch('/draw_keno_numbers').then(r=>r.json()).then(dData => {
                        let drawn = dData.drawn;
                        let index = 0;
                        let drawInterval = setInterval(() => {
                            if(index < drawn.length) {
                                let n = drawn[index];
                                drawnKenoNumbers.push(n);
                                
                                let spinCount = 0;
                                let spinTimer = setInterval(() => {
                                    if(spinnerSlot) spinnerSlot.innerText = Math.floor(Math.random() * 80) + 1;
                                    spinCount++;
                                    if(spinCount > 6) {
                                        clearInterval(spinTimer);
                                        if(spinnerSlot) spinnerSlot.innerText = n;
                                    }
                                }, 60);

                                let cell = document.getElementById('keno-cell-' + n);
                                if(cell) {
                                    cell.classList.add('drawn-regular');
                                    kenoTickets.forEach(t => {
                                        if(t.placed && t.numbers.includes(n)) {
                                            cell.classList.add('ticket-matched');
                                        }
                                    });
                                }
                                renderKenoTicketsUI();
                                index++;
                            } else {
                                clearInterval(drawInterval);
                                if(spinnerSlot) spinnerSlot.innerText = "✓";
                                evaluateKenoResults(drawn);
                                isKenoDrawingActive = false;
                            }
                        }, 650);
                    });
                }
            }, 1000);
        }

        function evaluateKenoResults(drawn) {
            fetch('/update_keno_history', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: 'draws=' + JSON.stringify(drawn)
            }).then(r => r.json()).then(d => {
                let listContainer = document.getElementById('recent-keno-detailed-list');
                if(listContainer && d.recent) {
                    let html = "";
                    d.recent.forEach((item, idx) => {
                        let ballsHtml = item.map(num => {
                            let isMatchedHit = drawnKenoNumbers.includes(num);
                            return `<span class="kh-ball ${isMatchedHit ? 'hit-match' : ''}">${num}</span>`;
                        }).join('');

                        html += `<div class="keno-history-row">
                            <span><b>ጨዋታ #${idx+1}</b> (ወጥተዋል: ${item.length} ቁጥሮች)</span>
                            <div class="keno-history-balls">${ballsHtml}</div>
                        </div>`;
                    });
                    listContainer.innerHTML = html;
                }
            });

            kenoTickets.forEach(t => {
                if(t.placed) {
                    let selectedCount = t.numbers.length;
                    let hits = t.numbers.filter(n => drawn.includes(n)).length;
                    
                    let multiplier = (KENO_ODDS[selectedCount] && KENO_ODDS[selectedCount][hits] !== undefined) 
                                     ? KENO_ODDS[selectedCount][hits] 
                                     : 0.0;

                    let winAmt = t.amount * multiplier;

                    if(winAmt > 0) {
                        let fd = new FormData();
                        fd.append('game', 'Keno (ሻሞ)');
                        fd.append('bet_amount', t.amount);
                        fd.append('win_amount', winAmt.toFixed(2));
                        fd.append('result_info', `${hits}/${selectedCount} Hits (${multiplier}x)`);
                        fetch('/cashout', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{
                            if(d.success) document.getElementById('user-balance').innerText = d.new_balance.toFixed(2);
                        });
                    } else {
                        let fd = new FormData();
                        fd.append('game', 'Keno (ሻሞ)');
                        fd.append('bet_amount', t.amount);
                        fd.append('result_info', `${hits}/${selectedCount} Hits (0x)`);
                        fetch('/record_loss', {method: 'POST', body: fd});
                    }
                }
            });
            
            kenoTickets = [];
            kenoTotalRoundBetsCount = 0;
            renderKenoTicketsUI();

            setTimeout(() => {
                document.querySelectorAll('.keno-num').forEach(el => {
                    el.classList.remove('drawn-regular', 'ticket-matched');
                });
            }, 3000);
        }

        function fetchUserHistory() {
            fetch('/user_history').then(r=>r.json()).then(d=>{
                let tbody = document.getElementById('user-history-tbody');
                if(!d.history || d.history.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: var(--text-muted);">ምንም ሂስትሪ የለም</td></tr>`;
                    return;
                }
                let html = "";
                d.history.forEach(h => {
                    let isWin = h.win_amount > 0;
                    html += `<tr>
                        <td><b>${h.game}</b></td>
                        <td>${h.bet_amount} ETB</td>
                        <td>${h.result_info}</td>
                        <td class="${isWin ? 'badge-win' : 'badge-loss'}">${isWin ? '+' + h.win_amount + ' ETB' : '0.00 ETB'}</td>
                    </tr>`;
                });
                tbody.innerHTML = html;
            });
        }

        window.onload = function() {
            runAviatorAutoEngine();
            runKenoTimerEngine();
            window.addEventListener('resize', resizeCanvas);
        };

        function login() {
            let fd = new FormData();
            fd.append('phone', document.getElementById('auth-phone').value);
            fd.append('password', document.getElementById('auth-password').value);
            fetch('/login', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{ if(d.success) location.reload(); else alert(d.message); });
        }
        function register() {
            let fd = new FormData();
            fd.append('phone', document.getElementById('auth-phone').value);
            fd.append('password', document.getElementById('auth-password').value);
            fetch('/register', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{ if(d.success) location.reload(); else alert(d.message); });
        }

        function openDepositModal() { document.getElementById('deposit-modal').style.display = 'flex'; }
        function openWithdrawModal() { document.getElementById('withdraw-modal').style.display = 'flex'; }
        function closeModal(id) { document.getElementById(id).style.display = 'none'; }
        
        function submitDepositForm() {
            let amount = document.getElementById('dep-amount-input').value;
            if(!amount) { alert("እባክዎን የብር መጠን ያስገቡ!"); return; }

            let fd = new FormData();
            fd.append('amount', amount);
            fetch('/deposit', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{
                alert(d.message); if(d.success) closeModal('deposit-modal');
            });
        }

        function submitWithdrawForm() {
            let method = document.getElementById('with-method').value;
            let account = document.getElementById('with-account').value;
            let amount = document.getElementById('with-amount').value;

            let fd = new FormData();
            fd.append('method', method); fd.append('account', account); fd.append('amount', amount);
            fetch('/withdraw', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>{
                alert(d.message); if(d.success) closeModal('withdraw-modal');
            });
        }
    </script>
</body>
</html>
"""

ADMIN_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="am">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="5"> <!-- Auto refresh every 5 seconds -->
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ethio Bet - Admin Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; background: #12181f; color: #fff; padding: 20px; }
        h1, h2 { color: #f5a623; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 30px; background: #1a222d; }
        th, td { border: 1px solid #26323f; padding: 10px; text-align: left; }
        th { background: #0c1015; color: #8b949e; }
        .btn-approve { background: #00e676; color: #000; border: none; padding: 6px 12px; font-weight: bold; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }
        .btn-reject { background: #ff1744; color: #fff; border: none; padding: 6px 12px; font-weight: bold; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }
        .nav-home { color: #00e676; text-decoration: none; font-weight: bold; display: inline-block; margin-bottom: 20px; }
    </style>
</head>
<body>
    <a href="/" class="nav-home">← ወደ ዋናው ገጽ ተመለስ (Back to Home)</a>
    <h1>Admin Control Panel</h1>
    <p style="font-size: 12px; color: #8b949e;">ይህ ገጽ በየ 5 ሰከንዱ ራሱን ያድሳል (Auto-refreshes every 5s)</p>
    <hr style="border-color: #26323f; margin-bottom: 20px;">

    <h2>1. የዲፖዚት ጥያቄዎች (Deposit Requests)</h2>
    <table>
        <thead>
            <tr>
                <th>ተራ ቁጥር</th>
                <th>ስልክ ቁጥር</th>
                <th>መጠን (ETB)</th>
                <th>እርምጃ (Action)</th>
            </tr>
        </thead>
        <tbody>
            {% if not deposit_requests %}
            <tr><td colspan="4" style="text-align: center; color: #8b949e;">ምንም የዲፖዚት ጥያቄ የለም</td></tr>
            {% endif %}
            {% for req in deposit_requests %}
            <tr>
                <td>{{ loop.index }}</td>
                <td><b>{{ req.phone }}</b></td>
                <td style="color: #00e676; font-weight: bold;">{{ "%.2f"|format(req.amount) }} ETB</td>
                <td>
                    <a href="/admin/approve_deposit/{{ loop.index0 }}" class="btn-approve">አፅድቅ (Approve)</a>
                    <a href="/admin/reject_deposit/{{ loop.index0 }}" class="btn-reject">ሰርዝ (Reject)</a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <h2>2. የብር ማውጫ ጥያቄዎች (Withdraw Requests)</h2>
    <table>
        <thead>
            <tr>
                <th>ተራ ቁጥር</th>
                <th>ስልክ ቁጥር</th>
                <th>አካውንት/ስልክ</th>
                <th>ዘዴ</th>
                <th>መጠን (ETB)</th>
                <th>እርምጃ (Action)</th>
            </tr>
        </thead>
        <tbody>
            {% if not withdraw_requests %}
            <tr><td colspan="6" style="text-align: center; color: #8b949e;">ምንም የብር ማውጫ ጥያቄ የለም</td></tr>
            {% endif %}
            {% for req in withdraw_requests %}
            <tr>
                <td>{{ loop.index }}</td>
                <td><b>{{ req.phone }}</b></td>
                <td>{{ req.account }}</td>
                <td>{{ req.method }}</td>
                <td style="color: #ff9800; font-weight: bold;">{{ "%.2f"|format(req.amount) }} ETB</td>
                <td>
                    <a href="/admin/approve_withdraw/{{ loop.index0 }}" class="btn-approve">ተፈፅሟል (Complete)</a>
                    <a href="/admin/reject_withdraw/{{ loop.index0 }}" class="btn-reject">መልስ/ሰርዝ (Reject)</a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

@app.route('/')
def index():
    if 'user' not in session:
        return render_template_string(HTML_TEMPLATE, logged_in=False)
    
    phone = session['user']
    user_data = users_db.get(phone, {"balance": 0.0, "is_admin": False})
    return render_template_string(HTML_TEMPLATE, 
                                  logged_in=True, 
                                  phone=phone, 
                                  balance=user_data['balance'], 
                                  is_admin=user_data.get('is_admin', False))

@app.route('/register', methods=['POST'])
def register():
    phone = request.form.get('phone', '').strip()
    password = request.form.get('password', '').strip()
    if not phone or not password or phone in users_db:
        return jsonify({"success": False, "message": "መረጃው ተሳስቷል ወይም አስቀድሞ አለ!"})
    
    users_db[phone] = { "password": generate_password_hash(password), "balance": 0.0, "is_admin": False }
    session['user'] = phone
    return jsonify({"success": True})

@app.route('/login', methods=['POST'])
def login():
    phone = request.form.get('phone', '').strip()
    password = request.form.get('password', '').strip()
    user = users_db.get(phone)
    if user and check_password_hash(user['password'], password):
        session['user'] = phone
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "የተሳሳተ መረጃ!"})

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/place_bet', methods=['POST'])
def place_bet():
    if 'user' not in session: return jsonify({"success": False})
    phone = session['user']
    bet_amount = float(request.form.get('amount', 0))
    if users_db[phone]['balance'] < bet_amount or bet_amount <= 0:
        return jsonify({"success": False, "message": "በቂ ባላንስ የሎትም!"})
    users_db[phone]['balance'] -= bet_amount
    return jsonify({"success": True, "new_balance": users_db[phone]['balance']})

@app.route('/cancel_bet', methods=['POST'])
def cancel_bet():
    if 'user' not in session: return jsonify({"success": False})
    phone = session['user']
    amount = float(request.form.get('amount', 0))
    users_db[phone]['balance'] += amount
    return jsonify({"success": True, "new_balance": users_db[phone]['balance']})

@app.route('/cashout', methods=['POST'])
def cashout():
    if 'user' not in session: return jsonify({"success": False})
    phone = session['user']
    win_amount = float(request.form.get('win_amount', 0))
    bet_amount = float(request.form.get('bet_amount', 0))
    game = request.form.get('game', 'Game')
    result_info = request.form.get('result_info', '')

    users_db[phone]['balance'] += win_amount
    global_bet_history.append({"phone": phone, "game": game, "bet_amount": bet_amount, "win_amount": win_amount, "result_info": result_info})
    return jsonify({"success": True, "new_balance": users_db[phone]['balance']})

@app.route('/record_loss', methods=['POST'])
def record_loss():
    if 'user' not in session: return jsonify({"success": False})
    phone = session['user']
    bet_amount = float(request.form.get('bet_amount', 0))
    game = request.form.get('game', 'Game')
    result_info = request.form.get('result_info', '')

    global_bet_history.append({"phone": phone, "game": game, "bet_amount": bet_amount, "win_amount": 0, "result_info": result_info})
    return jsonify({"success": True})

@app.route('/draw_keno_numbers')
def draw_keno_numbers():
    drawn = random.sample(range(1, 81), 20)
    return jsonify({"drawn": drawn})

@app.route('/join_bingo', methods=['POST'])
def join_bingo():
    if 'user' not in session: return jsonify({"success": False, "message": "እባክዎን አስቀድመው ይግቡ!"})
    phone = session['user']
    stake = int(request.form.get('stake', 10))
    card_ids_str = request.form.get('card_ids', '[]')
    card_ids = json.loads(card_ids_str)

    total_stake = stake * len(card_ids)

    if users_db[phone]['balance'] < total_stake:
        return jsonify({"success": False, "message": "በቂ ባላንስ የሎትም!"})

    users_db[phone]['balance'] -= total_stake
    
    net_stake = total_stake * 0.80
    room = bingo_rooms.get(stake, bingo_rooms[10])
    
    if phone not in room['players']:
        room['players'][phone] = []
    
    room['players'][phone].extend(card_ids)
    room['pot'] += net_stake

    selected_cards = [{"id": cid, "card": BINGO_CARDS.get(cid)} for cid in card_ids]
    return jsonify({
        "success": True, 
        "new_balance": users_db[phone]['balance'], 
        "cards": selected_cards
    })

@app.route('/bingo_room_status')
def bingo_room_status():
    stake = int(request.args.get('stake', 10))
    room = bingo_rooms.get(stake, bingo_rooms[10])
    player_count = sum(len(cards) for cards in room['players'].values())
    return jsonify({
        "player_count": player_count,
        "pot": room['pot'],
        "status": room['status']
    })

@app.route('/claim_bingo', methods=['POST'])
def claim_bingo():
    if 'user' not in session: return jsonify({"success": False})
    phone = session['user']
    stake = int(request.form.get('stake', 10))
    room = bingo_rooms.get(stake, bingo_rooms[10])
    
    win_amount = room['pot'] if room['pot'] > 0 else stake * 2
    users_db[phone]['balance'] += win_amount
    room['pot'] = 0.0

    global_bet_history.append({"phone": phone, "game": f"Bingo ({stake} ETB Room)", "bet_amount": stake, "win_amount": win_amount, "result_info": "Bingo Won!"})
    return jsonify({"success": True, "new_balance": users_db[phone]['balance'], "win_amount": win_amount})

@app.route('/cancel_bingo', methods=['POST'])
def cancel_bingo():
    if 'user' not in session: return jsonify({"success": False})
    phone = session['user']
    stake = int(request.form.get('stake', 10))
    card_count = int(request.form.get('card_count', 1))
    
    refund_amount = stake * card_count
    users_db[phone]['balance'] += refund_amount
    
    room = bingo_rooms.get(stake, bingo_rooms[10])
    if phone in room['players']:
        room['players'].pop(phone, None)
        room['pot'] -= (refund_amount * 0.80)
        if room['pot'] < 0: room['pot'] = 0.0

    return jsonify({"success": True, "message": "ቲኬቱ ተሰርዟል፣ ብርዎ ተመልሷል!", "new_balance": users_db[phone]['balance']})

@app.route('/update_keno_history', methods=['POST'])
def update_keno_history():
    draws_str = request.form.get('draws', '[]')
    draws = json.loads(draws_str)
    keno_recent_draws.insert(0, draws)
    if len(keno_recent_draws) > 3:
        keno_recent_draws.pop()
    return jsonify({"success": True, "recent": keno_recent_draws})

@app.route('/aviator_history_data')
def aviator_history_data():
    return jsonify({"history": aviator_history_list})

@app.route('/add_aviator_history', methods=['POST'])
def add_aviator_history():
    mult = request.form.get('mult', '2.00x')
    aviator_history_list.insert(0, mult)
    if len(aviator_history_list) > 10:
        aviator_history_list.pop()
    return jsonify({"success": True})

@app.route('/user_history')
def user_history():
    if 'user' not in session: return jsonify({"history": []})
    phone = session['user']
    user_hist = [h for h in global_bet_history if h['phone'] == phone]
    return jsonify({"history": user_hist[::-1]})

@app.route('/deposit', methods=['POST'])
def deposit():
    if 'user' not in session: return jsonify({"success": False, "message": "እባክዎን አስቀድመው ይግቡ!"})
    try:
        amount = float(request.form.get('amount', 0))
    except ValueError:
        return jsonify({"success": False, "message": "እባክዎን ትክክለኛ የብር መጠን ያስገቡ!"})
        
    if amount <= 0: return jsonify({"success": False, "message": "ልክ ያልሆነ መጠን!"})
    deposit_requests.append({"phone": session['user'], "amount": amount})
    return jsonify({"success": True, "message": "የብር ማስገቢያ ጥያቄዎ ተልኳል! በቅርብ ጊዜ ይጸድቃል።"})

@app.route('/withdraw', methods=['POST'])
def withdraw():
    if 'user' not in session: return jsonify({"success": False, "message": "እባክዎን አስቀድመው ይግቡ!"})
    phone = session['user']
    try:
        amount = float(request.form.get('amount', 0))
    except ValueError:
        return jsonify({"success": False, "message": "እባክዎን ትክክለኛ የብር መጠን ያስገቡ!"})
        
    method = request.form.get('method', 'Telebirr')
    account = request.form.get('account', '')
    
    if users_db[phone]['balance'] < amount or amount <= 0:
        return jsonify({"success": False, "message": "በቂ ባላንስ የሎትም!"})
    
    users_db[phone]['balance'] -= amount
    withdraw_requests.append({"phone": phone, "amount": amount, "method": method, "account": account})
    return jsonify({"success": True, "message": "የብር ማውጫ ጥያቄዎ ተሳክቷል!"})

# ==========================================
# ADMIN DASHBOARD & REQUEST HANDLING ROUTES
# ==========================================
@app.route('/admin')
def admin():
    if 'user' not in session or not users_db.get(session['user'], {}).get('is_admin', False):
        return redirect(url_for('index'))
    return render_template_string(
        ADMIN_HTML_TEMPLATE, 
        deposit_requests=deposit_requests, 
        withdraw_requests=withdraw_requests
    )

@app.route('/admin/approve_deposit/<int:req_id>')
def approve_deposit(req_id):
    if 'user' not in session or not users_db.get(session['user'], {}).get('is_admin', False):
        return redirect(url_for('index'))
    if 0 <= req_id < len(deposit_requests):
        req = deposit_requests.pop(req_id)
        phone = req['phone']
        amount = req['amount']
        if phone in users_db:
            users_db[phone]['balance'] += amount
    return redirect(url_for('admin'))

@app.route('/admin/reject_deposit/<int:req_id>')
def reject_deposit(req_id):
    if 'user' not in session or not users_db.get(session['user'], {}).get('is_admin', False):
        return redirect(url_for('index'))
    if 0 <= req_id < len(deposit_requests):
        deposit_requests.pop(req_id)
    return redirect(url_for('admin'))

@app.route('/admin/approve_withdraw/<int:req_id>')
def approve_withdraw(req_id):
    if 'user' not in session or not users_db.get(session['user'], {}).get('is_admin', False):
        return redirect(url_for('index'))
    if 0 <= req_id < len(withdraw_requests):
        withdraw_requests.pop(req_id)
    return redirect(url_for('admin'))

@app.route('/admin/reject_withdraw/<int:req_id>')
def reject_withdraw(req_id):
    if 'user' not in session or not users_db.get(session['user'], {}).get('is_admin', False):
        return redirect(url_for('index'))
    if 0 <= req_id < len(withdraw_requests):
        req = withdraw_requests.pop(req_id)
        phone = req['phone']
        amount = req['amount']
        if phone in users_db:
            users_db[phone]['balance'] += amount
    return redirect(url_for('admin'))

# ==========================================
# LIVE GAME STATE API (ለሁሉም ሰው እኩል እንዲሆን)
# ==========================================
import time

@app.route('/api/live-status')
def get_live_status():
    current_timestamp = int(time.time())
    cycle = current_timestamp % 15  # በየ 15 ሰከንዱ የሚደጋገም ዙር
    
    if cycle < 10:
        multiplier = round(1.0 + (cycle * 0.25), 2)
        crashed = False
    else:
        multiplier = round(1.0 + (10 * 0.25), 2)
        crashed = True

    return jsonify({
        "timestamp": current_timestamp,
        "aviator_multiplier": multiplier,
        "is_crashed": crashed,
        "time_left": 15 - cycle
    })
# ==========================================
# 150 BOARDS STANDARD BINGO (1-75) SYSTEM
# ==========================================
BINGO_CARD_PRICE = 10.0
BINGO_WIN_PERCENTAGE = 0.80

def generate_bingo_board(board_id):
    random.seed(board_id)
    board = {
        'B': random.sample(range(1, 16), 5),
        'I': random.sample(range(16, 31), 5),
        'N': random.sample(range(31, 46), 5),
        'G': random.sample(range(46, 61), 5),
        'O': random.sample(range(61, 76), 5)
    }
    board['N'][2] = "FREE"
    return board

@app.route('/api/bingo/board/<int:board_id>')
def get_bingo_board(board_id):
    if board_id < 1 or board_id > 150:
        return jsonify({"error": "Board ID must be between 1 and 150"}), 400
    return jsonify({
        "board_id": board_id,
        "grid": generate_bingo_board(board_id)
    })

@app.route('/api/bingo/live')
def get_bingo_live():
    current_time = int(time.time())
    step = (current_time // 3) % 75
    random.seed(current_time // 300)
    all_numbers = list(range(1, 76))
    random.shuffle(all_numbers)
    
    drawn = all_numbers[:step + 1]
    current = drawn[-1] if drawn else None

    return jsonify({
        "current_number": current,
        "drawn_numbers": drawn,
        "total_drawn": len(drawn),
        "next_in_seconds": 3 - (current_time % 3)
    })

@app.route('/api/bingo/claim', methods=['POST'])
def claim_bingo():
    data = request.json
    phone = data.get('phone')
    board_id = data.get('board_id')
    
    if phone not in users_db:
        return jsonify({"success": False, "message": "እባክዎ በመጀመሪያ ይግቡ (Login)!"}), 400

    grid = generate_bingo_board(int(board_id))
    current_time = int(time.time())
    step = (current_time // 3) % 75
    random.seed(current_time // 300)
    all_numbers = list(range(1, 76))
    random.shuffle(all_numbers)
    drawn_numbers = set(all_numbers[:step + 1])
    
    is_winner = True
    for letter in ['B', 'I', 'N', 'G', 'O']:
        for val in grid[letter]:
            if val != "FREE" and val not in drawn_numbers:
                is_winner = False
                break
        if not is_winner:
            break

    if is_winner:
        reward = BINGO_CARD_PRICE * 150 * BINGO_WIN_PERCENTAGE
        users_db[phone]['balance'] += reward
        return jsonify({
            "success": True,
            "message": f"እንኳን ደስ አለዎት! BINGO አሸንፈዋል! {reward} ብር ባላንስዎ ላይ ተጨምሯል።",
            "new_balance": users_db[phone]['balance']
        })
    else:
        return jsonify({
            "success": False,
            "message": "ቦርድዎ ገና አልሞላም! ተጨማሪ ቁጥሮች እስኪወጡ ይጠብቁ።"
        })
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
