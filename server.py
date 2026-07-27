#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║  Ebenezer Worship Centre — Taifa                            ║
║  Church Management System — Cloud Server                    ║
║  The Church of Pentecost · Taifa District · Greater Accra   ║
║                                                              ║
║  Zero external dependencies — Pure Python 3 stdlib only     ║
║  Works on:  Railway · Render · VPS · localhost              ║
╚══════════════════════════════════════════════════════════════╝
"""
import os, sys, json, sqlite3, hashlib, hmac, base64, uuid, re, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path
from datetime import datetime

# ─── CONFIGURATION ────────────────────────────────────────────────────
PORT       = int(os.environ.get("PORT", 3000))
HOST       = "0.0.0.0"
SECRET_KEY = os.environ.get("EWC_SECRET", "EWC_TAIFA_COP_2024_CHANGE_THIS_IN_PRODUCTION")
# Data dir: /data for Railway/Render (persistent volume), else current dir
_DATA_DIR  = Path("/data") if Path("/data").exists() else Path(__file__).parent
DB_PATH    = str(_DATA_DIR / "ewc_database.db")
STATIC_DIR = Path(__file__).parent.resolve()

# ─── DATABASE ─────────────────────────────────────────────────────────
def db_conn():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("PRAGMA foreign_keys=ON")
    return c

def db_init():
    c = db_conn()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fn TEXT DEFAULT '', ln TEXT DEFAULT '',
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        ph TEXT DEFAULT '', em TEXT DEFAULT '',
        active INTEGER DEFAULT 1,
        created TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fn TEXT DEFAULT '', ln TEXT DEFAULT '',
        ge TEXT DEFAULT 'Male', dob TEXT DEFAULT '',
        ph TEXT DEFAULT '', ph2 TEXT DEFAULT '',
        em TEXT DEFAULT '', oc TEXT DEFAULT '',
        emp TEXT DEFAULT '', mar TEXT DEFAULT 'Single',
        nch INTEGER DEFAULT 0, adr TEXT DEFAULT '',
        gps TEXT DEFAULT '', ht TEXT DEFAULT '',
        cel TEXT DEFAULT 'None', min TEXT DEFAULT 'None',
        rank TEXT DEFAULT 'Member', hgb TEXT DEFAULT 'No',
        jd TEXT DEFAULT '', hj TEXT DEFAULT 'Baptism',
        bap TEXT DEFAULT '', st TEXT DEFAULT 'active',
        ecn TEXT DEFAULT '', ecp TEXT DEFAULT '',
        ecr TEXT DEFAULT '', nid TEXT DEFAULT '',
        nokN TEXT DEFAULT '', nokP TEXT DEFAULT '',
        nokR TEXT DEFAULT '', nts TEXT DEFAULT '',
        photo TEXT DEFAULT '',
        registration_source TEXT DEFAULT 'admin',
        created TEXT DEFAULT (datetime('now')),
        updated TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS tithes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dt TEXT DEFAULT '', mid INTEGER DEFAULT 0,
        cat TEXT DEFAULT '', amt REAL DEFAULT 0,
        mth TEXT DEFAULT 'Cash', rcv TEXT DEFAULT '',
        ref TEXT DEFAULT '', not_ TEXT DEFAULT '',
        created TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dt TEXT DEFAULT '', cat TEXT DEFAULT '',
        desc TEXT DEFAULT '', amt REAL DEFAULT 0,
        paid TEXT DEFAULT '', vph TEXT DEFAULT '',
        memId INTEGER DEFAULT 0, mth TEXT DEFAULT 'Cash',
        appr TEXT DEFAULT '', rec TEXT DEFAULT '',
        fund TEXT DEFAULT 'General Fund', budg REAL DEFAULT 0,
        nts TEXT DEFAULT '',
        created TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT DEFAULT '', service TEXT DEFAULT '',
        saved TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS attendance_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        att_id INTEGER, member_id INTEGER, status TEXT DEFAULT ''
    );
    CREATE TABLE IF NOT EXISTS converts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fn TEXT DEFAULT '', ln TEXT DEFAULT '',
        ge TEXT DEFAULT '', dt TEXT DEFAULT '',
        ph TEXT DEFAULT '', age INTEGER DEFAULT 0,
        inv TEXT DEFAULT '', how TEXT DEFAULT '',
        adr TEXT DEFAULT '', prev TEXT DEFAULT '',
        fuby TEXT DEFAULT '', fust TEXT DEFAULT 'Pending',
        cell TEXT DEFAULT 'Not assigned',
        bap TEXT DEFAULT 'No', bapdx TEXT DEFAULT '',
        nts TEXT DEFAULT '',
        created TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS beneficiaries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nm TEXT DEFAULT '', ph TEXT DEFAULT '',
        dt TEXT DEFAULT '', type TEXT DEFAULT '',
        need TEXT DEFAULT '', supp TEXT DEFAULT '',
        amt REAL DEFAULT 0, memId INTEGER DEFAULT 0,
        rel TEXT DEFAULT '', appr TEXT DEFAULT '',
        st TEXT DEFAULT 'Pending', nts TEXT DEFAULT '',
        created TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT DEFAULT '', dt TEXT DEFAULT '',
        end_dt TEXT DEFAULT '', time_ TEXT DEFAULT '',
        ven TEXT DEFAULT '', cat TEXT DEFAULT '',
        org TEXT DEFAULT '', desc TEXT DEFAULT '',
        budg REAL DEFAULT 0, exp INTEGER DEFAULT 0,
        created TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS prayer_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mid INTEGER DEFAULT 0, dt TEXT DEFAULT '',
        req TEXT DEFAULT '', cat TEXT DEFAULT '',
        st TEXT DEFAULT 'Open', upd TEXT DEFAULT '',
        created TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS weekly_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT UNIQUE NOT NULL DEFAULT '',
        svcType TEXT DEFAULT '', preacher TEXT DEFAULT '',
        men INTEGER DEFAULT 0, women INTEGER DEFAULT 0,
        children INTEGER DEFAULT 0, youth INTEGER DEFAULT 0,
        visitors INTEGER DEFAULT 0, offering REAL DEFAULT 0,
        souls INTEGER DEFAULT 0, hgb INTEGER DEFAULT 0,
        waterBap INTEGER DEFAULT 0, lordSupper INTEGER DEFAULT 0,
        followup INTEGER DEFAULT 0, bibleRead INTEGER DEFAULT 0,
        bibleClass INTEGER DEFAULT 0, bibleAtt INTEGER DEFAULT 0,
        cell1 INTEGER DEFAULT 0, cell2 INTEGER DEFAULT 0,
        cell3 INTEGER DEFAULT 0, cellMtg INTEGER DEFAULT 0,
        cellSouls INTEGER DEFAULT 0, prayerMtg INTEGER DEFAULT 0,
        outreach INTEGER DEFAULT 0, outSouls INTEGER DEFAULT 0,
        outAtt INTEGER DEFAULT 0, tracts INTEGER DEFAULT 0,
        minMtg INTEGER DEFAULT 0, minSouls INTEGER DEFAULT 0,
        tithe REAL DEFAULT 0, welfare REAL DEFAULT 0,
        health REAL DEFAULT 0, educ REAL DEFAULT 0,
        donate REAL DEFAULT 0, schol REAL DEFAULT 0,
        notes TEXT DEFAULT '',
        created TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS transfers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT DEFAULT '', type TEXT DEFAULT '',
        memId INTEGER DEFAULT 0, name TEXT DEFAULT '',
        ge TEXT DEFAULT '', ph TEXT DEFAULT '',
        rank TEXT DEFAULT '', from_assembly TEXT DEFAULT '',
        to_assembly TEXT DEFAULT '', dist TEXT DEFAULT '',
        area TEXT DEFAULT '', reason TEXT DEFAULT '',
        recBy TEXT DEFAULT '', st TEXT DEFAULT 'Pending',
        nts TEXT DEFAULT '',
        created TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS outreach (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT DEFAULT '', loc TEXT DEFAULT '',
        type TEXT DEFAULT '', led TEXT DEFAULT '',
        team INTEGER DEFAULT 0, att INTEGER DEFAULT 0,
        souls INTEGER DEFAULT 0, hgb INTEGER DEFAULT 0,
        tracts INTEGER DEFAULT 0, followup TEXT DEFAULT '',
        nts TEXT DEFAULT '',
        created TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS ministry_meetings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT DEFAULT '', min TEXT DEFAULT '',
        type TEXT DEFAULT '', fac TEXT DEFAULT '',
        att INTEGER DEFAULT 0, souls INTEGER DEFAULT 0,
        hgb INTEGER DEFAULT 0, dur REAL DEFAULT 0,
        nts TEXT DEFAULT '',
        created TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS holy_ghost_baptisms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT DEFAULT '', memId INTEGER DEFAULT 0,
        name TEXT DEFAULT '', ge TEXT DEFAULT '',
        age INTEGER DEFAULT 0, svc TEXT DEFAULT '',
        minister TEXT DEFAULT '', conv TEXT DEFAULT '',
        nts TEXT DEFAULT '',
        created TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS special_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT DEFAULT '', cat TEXT DEFAULT '',
        title TEXT DEFAULT '', desc TEXT DEFAULT '',
        person TEXT DEFAULT '', wit TEXT DEFAULT '',
        created TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS scholarships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT DEFAULT '', type TEXT DEFAULT '',
        name TEXT DEFAULT '', memId INTEGER DEFAULT 0,
        inst TEXT DEFAULT '', level TEXT DEFAULT '',
        amt REAL DEFAULT 0, period TEXT DEFAULT '',
        appr TEXT DEFAULT '', st TEXT DEFAULT 'Pending',
        nts TEXT DEFAULT '',
        created TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS member_registrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token TEXT DEFAULT '',
        fn TEXT DEFAULT '', ln TEXT DEFAULT '',
        ge TEXT DEFAULT '', dob TEXT DEFAULT '',
        ph TEXT DEFAULT '', ph2 TEXT DEFAULT '',
        em TEXT DEFAULT '', oc TEXT DEFAULT '',
        emp TEXT DEFAULT '', mar TEXT DEFAULT '',
        nch INTEGER DEFAULT 0, adr TEXT DEFAULT '',
        gps TEXT DEFAULT '', ht TEXT DEFAULT '',
        rank TEXT DEFAULT 'Member',
        nokN TEXT DEFAULT '', nokP TEXT DEFAULT '',
        nokR TEXT DEFAULT '', nts TEXT DEFAULT '',
        photo TEXT DEFAULT '', status TEXT DEFAULT 'pending',
        submitted TEXT DEFAULT (datetime('now')),
        reviewed TEXT DEFAULT '', reviewed_by TEXT DEFAULT ''
    );
    CREATE TABLE IF NOT EXISTS church_config (
        key TEXT PRIMARY KEY, value TEXT DEFAULT ''
    );
    INSERT OR IGNORE INTO church_config VALUES
        ('name','Ebenezer Worship Centre - Taifa'),
        ('district','Taifa District'),
        ('area','Greater Accra Area'),
        ('pastor',''), ('elder',''), ('phone',''),
        ('email',''), ('addr',''), ('svcTime','8:00 AM'),
        ('adminKey','COP2024TAIFA'),
        ('c1l',''), ('c1d','Tuesday'),
        ('c2l',''), ('c2d','Wednesday'),
        ('c3l',''), ('c3d','Thursday');
    """)
    c.commit()
    # Create default admin
    row = c.execute("SELECT id FROM users WHERE role='admin'").fetchone()
    if not row:
        pw = _hash_pw("admin123")
        c.execute("INSERT OR IGNORE INTO users(fn,ln,username,password,role) VALUES(?,?,?,?,?)",
                  ("Admin","User","admin",pw,"admin"))
        c.commit()
        print("  ✅ Admin created: username=admin  password=admin123")
    c.close()

# ─── AUTH HELPERS ──────────────────────────────────────────────────────
def _hash_pw(pw):
    salt = uuid.uuid4().hex
    h = hashlib.pbkdf2_hmac('sha256', pw.encode(), salt.encode(), 100000)
    return f"{salt}:{h.hex()}"

def _check_pw(pw, stored):
    try:
        if ':' in stored:
            salt, h = stored.split(':', 1)
            return hmac.compare_digest(
                h, hashlib.pbkdf2_hmac('sha256', pw.encode(), salt.encode(), 100000).hex())
        # legacy base64 fallback
        return hmac.compare_digest(base64.b64encode(pw.encode()).decode(), stored)
    except:
        return False

def _make_token(user):
    payload = json.dumps({
        "id": user["id"], "fn": user["fn"],
        "username": user["username"], "role": user["role"],
        "exp": int(time.time()) + 30 * 86400
    })
    b64 = base64.b64encode(payload.encode()).decode()
    sig = hmac.new(SECRET_KEY.encode(), b64.encode(), hashlib.sha256).hexdigest()
    return f"{b64}.{sig}"

def _verify_token(token):
    try:
        b64, sig = token.rsplit('.', 1)
        expected = hmac.new(SECRET_KEY.encode(), b64.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return None
        payload = json.loads(base64.b64decode(b64).decode())
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except:
        return None

# ─── GENERIC DB HELPERS ────────────────────────────────────────────────
ALLOWED_TABLES = {
    "members", "tithes", "expenses", "converts", "beneficiaries",
    "events", "prayer_requests", "weekly_records", "transfers",
    "outreach", "ministry_meetings", "holy_ghost_baptisms",
    "special_events", "scholarships", "users"
}

def db_all(table, order="id DESC"):
    c = db_conn()
    rows = [dict(r) for r in c.execute(f"SELECT * FROM {table} ORDER BY {order}").fetchall()]
    c.close()
    return rows

def db_insert(table, data):
    data = {k: v for k, v in data.items() if k != "id"}
    if not data:
        return None
    cols = list(data.keys())
    c = db_conn()
    cur = c.execute(
        f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join(['?']*len(cols))})",
        [data[k] for k in cols])
    c.commit()
    rid = cur.lastrowid
    c.close()
    return rid

def db_update(table, rid, data):
    data = {k: v for k, v in data.items() if k != "id"}
    if not data:
        return
    cols = list(data.keys())
    c = db_conn()
    c.execute(
        f"UPDATE {table} SET {','.join(c+'=?' for c in cols)} WHERE id=?",
        [data[k] for k in cols] + [rid])
    c.commit()
    c.close()

def db_delete(table, rid):
    c = db_conn()
    c.execute(f"DELETE FROM {table} WHERE id=?", [rid])
    c.commit()
    c.close()

# ─── HTTP REQUEST HANDLER ──────────────────────────────────────────────
class EWCHandler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        ts = datetime.now().strftime('%H:%M:%S')
        msg = (args[0] if args else '')[:70]
        if '/api/' in msg or msg.startswith('GET / ') or msg.startswith('GET /r'):
            print(f"  [{ts}] {msg}")

    # ── Response helpers ─────────────────────────────────────────────
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin",  "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type,Authorization")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")

    def send_json(self, code, data):
        body = json.dumps(data, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def send_ok(self, data=None):
        self.send_json(200, data if data is not None else {"success": True})

    def send_err(self, code, msg):
        self.send_json(code, {"error": msg})

    def read_body(self):
        n = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(n)) if n else {}

    def get_user(self):
        tok = self.headers.get("Authorization", "").replace("Bearer ", "").strip()
        return _verify_token(tok) if tok else None

    def serve_file(self, name):
        p = STATIC_DIR / name
        if not p.exists():
            self.send_err(404, f"File not found: {name}")
            return
        ext_map = {
            ".html": "text/html; charset=utf-8",
            ".js":   "application/javascript",
            ".css":  "text/css",
            ".json": "application/json",
            ".png":  "image/png",
            ".jpg":  "image/jpeg",
            ".ico":  "image/x-icon",
            ".txt":  "text/plain"
        }
        ct = ext_map.get(p.suffix, "application/octet-stream")
        data = p.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ct)
        self.send_header("Content-Length", str(len(data)))
        self._cors()
        self.end_headers()
        self.wfile.write(data)

    # ── OPTIONS (CORS preflight) ─────────────────────────────────────
    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.send_header("Content-Length", "0")
        self.end_headers()

    # ── GET ──────────────────────────────────────────────────────────
    def do_GET(self):
        path = urlparse(self.path).path.rstrip("/") or "/"

        # Static files
        if path == "/" or path == "":
            return self.serve_file("EbenezerWC_CMS.html")
        if path in ("/register", "/register.html"):
            return self.serve_file("register.html")
        if not path.startswith("/api"):
            return self.serve_file(path.lstrip("/"))

        # API — require auth
        user = self.get_user()
        if not user:
            return self.send_err(401, "Unauthorised — please log in")

        # /api/dashboard
        if path == "/api/dashboard":
            c = db_conn()
            mem  = c.execute("SELECT COUNT(*) FROM members WHERE st='active'").fetchone()[0]
            inc  = c.execute("SELECT COALESCE(SUM(amt),0) FROM tithes").fetchone()[0]
            exp  = c.execute("SELECT COALESCE(SUM(amt),0) FROM expenses").fetchone()[0]
            souls= c.execute("SELECT COALESCE(SUM(souls+outSouls+minSouls+cellSouls),0) FROM weekly_records").fetchone()[0]
            hgb  = c.execute("SELECT COUNT(*) FROM holy_ghost_baptisms").fetchone()[0]
            pend = c.execute("SELECT COUNT(*) FROM member_registrations WHERE status='pending'").fetchone()[0]
            bday = c.execute("""SELECT COUNT(*) FROM members WHERE
                strftime('%m-%d',dob) BETWEEN
                strftime('%m-%d','now') AND
                strftime('%m-%d','now','+7 days')""").fetchone()[0]
            c.close()
            return self.send_ok({
                "members":mem, "income":float(inc), "expenses":float(exp),
                "balance":float(inc)-float(exp), "souls":int(souls or 0),
                "hgb":int(hgb), "pending":int(pend), "birthdays":int(bday)
            })

        # /api/config
        if path == "/api/config":
            c = db_conn()
            cfg = {r["key"]: r["value"] for r in c.execute("SELECT key,value FROM church_config").fetchall()}
            c.close()
            return self.send_ok(cfg)

        # /api/attendance
        if path == "/api/attendance":
            c = db_conn()
            sessions = [dict(r) for r in c.execute("SELECT * FROM attendance ORDER BY date DESC").fetchall()]
            recs     = c.execute("SELECT * FROM attendance_records").fetchall()
            c.close()
            rec_map = {}
            for r in recs:
                rec_map.setdefault(r["att_id"], {})[str(r["member_id"])] = r["status"]
            for s in sessions:
                s["records"] = rec_map.get(s["id"], {})
            return self.send_ok(sessions)

        # /api/pending-registrations
        if path == "/api/pending-registrations":
            c = db_conn()
            rows = [dict(r) for r in c.execute(
                "SELECT * FROM member_registrations WHERE status='pending' ORDER BY submitted DESC"
            ).fetchall()]
            c.close()
            return self.send_ok(rows)

        # /api/<table>
        seg = path.replace("/api/", "").split("/")[0]
        if seg in ALLOWED_TABLES:
            order_map = {
                "tithes":"dt DESC","expenses":"dt DESC",
                "weekly_records":"date DESC","outreach":"date DESC","transfers":"date DESC"
            }
            return self.send_ok(db_all(seg, order_map.get(seg, "id DESC")))

        self.send_err(404, "Not found")

    # ── POST ─────────────────────────────────────────────────────────
    def do_POST(self):
        path = urlparse(self.path).path.rstrip("/")
        data = self.read_body()

        # ── Public endpoints (no auth) ────────────────────────────
        if path == "/api/login":
            c = db_conn()
            u = c.execute("SELECT * FROM users WHERE username=? AND active=1",
                          [data.get("username","")]).fetchone()
            c.close()
            if not u or not _check_pw(data.get("password",""), u["password"]):
                return self.send_err(401, "Invalid username or password")
            token = _make_token(dict(u))
            return self.send_ok({"token": token, "user": {
                "id":u["id"],"fn":u["fn"],"ln":u["ln"],
                "username":u["username"],"role":u["role"]
            }})

        if path == "/api/register":
            fn,ln = data.get("fn","").strip(), data.get("ln","").strip()
            uname = data.get("username","").strip()
            pw    = data.get("password","")
            if not all([fn,ln,uname,pw]):
                return self.send_err(400, "Missing required fields")
            if len(pw) < 6:
                return self.send_err(400, "Password must be at least 6 characters")
            c = db_conn()
            cfg = c.execute("SELECT value FROM church_config WHERE key='adminKey'").fetchone()
            akey = cfg["value"] if cfg else "COP2024TAIFA"
            ex   = c.execute("SELECT id FROM users WHERE username=?", [uname]).fetchone()
            c.close()
            if ex:
                return self.send_err(409, "Username already taken")
            if data.get("role") == "admin" and data.get("adminKey","") != akey:
                return self.send_err(403, "Invalid admin registration key")
            rid = db_insert("users", {
                "fn":fn,"ln":ln,"username":uname,
                "password":_hash_pw(pw),
                "role":data.get("role","user"),
                "ph":data.get("ph",""),"em":data.get("em","")
            })
            return self.send_ok({"success":True,"id":rid})

        if path == "/api/self-register":
            token = data.get("token","")
            c = db_conn()
            v = c.execute("SELECT value FROM church_config WHERE key=?",
                          ["reg_token_"+token]).fetchone()
            c.close()
            if not v or v["value"] != "active":
                return self.send_err(403, "Invalid or expired registration link")
            fields = ["fn","ln","ge","dob","ph","ph2","em","oc","emp","mar","nch",
                      "adr","gps","ht","rank","nokN","nokP","nokR","nts","photo"]
            row = {f: data.get(f,"") for f in fields}
            row.update({"token":token,"status":"pending"})
            db_insert("member_registrations", row)
            return self.send_ok({"success":True,"message":"Registration submitted!"})

        # ── Authenticated endpoints ───────────────────────────────
        user = self.get_user()
        if not user:
            return self.send_err(401, "Unauthorised — please log in")

        # Registration link generator
        if path == "/api/registration-link":
            token = uuid.uuid4().hex
            c = db_conn()
            c.execute("INSERT OR REPLACE INTO church_config(key,value) VALUES(?,?)",
                      ["reg_token_"+token,"active"])
            c.commit(); c.close()
            base = f"https://{self.headers.get('Host','localhost')}"
            link = f"{base}/register.html?token={token}"
            msg  = (f"Dear church member,\n\nPlease register your membership details "
                    f"with Ebenezer Worship Centre — Taifa using this link:\n\n{link}\n\n"
                    f"Fill in all details carefully on your phone or computer.\n\nGod bless you!")
            return self.send_ok({"link":link,"token":token,"message":msg})

        # Approve pending registration
        m = re.match(r'^/api/approve-registration/(\d+)$', path)
        if m:
            rid = int(m.group(1))
            c = db_conn()
            reg = c.execute("SELECT * FROM member_registrations WHERE id=?", [rid]).fetchone()
            c.close()
            if not reg:
                return self.send_err(404, "Registration not found")
            reg = dict(reg)
            fields = ["fn","ln","ge","dob","ph","ph2","em","oc","emp","mar","nch",
                      "adr","gps","ht","rank","nokN","nokP","nokR","nts","photo"]
            member = {f: reg.get(f,"") for f in fields}
            member.update({
                "jd": datetime.now().strftime("%Y-%m-%d"),
                "hj":"New birth","st":"active",
                "registration_source":"self_registration"
            })
            db_insert("members", member)
            c = db_conn()
            c.execute("UPDATE member_registrations SET status='approved',"
                      "reviewed=datetime('now'),reviewed_by=? WHERE id=?",
                      [user.get("fn","admin"), rid])
            c.commit(); c.close()
            return self.send_ok()

        # Reject registration
        m = re.match(r'^/api/reject-registration/(\d+)$', path)
        if m:
            c = db_conn()
            c.execute("UPDATE member_registrations SET status='rejected',"
                      "reviewed=datetime('now'),reviewed_by=? WHERE id=?",
                      [user.get("fn","admin"), int(m.group(1))])
            c.commit(); c.close()
            return self.send_ok()

        # Attendance save
        if path == "/api/attendance":
            date_, svc = data.get("date",""), data.get("service","")
            records    = data.get("records",{})
            c = db_conn()
            ex = c.execute("SELECT id FROM attendance WHERE date=? AND service=?",
                           [date_,svc]).fetchone()
            if ex:
                att_id = ex["id"]
                c.execute("DELETE FROM attendance_records WHERE att_id=?", [att_id])
            else:
                cur    = c.execute("INSERT INTO attendance(date,service) VALUES(?,?)",[date_,svc])
                att_id = cur.lastrowid
            for mid,status in records.items():
                c.execute("INSERT INTO attendance_records(att_id,member_id,status) VALUES(?,?,?)",
                          [att_id,mid,status])
            c.commit(); c.close()
            return self.send_ok({"success":True,"id":att_id})

        # Weekly records — upsert on duplicate date
        if path == "/api/weekly_records":
            date_ = data.get("date","")
            data.pop("id",None)
            if date_:
                c = db_conn()
                ex = c.execute("SELECT id FROM weekly_records WHERE date=?",[date_]).fetchone()
                c.close()
                if ex:
                    db_update("weekly_records", ex["id"], data)
                    return self.send_ok({"success":True,"id":ex["id"]})
            rid = db_insert("weekly_records", data)
            return self.send_ok({"success":True,"id":rid})

        # Generic table insert
        seg = path.replace("/api/","").split("/")[0]
        if seg in ALLOWED_TABLES:
            data.pop("id",None)
            rid = db_insert(seg, data)
            return self.send_ok({"success":True,"id":rid})

        self.send_err(404, "Not found")

    # ── PUT ──────────────────────────────────────────────────────────
    def do_PUT(self):
        path = urlparse(self.path).path.rstrip("/")
        user = self.get_user()
        if not user:
            return self.send_err(401, "Unauthorised")
        data = self.read_body()

        # Config update
        if path == "/api/config":
            c = db_conn()
            for k,v in data.items():
                c.execute("INSERT OR REPLACE INTO church_config(key,value) VALUES(?,?)",[k,v])
            c.commit(); c.close()
            return self.send_ok()

        # Generic table update
        m = re.match(r'^/api/(\w+)/(\d+)$', path)
        if m and m.group(1) in ALLOWED_TABLES:
            data.pop("id",None)
            db_update(m.group(1), int(m.group(2)), data)
            return self.send_ok()

        self.send_err(404, "Not found")

    # ── DELETE ───────────────────────────────────────────────────────
    def do_DELETE(self):
        path = urlparse(self.path).path.rstrip("/")
        user = self.get_user()
        if not user:
            return self.send_err(401, "Unauthorised")

        m = re.match(r'^/api/(\w+)/(\d+)$', path)
        if m and m.group(1) in ALLOWED_TABLES:
            db_delete(m.group(1), int(m.group(2)))
            return self.send_ok()

        self.send_err(404, "Not found")


# ─── ENTRY POINT ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║  Ebenezer Worship Centre — Taifa CMS Server                 ║
║  The Church of Pentecost · Taifa District                   ║
╚══════════════════════════════════════════════════════════════╝""")

    print(f"\n  📂 Database: {DB_PATH}")
    db_init()

    server = HTTPServer((HOST, PORT), EWCHandler)
    print(f"""
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📱  Local:   http://localhost:{PORT}
  🌐  Network: http://0.0.0.0:{PORT}
  🔑  Login:   admin / admin123
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅  Server running — press Ctrl+C to stop
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  🙏 Server stopped. Database saved. Goodbye!")
        server.server_close()
