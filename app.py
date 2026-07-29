from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import random
import os

app = Flask(__name__)
CORS(app)

user_data = {
    "balance": 1000.00
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="am">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kino Gaming - Aviator & Keno</title>
    <meta name="google-site-verification" content="nup0GQ6hYkA57wXjtXvAdY5gUvLxF2dOgpAHfi_bScg" />
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #0f172a; color: white; font-family: sans-serif; }
        canvas { background-color: #1e293b; border-radius: 8px; width: 100%; height: 200px; }
    </style>
</head>
<body class="p-4 max-w-md mx-auto">

    <header class="flex justify-between items-center mb-6 bg-slate-800 p-4 rounded-xl shadow-lg">
        <h1 class="text-xl font-bold text-yellow-400">Kino Games</h1>
        <div class="bg-slate-900 px-3 py-1.5 rounded-lg border border-yellow-500/30">
            <span class="text-xs text-gray-400">ሒሳብ:</span>
            <span id="balance" class="font-bold text-green-400">0.00</span> <span class="text-xs text-yellow-400">ብር</span>
        </div>
    </header>

    <div class="flex gap-2 mb-6">
        <button onclick="switchGame('aviator')" id="btn-aviator" class="flex-1 py-2.5 rounded-lg font-bold bg-red-600 text-white shadow">✈️ Aviator</button>
        <button onclick="switchGame('keno')" id="btn-keno" class="flex-1 py-2.5 rounded-lg font-bold bg-slate-700 text-gray-300">🎱 Keno</button>
    </div>

    <div id="aviator-section" class="space-y-4">
        <div class="relative">
            <canvas id="aviatorCanvas"></canvas>
            <div id="multiplierText" class="absolute inset-0 flex items-center justify-center text-4xl font-extrabold text-white">1.00x</div>
        </div>

        <div class="bg-slate-800 p-4 rounded-xl space-y-3">
            <div class="flex justify-between items-center">
                <span class="text-sm font-semibold">የውርርድ መጠን (ብር):</span>
                <input type="number" id="aviatorBetAmount" value="50" class="bg-slate-900 text-center w-24 py-1.5 rounded border border-slate-700 font-bold text-yellow-400">
            </div>
            <button id="aviatorBtn" onclick="playAviator()" class="w-full py-3 bg-green-600 hover:bg-green-500 font-bold text-lg rounded-xl transition active:scale-95 shadow-lg">መወራረድ (Bet)</button>
        </div>
    </div>

    <div id="keno-section" class="hidden space-y-4">
        <div class="bg-slate-800 p-4 rounded-xl">
            <div class="flex justify-between items-center mb-3">
                <p class="text-xs text-gray-400">ከ 1 እስከ 40 ውስጥ ቁጥር ይምረጡ</p>
                <span id="selectedCount" class="text-xs bg-yellow-500 text-black px-2 py-0.5 rounded font-bold">0/10</span>
            </div>
            <div id="kenoGrid" class="grid grid-cols-8 gap-1.5"></div>
        </div>

        <div class="bg-slate-800 p-4 rounded-xl space-y-3">
            <div class="flex justify-between items-center">
                <span class="text-sm font-semibold">የውርርድ መጠን (ብር):</span>
                <input type="number" id="kenoBetAmount" value="20" class="bg-slate-900 text-center w-24 py-1.5 rounded border border-slate-700 font-bold text-yellow-400">
            </div>
            <button onclick="playKeno()" class="w-full py-3 bg-yellow-600 hover:bg-yellow-500 font-bold text-lg rounded-xl transition active:scale-95 shadow-lg">ጨዋታውን ጀምር (Play Keno)</button>
        </div>
        <div id="kenoResult" class="text-center font-bold text-sm min-h-[24px]"></div>
    </div>

    <script>
        const API_URL = "/api";

        async function fetchBalance() {
            try {
                let res = await fetch(`${API_URL}/balance`);
                let data = await res.json();
                document.getElementById('balance').innerText = data.balance.toFixed(2);
            } catch(e) { console.log("Error", e); }
        }
        fetchBalance();

        function switchGame(game) {
            if(game === 'aviator') {
                document.getElementById('aviator-section').classList.remove('hidden');
                document.getElementById('keno-section').classList.add('hidden');
                document.getElementById('btn-aviator').className = "flex-1 py-2.5 rounded-lg font-bold bg-red-600 text-white shadow";
                document.getElementById('btn-keno').className = "flex-1 py-2.5 rounded-lg font-bold bg-slate-700 text-gray-300";
            } else {
                document.getElementById('aviator-section').classList.add('hidden');
                document.getElementById('keno-section').classList.remove('hidden');
                document.getElementById('btn-keno').className = "flex-1 py-2.5 rounded-lg font-bold bg-yellow-600 text-white shadow";
                document.getElementById('btn-aviator').className = "flex-1 py-2.5 rounded-lg font-bold bg-slate-700 text-gray-300";
            }
        }

        const kenoGrid = document.getElementById('kenoGrid');
        let selectedKeno = [];
        for(let i=1; i<=40; i++) {
            let btn = document.createElement('button');
            btn.innerText = i;
            btn.id = `keno-btn-${i}`;
            btn.className = "p-2 bg-slate-700 rounded font-bold text-xs hover:bg-slate-600 transition";
            btn.onclick = () => {
                if(selectedKeno.includes(i)) {
                    selectedKeno = selectedKeno.filter(num => num !== i);
                    btn.classList.remove('bg-yellow-500', 'text-black');
                    btn.classList.add('bg-slate-700');
                } else if(selectedKeno.length < 10) {
                    selectedKeno.push(i);
                    btn.classList.add('bg-yellow-500', 'text-black');
                    btn.classList.remove('bg-slate-700');
                }
                document.getElementById('selectedCount').innerText = `${selectedKeno.length}/10`;
            };
            kenoGrid.appendChild(btn);
        }

        async function playKeno() {
            let bet = parseFloat(document.getElementById('kenoBetAmount').value);
            let resText = document.getElementById('kenoResult');

            if(selectedKeno.length === 0) {
                alert("እባክዎን ከ 1 እስከ 10 ቁጥሮችን ይምረጡ!");
                return;
            }

            try {
                let response = await fetch(`${API_URL}/keno/play`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ bet: bet, numbers: selectedKeno })
                });

                let data = await response.json();
                if(response.status !== 200) { alert(data.message); return; }

                for(let i=1; i<=40; i++) {
                    let b = document.getElementById(`keno-btn-${i}`);
                    if(!selectedKeno.includes(i)) b.className = "p-2 bg-slate-700 rounded font-bold text-xs";
                }

                data.drawn_numbers.forEach(num => {
                    let b = document.getElementById(`keno-btn-${num}`);
                    if(selectedKeno.includes(num)) {
                        b.className = "p-2 bg-green-500 text-white rounded font-bold text-xs animate-bounce";
                    } else {
                        b.className = "p-2 bg-red-500/50 text-white rounded font-bold text-xs";
                    }
                });

                document.getElementById('balance').innerText = data.new_balance.toFixed(2);
                if(data.win_amount > 0) {
                    resText.className = "text-center font-bold text-sm text-green-400";
                    resText.innerText = `🎉 እንኳን ደስ አለዎት! ${data.match_count} ቁጥር ገጥሞልዎታል: ${data.win_amount} ብር አሸነፉ!`;
                } else {
                    resText.className = "text-center font-bold text-sm text-red-400";
                    resText.innerText = `❌ አልገጠመም (${data.match_count} ገጠመ)። እንደገና ይሞክሩ!`;
                }
            } catch(e) { alert("የሰርቨር ችግር አጋጥሟል!"); }
        }

        let isFlying = false;
        let currentMult = 1.00;
        let flightInterval;

        async function playAviator() {
            let btn = document.getElementById('aviatorBtn');
            let multText = document.getElementById('multiplierText');
            let bet = parseFloat(document.getElementById('aviatorBetAmount').value);

            if(!isFlying) {
                isFlying = true;
                btn.innerText = "Cash Out (ወጣሁ)";
                btn.className = "w-full py-3 bg-orange-500 hover:bg-orange-400 font-bold text-lg rounded-xl transition shadow-lg";

                currentMult = 1.00;
                multText.style.color = "white";

                flightInterval = setInterval(() => {
                    currentMult += 0.02;
                    multText.innerText = currentMult.toFixed(2) + "x";
                }, 80);

            } else {
                clearInterval(flightInterval);
                isFlying = false;

                try {
                    let response = await fetch(`${API_URL}/aviator/play`, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ bet: bet, cashout: currentMult })
                    });
                    let data = await response.json();

                    if(data.won) {
                        multText.style.color = "#4ade80";
                        multText.innerText = `WIN ${data.win_amount} ብር!`;
                        alert(`እንኳን ደስ አለዎት! በ ${currentMult.toFixed(2)}x ወጥተው ${data.win_amount} ብር አሸንፈዋል!`);
                    } else {
                        multText.style.color = "#ef4444";
                        multText.innerText = `CRASHED @ ${data.crash_point}x`;
                        alert(`አውሮፕላኗ በ ${data.crash_point}x ላይ ተከሰከሰች! ተሸንፈዋል።`);
                    }

                    document.getElementById('balance').innerText = data.new_balance.toFixed(2);
                    btn.innerText = "መወራረድ (Bet)";
                    btn.className = "w-full py-3 bg-green-600 hover:bg-green-500 font-bold text-lg rounded-xl transition shadow-lg";
                } catch(e) { alert("የውጤት ችግር አጋጥሟል!"); }
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/balance', methods=['GET'])
def get_balance():
    return jsonify({"balance": user_data["balance"]})

@app.route('/api/aviator/play', methods=['POST'])
def aviator_play():
    data = request.json
    bet_amount = float(data.get('bet', 0))
    cashout_mult = float(data.get('cashout', 0))

    if bet_amount > user_data["balance"] or bet_amount <= 0:
        return jsonify({"status": "error", "message": "በቂ ብር የለዎትም!"}), 400

    user_data["balance"] -= bet_amount

    if random.randint(1, 100) <= 5:
        crash_point = 1.00
    else:
        crash_point = round(random.uniform(1.01, 15.00), 2)

    won = False
    win_amount = 0

    if cashout_mult > 0 and cashout_mult <= crash_point:
        won = True
        win_amount = round(bet_amount * cashout_mult, 2)
        user_data["balance"] += win_amount

    return jsonify({
        "crash_point": crash_point,
        "won": won,
        "win_amount": win_amount,
        "new_balance": round(user_data["balance"], 2)
    })

@app.route('/api/keno/play', methods=['POST'])
def keno_play():
    data = request.json
    bet_amount = float(data.get('bet', 0))
    user_numbers = data.get('numbers', [])

    if bet_amount > user_data["balance"] or bet_amount <= 0:
        return jsonify({"status": "error", "message": "በቂ ብር የለዎትም!"}), 400

    if len(user_numbers) == 0 or len(user_numbers) > 10:
        return jsonify({"status": "error", "message": "እባክዎን ከ 1 እስከ 10 ቁጥሮችን ይምረጡ!"}), 400

    user_data["balance"] -= bet_amount

    drawn_numbers = random.sample(range(1, 41), 10)
    matched_numbers = list(set(user_numbers).intersection(drawn_numbers))
    match_count = len(matched_numbers)

    multipliers = {0: 0, 1: 0, 2: 1.5, 3: 3.0, 4: 5.0, 5: 10.0, 6: 25.0, 7: 50.0, 8: 100.0, 9: 200.0, 10: 500.0}
    multiplier = multipliers.get(match_count, 0)
    
    win_amount = round(bet_amount * multiplier, 2)
    user_data["balance"] += win_amount

    return jsonify({
        "drawn_numbers": drawn_numbers,
        "matched_numbers": matched_numbers,
        "match_count": match_count,
        "win_amount": win_amount,
        "new_balance": round(user_data["balance"], 2)
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

    <div class="flex gap-2 mb-6">
        <button onclick="switchGame('aviator')" id="btn-aviator" class="flex-1 py-2.5 rounded-lg font-bold bg-red-600 text-white shadow">✈️ Aviator</button>
        <button onclick="switchGame('keno')" id="btn-keno" class="flex-1 py-2.5 rounded-lg font-bold bg-slate-700 text-gray-300">🎱 Keno</button>
    </div>

    <div id="aviator-section" class="space-y-4">
        <div class="relative">
            <canvas id="aviatorCanvas"></canvas>
            <div id="multiplierText" class="absolute inset-0 flex items-center justify-center text-4xl font-extrabold text-white">1.00x</div>
        </div>

        <div class="bg-slate-800 p-4 rounded-xl space-y-3">
            <div class="flex justify-between items-center">
                <span class="text-sm font-semibold">የውርርድ መጠን (ብር):</span>
                <input type="number" id="aviatorBetAmount" value="50" class="bg-slate-900 text-center w-24 py-1.5 rounded border border-slate-700 font-bold text-yellow-400">
            </div>
            <button id="aviatorBtn" onclick="playAviator()" class="w-full py-3 bg-green-600 hover:bg-green-500 font-bold text-lg rounded-xl transition active:scale-95 shadow-lg">መወራረድ (Bet)</button>
        </div>
    </div>

    <div id="keno-section" class="hidden space-y-4">
        <div class="bg-slate-800 p-4 rounded-xl">
            <div class="flex justify-between items-center mb-3">
                <p class="text-xs text-gray-400">ከ 1 እስከ 40 ውስጥ ቁጥር ይምረጡ</p>
                <span id="selectedCount" class="text-xs bg-yellow-500 text-black px-2 py-0.5 rounded font-bold">0/10</span>
            </div>
            <div id="kenoGrid" class="grid grid-cols-8 gap-1.5"></div>
        </div>

        <div class="bg-slate-800 p-4 rounded-xl space-y-3">
            <div class="flex justify-between items-center">
                <span class="text-sm font-semibold">የውርርድ መጠን (ብር):</span>
                <input type="number" id="kenoBetAmount" value="20" class="bg-slate-900 text-center w-24 py-1.5 rounded border border-slate-700 font-bold text-yellow-400">
            </div>
            <button onclick="playKeno()" class="w-full py-3 bg-yellow-600 hover:bg-yellow-500 font-bold text-lg rounded-xl transition active:scale-95 shadow-lg">ጨዋታውን ጀምር (Play Keno)</button>
        </div>
        <div id="kenoResult" class="text-center font-bold text-sm min-h-[24px]"></div>
    </div>

    <script>
        const API_URL = "/api";

        async function fetchBalance() {
            try {
                let res = await fetch(`${API_URL}/balance`);
                let data = await res.json();
                document.getElementById('balance').innerText = data.balance.toFixed(2);
            } catch(e) { console.log("Error", e); }
        }
        fetchBalance();

        function switchGame(game) {
            if(game === 'aviator') {
                document.getElementById('aviator-section').classList.remove('hidden');
                document.getElementById('keno-section').classList.add('hidden');
                document.getElementById('btn-aviator').className = "flex-1 py-2.5 rounded-lg font-bold bg-red-600 text-white shadow";
                document.getElementById('btn-keno').className = "flex-1 py-2.5 rounded-lg font-bold bg-slate-700 text-gray-300";
            } else {
                document.getElementById('aviator-section').classList.add('hidden');
                document.getElementById('keno-section').classList.remove('hidden');
                document.getElementById('btn-keno').className = "flex-1 py-2.5 rounded-lg font-bold bg-yellow-600 text-white shadow";
                document.getElementById('btn-aviator').className = "flex-1 py-2.5 rounded-lg font-bold bg-slate-700 text-gray-300";
            }
        }

        const kenoGrid = document.getElementById('kenoGrid');
        let selectedKeno = [];
        for(let i=1; i<=40; i++) {
            let btn = document.createElement('button');
            btn.innerText = i;
            btn.id = `keno-btn-${i}`;
            btn.className = "p-2 bg-slate-700 rounded font-bold text-xs hover:bg-slate-600 transition";
            btn.onclick = () => {
                if(selectedKeno.includes(i)) {
                    selectedKeno = selectedKeno.filter(num => num !== i);
                    btn.classList.remove('bg-yellow-500', 'text-black');
                    btn.classList.add('bg-slate-700');
                } else if(selectedKeno.length < 10) {
                    selectedKeno.push(i);
                    btn.classList.add('bg-yellow-500', 'text-black');
                    btn.classList.remove('bg-slate-700');
                }
                document.getElementById('selectedCount').innerText = `${selectedKeno.length}/10`;
            };
            kenoGrid.appendChild(btn);
        }

        async function playKeno() {
            let bet = parseFloat(document.getElementById('kenoBetAmount').value);
            let resText = document.getElementById('kenoResult');

            if(selectedKeno.length === 0) {
                alert("እባክዎን ከ 1 እስከ 10 ቁጥሮችን ይምረጡ!");
                return;
            }

            try {
                let response = await fetch(`${API_URL}/keno/play`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ bet: bet, numbers: selectedKeno })
                });

                let data = await response.json();
                if(response.status !== 200) { alert(data.message); return; }

                for(let i=1; i<=40; i++) {
                    let b = document.getElementById(`keno-btn-${i}`);
                    if(!selectedKeno.includes(i)) b.className = "p-2 bg-slate-700 rounded font-bold text-xs";
                }

                data.drawn_numbers.forEach(num => {
                    let b = document.getElementById(`keno-btn-${num}`);
                    if(selectedKeno.includes(num)) {
                        b.className = "p-2 bg-green-500 text-white rounded font-bold text-xs animate-bounce";
                    } else {
                        b.className = "p-2 bg-red-500/50 text-white rounded font-bold text-xs";
                    }
                });

                document.getElementById('balance').innerText = data.new_balance.toFixed(2);
                if(data.win_amount > 0) {
                    resText.className = "text-center font-bold text-sm text-green-400";
                    resText.innerText = `🎉 እንኳን ደስ አለዎት! ${data.match_count} ቁጥር ገጥሞልዎታል: ${data.win_amount} ብር አሸነፉ!`;
                } else {
                    resText.className = "text-center font-bold text-sm text-red-400";
                    resText.innerText = `❌ አልገጠመም (${data.match_count} ገጠመ)። እንደገና ይሞክሩ!`;
                }
            } catch(e) { alert("የሰርቨር ችግር አጋጥሟል!"); }
        }

        let isFlying = false;
        let currentMult = 1.00;
        let flightInterval;

        async function playAviator() {
            let btn = document.getElementById('aviatorBtn');
            let multText = document.getElementById('multiplierText');
            let bet = parseFloat(document.getElementById('aviatorBetAmount').value);

            if(!isFlying) {
                isFlying = true;
                btn.innerText = "Cash Out (ወጣሁ)";
                btn.className = "w-full py-3 bg-orange-500 hover:bg-orange-400 font-bold text-lg rounded-xl transition shadow-lg";

                currentMult = 1.00;
                multText.style.color = "white";

                flightInterval = setInterval(() => {
                    currentMult += 0.02;
                    multText.innerText = currentMult.toFixed(2) + "x";
                }, 80);

            } else {
                clearInterval(flightInterval);
                isFlying = false;

                try {
                    let response = await fetch(`${API_URL}/aviator/play`, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ bet: bet, cashout: currentMult })
                    });
                    let data = await response.json();

                    if(data.won) {
                        multText.style.color = "#4ade80";
                        multText.innerText = `WIN ${data.win_amount} ብር!`;
                        alert(`እንኳን ደስ አለዎት! በ ${currentMult.toFixed(2)}x ወጥተው ${data.win_amount} ብር አሸንፈዋል!`);
                    } else {
                        multText.style.color = "#ef4444";
                        multText.innerText = `CRASHED @ ${data.crash_point}x`;
                        alert(`አውሮፕላኗ በ ${data.crash_point}x ላይ ተከሰከሰች! ተሸንፈዋል።`);
                    }

                    document.getElementById('balance').innerText = data.new_balance.toFixed(2);
                    btn.innerText = "መወራረድ (Bet)";
                    btn.className = "w-full py-3 bg-green-600 hover:bg-green-500 font-bold text-lg rounded-xl transition shadow-lg";
                } catch(e) { alert("የውጤት ችግር አጋጥሟል!"); }
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/balance', methods=['GET'])
def get_balance():
    return jsonify({"balance": user_data["balance"]})

@app.route('/api/aviator/play', methods=['POST'])
def aviator_play():
    data = request.json
    bet_amount = float(data.get('bet', 0))
    cashout_mult = float(data.get('cashout', 0))

    if bet_amount > user_data["balance"] or bet_amount <= 0:
        return jsonify({"status": "error", "message": "በቂ ብር የለዎትም!"}), 400

    user_data["balance"] -= bet_amount

    if random.randint(1, 100) <= 5:
        crash_point = 1.00
    else:
        crash_point = round(random.uniform(1.01, 15.00), 2)

    won = False
    win_amount = 0

    if cashout_mult > 0 and cashout_mult <= crash_point:
        won = True
        win_amount = round(bet_amount * cashout_mult, 2)
        user_data["balance"] += win_amount

    return jsonify({
        "crash_point": crash_point,
        "won": won,
        "win_amount": win_amount,
        "new_balance": round(user_data["balance"], 2)
    })

@app.route('/api/keno/play', methods=['POST'])
def keno_play():
    data = request.json
    bet_amount = float(data.get('bet', 0))
    user_numbers = data.get('numbers', [])

    if bet_amount > user_data["balance"] or bet_amount <= 0:
        return jsonify({"status": "error", "message": "በቂ ብር የለዎትም!"}), 400

    if len(user_numbers) == 0 or len(user_numbers) > 10:
        return jsonify({"status": "error", "message": "እባክዎን ከ 1 እስከ 10 ቁጥሮችን ይምረጡ!"}), 400

    user_data["balance"] -= bet_amount

    drawn_numbers = random.sample(range(1, 41), 10)
    matched_numbers = list(set(user_numbers).intersection(drawn_numbers))
    match_count = len(matched_numbers)

    multipliers = {0: 0, 1: 0, 2: 1.5, 3: 3.0, 4: 5.0, 5: 10.0, 6: 25.0, 7: 50.0, 8: 100.0, 9: 200.0, 10: 500.0}
    multiplier = multipliers.get(match_count, 0)
    
    win_amount = round(bet_amount * multiplier, 2)
    user_data["balance"] += win_amount

    return jsonify({
        "drawn_numbers": drawn_numbers,
        "matched_numbers": matched_numbers,
        "match_count": match_count,
        "win_amount": win_amount,
        "new_balance": round(user_data["balance"], 2)
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
 onclick="switchGame('keno')" id="btn-keno" class="flex-1 py-2.5 rounded-lg font-bold bg-slate-700 text-gray-300">🎱 Keno</button>
    </div>

    <div id="aviator-section" class="space-y-4">
        <div class="relative">
            <canvas id="aviatorCanvas"></canvas>
            <div id="multiplierText" class="absolute inset-0 flex items-center justify-center text-4xl font-extrabold text-white">1.00x</div>
        </div>

        <div class="bg-slate-800 p-4 rounded-xl space-y-3">
            <div class="flex justify-between items-center">
                <span class="text-sm font-semibold">የውርርድ መጠን (ብር):</span>
                <input type="number" id="aviatorBetAmount" value="50" class="bg-slate-900 text-center w-24 py-1.5 rounded border border-slate-700 font-bold text-yellow-400">
            </div>
            <button id="aviatorBtn" onclick="playAviator()" class="w-full py-3 bg-green-600 hover:bg-green-500 font-bold text-lg rounded-xl transition active:scale-95 shadow-lg">መወራረድ (Bet)</button>
        </div>
    </div>

    <div id="keno-section" class="hidden space-y-4">
        <div class="bg-slate-800 p-4 rounded-xl">
            <div class="flex justify-between items-center mb-3">
                <p class="text-xs text-gray-400">ከ 1 እስከ 40 ውስጥ ቁጥር ይምረጡ</p>
                <span id="selectedCount" class="text-xs bg-yellow-500 text-black px-2 py-0.5 rounded font-bold">0/10</span>
            </div>
            <div id="kenoGrid" class="grid grid-cols-8 gap-1.5"></div>
        </div>

        <div class="bg-slate-800 p-4 rounded-xl space-y-3">
            <div class="flex justify-between items-center">
                <span class="text-sm font-semibold">የውርርድ መጠን (ብር):</span>
                <input type="number" id="kenoBetAmount" value="20" class="bg-slate-900 text-center w-24 py-1.5 rounded border border-slate-700 font-bold text-yellow-400">
            </div>
            <button onclick="playKeno()" class="w-full py-3 bg-yellow-600 hover:bg-yellow-500 font-bold text-lg rounded-xl transition active:scale-95 shadow-lg">ጨዋታውን ጀምር (Play Keno)</button>
        </div>
        <div id="kenoResult" class="text-center font-bold text-sm min-h-[24px]"></div>
    </div>

    <script>
        const API_URL = "/api";

        async function fetchBalance() {
            try {
                let res = await fetch(`${API_URL}/balance`);
                let data = await res.json();
                document.getElementById('balance').innerText = data.balance.toFixed(2);
            } catch(e) { console.log("Error", e); }
        }
        fetchBalance();

        function switchGame(game) {
            if(game === 'aviator') {
                document.getElementById('aviator-section').classList.remove('hidden');
                document.getElementById('keno-section').classList.add('hidden');
                document.getElementById('btn-aviator').className = "flex-1 py-2.5 rounded-lg font-bold bg-red-600 text-white shadow";
                document.getElementById('btn-keno').className = "flex-1 py-2.5 rounded-lg font-bold bg-slate-700 text-gray-300";
            } else {
                document.getElementById('aviator-section').classList.add('hidden');
                document.getElementById('keno-section').classList.remove('hidden');
                document.getElementById('btn-keno').className = "flex-1 py-2.5 rounded-lg font-bold bg-yellow-600 text-white shadow";
                document.getElementById('btn-aviator').className = "flex-1 py-2.5 rounded-lg font-bold bg-slate-700 text-gray-300";
            }
        }

        const kenoGrid = document.getElementById('kenoGrid');
        let selectedKeno = [];
        for(let i=1; i<=40; i++) {
            let btn = document.createElement('button');
            btn.innerText = i;
            btn.id = `keno-btn-${i}`;
            btn.className = "p-2 bg-slate-700 rounded font-bold text-xs hover:bg-slate-600 transition";
            btn.onclick = () => {
                if(selectedKeno.includes(i)) {
                    selectedKeno = selectedKeno.filter(num => num !== i);
                    btn.classList.remove('bg-yellow-500', 'text-black');
                    btn.classList.add('bg-slate-700');
                } else if(selectedKeno.length < 10) {
                    selectedKeno.push(i);
                    btn.classList.add('bg-yellow-500', 'text-black');
                    btn.classList.remove('bg-slate-700');
                }
                document.getElementById('selectedCount').innerText = `${selectedKeno.length}/10`;
            };
            kenoGrid.appendChild(btn);
        }

        async function playKeno() {
            let bet = parseFloat(document.getElementById('kenoBetAmount').value);
            let resText = document.getElementById('kenoResult');

            if(selectedKeno.length === 0) {
                alert("እባክዎን ከ 1 እስከ 10 ቁጥሮችን ይምረጡ!");
                return;
            }

            try {
                let response = await fetch(`${API_URL}/keno/play`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ bet: bet, numbers: selectedKeno })
                });

                let data = await response.json();
                if(response.status !== 200) { alert(data.message); return; }

                for(let i=1; i<=40; i++) {
                    let b = document.getElementById(`keno-btn-${i}`);
                    if(!selectedKeno.includes(i)) b.className = "p-2 bg-slate-700 rounded font-bold text-xs";
                }

                data.drawn_numbers.forEach(num => {
                    let b = document.getElementById(`keno-btn-${num}`);
                    if(selectedKeno.includes(num)) {
                        b.className = "p-2 bg-green-500 text-white rounded font-bold text-xs animate-bounce";
                    } else {
                        b.className = "p-2 bg-red-500/50 text-white rounded font-bold text-xs";
                    }
                });

                document.getElementById('balance').innerText = data.new_balance.toFixed(2);
                if(data.win_amount > 0) {
                    resText.className = "text-center font-bold text-sm text-green-400";
                    resText.innerText = `🎉 እንኳን ደስ አለዎት! ${data.match_count} ቁጥር ገጥሞልዎታል: ${data.win_amount} ብር አሸነፉ!`;
                } else {
                    resText.className = "text-center font-bold text-sm text-red-400";
                    resText.innerText = `❌ አልገጠመም (${data.match_count} ገጠመ)። እንደገና ይሞክሩ!`;
                }
            } catch(e) { alert("የሰርቨር ችግር አጋጥሟል!"); }
        }

        let isFlying = false;
        let currentMult = 1.00;
        let flightInterval;

        async function playAviator() {
            let btn = document.getElementById('aviatorBtn');
            let multText = document.getElementById('multiplierText');
            let bet = parseFloat(document.getElementById('aviatorBetAmount').value);

            if(!isFlying) {
                isFlying = true;
                btn.innerText = "Cash Out (ወጣሁ)";
                btn.className = "w-full py-3 bg-orange-500 hover:bg-orange-400 font-bold text-lg rounded-xl transition shadow-lg";

                currentMult = 1.00;
                multText.style.color = "white";

                flightInterval = setInterval(() => {
                    currentMult += 0.02;
                    multText.innerText = currentMult.toFixed(2) + "x";
                }, 80);

            } else {
                clearInterval(flightInterval);
                isFlying = false;

                try {
                    let response = await fetch(`${API_URL}/aviator/play`, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ bet: bet, cashout: currentMult })
                    });
                    let data = await response.json();

                    if(data.won) {
                        multText.style.color = "#4ade80";
                        multText.innerText = `WIN ${data.win_amount} ብር!`;
                        alert(`እንኳን ደስ አለዎት! በ ${currentMult.toFixed(2)}x ወጥተው ${data.win_amount} ብር አሸንፈዋል!`);
                    } else {
                        multText.style.color = "#ef4444";
                        multText.innerText = `CRASHED @ ${data.crash_point}x`;
                        alert(`አውሮፕላኗ በ ${data.crash_point}x ላይ ተከሰከሰች! ተሸንፈዋል።`);
                    }

                    document.getElementById('balance').innerText = data.new_balance.toFixed(2);
                    btn.innerText = "መወራረድ (Bet)";
                    btn.className = "w-full py-3 bg-green-600 hover:bg-green-500 font-bold text-lg rounded-xl transition shadow-lg";
                } catch(e) { alert("የውጤት ችግር አጋጥሟል!"); }
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/balance', methods=['GET'])
def get_balance():
    return jsonify({"balance": user_data["balance"]})

@app.route('/api/aviator/play', methods=['POST'])
def aviator_play():
    data = request.json
    bet_amount = float(data.get('bet', 0))
    cashout_mult = float(data.get('cashout', 0))

    if bet_amount > user_data["balance"] or bet_amount <= 0:
        return jsonify({"status": "error", "message": "በቂ ብር የለዎትም!"}), 400

    user_data["balance"] -= bet_amount

    if random.randint(1, 100) <= 5:
        crash_point = 1.00
    else:
        crash_point = round(random.uniform(1.01, 15.00), 2)

    won = False
    win_amount = 0

    if cashout_mult > 0 and cashout_mult <= crash_point:
        won = True
        win_amount = round(bet_amount * cashout_mult, 2)
        user_data["balance"] += win_amount

    return jsonify({
        "crash_point": crash_point,
        "won": won,
        "win_amount": win_amount,
        "new_balance": round(user_data["balance"], 2)
    })

@app.route('/api/keno/play', methods=['POST'])
def keno_play():
    data = request.json
    bet_amount = float(data.get('bet', 0))
    user_numbers = data.get('numbers', [])

    if bet_amount > user_data["balance"] or bet_amount <= 0:
        return jsonify({"status": "error", "message": "በቂ ብር የለዎትም!"}), 400

    if len(user_numbers) == 0 or len(user_numbers) > 10:
        return jsonify({"status": "error", "message": "እባክዎን ከ 1 እስከ 10 ቁጥሮችን ይምረጡ!"}), 400

    user_data["balance"] -= bet_amount

    drawn_numbers = random.sample(range(1, 41), 10)
    matched_numbers = list(set(user_numbers).intersection(drawn_numbers))
    match_count = len(matched_numbers)

    multipliers = {0: 0, 1: 0, 2: 1.5, 3: 3.0, 4: 5.0, 5: 10.0, 6: 25.0, 7: 50.0, 8: 100.0, 9: 200.0, 10: 500.0}
    multiplier = multipliers.get(match_count, 0)
    
    win_amount = round(bet_amount * multiplier, 2)
    user_data["balance"] += win_amount

    return jsonify({
        "drawn_numbers": drawn_numbers,
        "matched_numbers": matched_numbers,
        "match_count": match_count,
        "win_amount": win_amount,
        "new_balance": round(user_data["balance"], 2)
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
