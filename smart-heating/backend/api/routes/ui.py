from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def ui():
    return """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Smart Heating</title>

<style>
body { font-family: Arial; text-align: center; background: #111; color: white; }
button { width: 80%; padding: 20px; margin: 10px; font-size: 20px; border-radius: 10px; }
.on { background: green; }
.off { background: red; }
.mode { background: orange; }
</style>
</head>

<body>

<h1>🔥 Smart Heating</h1>

<input id="token" placeholder="API Token" style="width:80%;padding:10px"><br><br>

<button class="on" onclick="call('/heating/true')">Heating ON</button>
<button class="off" onclick="call('/heating/false')">Heating OFF</button>

<button class="mode" onclick="call('/manual/true')">Manual</button>
<button class="mode" onclick="call('/manual/false')">Auto</button>

<button onclick="getStatus()">Status</button>

<pre id="output"></pre>

<script>
function call(endpoint) {
    fetch(endpoint, {
        method: 'POST',
        headers: {
            'Authorization': 'Bearer ' + document.getElementById('token').value
        }
    })
    .then(r => r.json())
    .then(data => document.getElementById('output').innerText = JSON.stringify(data, null, 2))
}

function getStatus() {
    fetch('/status', {
        headers: {
            'Authorization': 'Bearer ' + document.getElementById('token').value
        }
    })
    .then(r => r.json())
    .then(data => document.getElementById('output').innerText = JSON.stringify(data, null, 2))
}
</script>

</body>
</html>
"""
