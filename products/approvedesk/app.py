"""ApproveDesk VF-01 — portable local MVP, Python standard library only.

Security scope: local single-node staging. No production deployment or canonical
IMPERIAL Core Approval Gateway/Audit Ledger integration is claimed.
"""
import base64
from datetime import datetime, timezone
import hashlib
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import secrets
import sqlite3
from threading import RLock
from urllib.parse import urlsplit

LOCK = RLock()
MAX_BODY = 40_960
MAX_TEXT = 24_576
EMAIL = re.compile(r"^[^@\s]{1,80}@[^@\s]{1,120}$")
SAFE_FILE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}\.txt$")
DB_PATH = os.getenv("APPROVEDESK_DB", "approvedesk.local.sqlite3")
SITE_PATH = Path(__file__).with_name("index.html")

def utc():
    return datetime.now(timezone.utc).isoformat()

def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def connect():
    db = sqlite3.connect(DB_PATH, timeout=8, isolation_level=None)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    db.execute("PRAGMA busy_timeout = 8000")
    return db

def initialize():
    with LOCK, connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE,
          pw_hash TEXT NOT NULL, salt TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS sessions (
          token_hash TEXT PRIMARY KEY, user_id INTEGER NOT NULL,
          csrf TEXT NOT NULL, created TEXT NOT NULL,
          FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS projects (
          id INTEGER PRIMARY KEY, name TEXT NOT NULL, owner_id INTEGER NOT NULL,
          created TEXT NOT NULL, FOREIGN KEY(owner_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS reviewers (
          project_id INTEGER NOT NULL, user_id INTEGER NOT NULL,
          PRIMARY KEY(project_id,user_id),
          FOREIGN KEY(project_id) REFERENCES projects(id),
          FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS versions (
          id INTEGER PRIMARY KEY, project_id INTEGER NOT NULL, number INTEGER NOT NULL,
          filename TEXT NOT NULL, content TEXT NOT NULL, sha256 TEXT NOT NULL,
          created TEXT NOT NULL, UNIQUE(project_id,number),
          FOREIGN KEY(project_id) REFERENCES projects(id)
        );
        CREATE TABLE IF NOT EXISTS comments (
          id INTEGER PRIMARY KEY, version_id INTEGER NOT NULL, reviewer_id INTEGER NOT NULL,
          text TEXT NOT NULL, created TEXT NOT NULL,
          FOREIGN KEY(version_id) REFERENCES versions(id),
          FOREIGN KEY(reviewer_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS approvals (
          id INTEGER PRIMARY KEY, version_id INTEGER NOT NULL, reviewer_id INTEGER NOT NULL,
          decision TEXT NOT NULL, created TEXT NOT NULL,
          UNIQUE(version_id,reviewer_id),
          FOREIGN KEY(version_id) REFERENCES versions(id),
          FOREIGN KEY(reviewer_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS audit (
          id INTEGER PRIMARY KEY, actor INTEGER NOT NULL, project_id INTEGER NOT NULL,
          action TEXT NOT NULL, details TEXT NOT NULL, created TEXT NOT NULL,
          prev_hash TEXT NOT NULL, event_hash TEXT NOT NULL
        );
        """)

def audit(db, actor, project, action, details):
    old = db.execute("SELECT event_hash FROM audit ORDER BY id DESC LIMIT 1").fetchone()
    prev = old["event_hash"] if old else "0" * 64
    record = json.dumps([actor,project,action,details,utc(),prev],separators=(",",":"))
    data = json.loads(record)
    db.execute("INSERT INTO audit(actor,project_id,action,details,created,prev_hash,event_hash) VALUES(?,?,?,?,?,?,?)",
               (actor,project,action,details,data[4],prev,digest(record)))

def serialize(row):
    return dict(row) if row is not None else None

class Application(BaseHTTPRequestHandler):
    server_version = "ApproveDeskLocal/0.1"
    def log_message(self, fmt, *args):
        # No raw authorization headers or uploaded bodies logged.
        return

    def reply(self, code, data, headers=None, content_type="application/json"):
        payload = json.dumps(data,ensure_ascii=False,separators=(",",":")).encode("utf-8") if content_type=="application/json" else data
        self.send_response(code)
        self.send_header("Content-Type", content_type+"; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'self'")
        for k,v in (headers or {}).items():self.send_header(k,v)
        self.end_headers()
        self.wfile.write(payload)

    def body(self):
        try:
            n=int(self.headers.get("Content-Length","0"))
            if n<1 or n>MAX_BODY:return None
            if self.headers.get("Content-Type","").split(";")[0].lower()!="application/json":return None
            obj=json.loads(self.rfile.read(n))
            return obj if isinstance(obj,dict) else None
        except (ValueError,UnicodeDecodeError,json.JSONDecodeError):
            return None

    def session(self,db,csrf=False):
        cookie=SimpleCookie()
        try:cookie.load(self.headers.get("Cookie",""))
        except Exception:return None
        if "ad_session" not in cookie:return None
        raw=cookie["ad_session"].value
        if len(raw)!=64 or not re.fullmatch(r"[0-9a-f]{64}",raw):return None
        row=db.execute("SELECT user_id,csrf FROM sessions WHERE token_hash=?",(digest(raw),)).fetchone()
        if not row:return None
        if csrf and not secrets.compare_digest(self.headers.get("X-CSRF-Token",""),row["csrf"]):return None
        return row

    def scope(self,db,project,user):
        return db.execute("""SELECT p.id,p.owner_id FROM projects p
           WHERE p.id=? AND (p.owner_id=? OR EXISTS
             (SELECT 1 FROM reviewers r WHERE r.project_id=p.id AND r.user_id=?))""",
             (project,user,user)).fetchone()

    def route(self):
        p=urlsplit(self.path)
        if p.query or p.fragment:return None
        return p.path

    def do_GET(self):
        path=self.route()
        if path=="/healthz":return self.reply(200,{"service":"approvedesk","stage":"LOCAL_MVP"})
        if path=="/":
            return self.reply(200,SITE_PATH.read_bytes(),content_type="text/html")
        if path=="/main.js":
            return self.reply(200,Path(__file__).with_name("main.js").read_bytes(),content_type="application/javascript")
        if path=="/style.css":
            return self.reply(200,Path(__file__).with_name("style.css").read_bytes(),content_type="text/css")
        with LOCK,connect() as db:
            auth=self.session(db)
            if not auth:return self.reply(401,{"error":"AUTH_REQUIRED"})
            user=auth["user_id"]
            if path=="/api/me":
                email=db.execute("SELECT email FROM users WHERE id=?",(user,)).fetchone()["email"]
                return self.reply(200,{"user_id":user,"email":email,"csrf":auth["csrf"]})
            if path=="/api/projects":
                rows=db.execute("""SELECT DISTINCT p.id,p.name,p.owner_id FROM projects p
                   LEFT JOIN reviewers r ON r.project_id=p.id
                   WHERE p.owner_id=? OR r.user_id=? ORDER BY p.id""",(user,user)).fetchall()
                return self.reply(200,{"projects":[serialize(x) for x in rows]})
            m=re.fullmatch(r"/api/projects/(\d+)(?:/(export))?",path or "")
            if m:
                pid=int(m.group(1));p=self.scope(db,pid,user)
                if not p:return self.reply(404,{"error":"NOT_FOUND"})
                if m.group(2)=="export" and p["owner_id"]!=user:return self.reply(403,{"error":"OWNER_REQUIRED"})
                vv=db.execute("SELECT id,number,filename,content,sha256 FROM versions WHERE project_id=? ORDER BY number",(pid,)).fetchall()
                versions=[]
                for v in vv:
                    row=serialize(v)
                    row["comments"]=[serialize(x) for x in db.execute(
                       "SELECT reviewer_id,text,created FROM comments WHERE version_id=?",(v["id"],)).fetchall()]
                    row["approvals"]=[serialize(x) for x in db.execute(
                       "SELECT reviewer_id,decision,created FROM approvals WHERE version_id=?",(v["id"],)).fetchall()]
                    versions.append(row)
                aud=[serialize(x) for x in db.execute("SELECT actor,action,details,created,prev_hash,event_hash FROM audit WHERE project_id=? ORDER BY id",(pid,)).fetchall()]
                if m.group(2)=="export":
                    return self.reply(200,{"schema":"approvedesk_export_v1","project":serialize(p),"versions":versions,"audit":aud})
                return self.reply(200,{"project":serialize(p),"versions":versions,
                  "reviewers":[x["user_id"] for x in db.execute("SELECT user_id FROM reviewers WHERE project_id=?",(pid,)).fetchall()],
                  "audit":aud})
            return self.reply(404,{"error":"NOT_FOUND"})

    def do_POST(self):
        path=self.route();data=self.body()
        if data is None:return self.reply(400,{"error":"INVALID_JSON_OR_LIMIT"})
        if path in ("/api/register","/api/login"):
            email=data.get("email");pwd=data.get("password")
            if not isinstance(email,str) or not EMAIL.fullmatch(email) or not isinstance(pwd,str) or not 12<=len(pwd)<=128:
                return self.reply(400,{"error":"INVALID_CREDENTIAL_FORMAT"})
            email=email.strip().lower()
            with LOCK,connect() as db:
                if path=="/api/register":
                    salt=secrets.token_hex(16)
                    hashed=hashlib.pbkdf2_hmac("sha256",pwd.encode(),bytes.fromhex(salt),260000).hex()
                    try:
                        with db:
                            db.execute("INSERT INTO users(email,pw_hash,salt) VALUES(?,?,?)",(email,hashed,salt))
                    except sqlite3.IntegrityError:return self.reply(409,{"error":"USER_EXISTS"})
                row=db.execute("SELECT * FROM users WHERE email=?",(email,)).fetchone()
                if not row:return self.reply(401,{"error":"INVALID_CREDENTIALS"})
                expected=hashlib.pbkdf2_hmac("sha256",pwd.encode(),bytes.fromhex(row["salt"]),260000).hex()
                if not secrets.compare_digest(expected,row["pw_hash"]):return self.reply(401,{"error":"INVALID_CREDENTIALS"})
                token=secrets.token_hex(32);csrf=secrets.token_hex(24)
                with db:
                    db.execute("INSERT INTO sessions(token_hash,user_id,csrf,created) VALUES(?,?,?,?)",
                               (digest(token),row["id"],csrf,utc()))
                secure="; Secure" if os.getenv("APPROVEDESK_SECURE_COOKIE")=="1" else ""
                return self.reply(200,{"user_id":row["id"],"csrf":csrf},
                   {"Set-Cookie":"ad_session="+token+"; Path=/; HttpOnly; SameSite=Strict"+secure})
        with LOCK,connect() as db:
            auth=self.session(db,csrf=True)
            if not auth:return self.reply(403,{"error":"AUTH_OR_CSRF_DENIED"})
            user=auth["user_id"]
            if path=="/api/logout":
                cookie=SimpleCookie()
                try:cookie.load(self.headers.get("Cookie",""))
                except Exception:pass
                if "ad_session" in cookie:
                    with db:db.execute("DELETE FROM sessions WHERE token_hash=?",(digest(cookie["ad_session"].value),))
                return self.reply(200,{"ok":True},{"Set-Cookie":"ad_session=; Max-Age=0; Path=/; HttpOnly; SameSite=Strict"})
            if path=="/api/projects":
                name=data.get("name")
                if not isinstance(name,str) or not 1<=len(name.strip())<=100:return self.reply(400,{"error":"INVALID_PROJECT_NAME"})
                with db:
                    cur=db.execute("INSERT INTO projects(name,owner_id,created) VALUES(?,?,?)",(name.strip(),user,utc()))
                    pid=cur.lastrowid
                    audit(db,user,pid,"CREATE_PROJECT",name.strip())
                return self.reply(201,{"project_id":pid})
            m=re.fullmatch(r"/api/projects/(\d+)/(reviewers|versions)",path or "")
            if m:
                pid=int(m.group(1));p=self.scope(db,pid,user)
                if not p:return self.reply(404,{"error":"NOT_FOUND"})
                if p["owner_id"]!=user:return self.reply(403,{"error":"OWNER_REQUIRED"})
                if m.group(2)=="reviewers":
                    email=data.get("email")
                    if not isinstance(email,str) or not EMAIL.fullmatch(email):return self.reply(400,{"error":"INVALID_EMAIL"})
                    target=db.execute("SELECT id FROM users WHERE email=?",(email.lower(),)).fetchone()
                    if not target or target["id"]==user:return self.reply(400,{"error":"REVIEWER_UNAVAILABLE"})
                    with db:
                        db.execute("INSERT OR IGNORE INTO reviewers(project_id,user_id) VALUES(?,?)",(pid,target["id"]))
                        audit(db,user,pid,"ADD_REVIEWER",str(target["id"]))
                    return self.reply(201,{"reviewer_id":target["id"]})
                filename=data.get("filename");content=data.get("content")
                if not isinstance(filename,str) or not SAFE_FILE.fullmatch(filename) or not isinstance(content,str) or not 1<=len(content.encode("utf-8"))<=MAX_TEXT:
                    return self.reply(400,{"error":"ONLY_SMALL_TEXT_FILES"})
                with db:
                    n=db.execute("SELECT COALESCE(MAX(number),0)+1 AS n FROM versions WHERE project_id=?",(pid,)).fetchone()["n"]
                    c=db.execute("INSERT INTO versions(project_id,number,filename,content,sha256,created) VALUES(?,?,?,?,?,?)",
                                 (pid,n,filename,content,digest(content),utc()))
                    audit(db,user,pid,"UPLOAD_VERSION",str(c.lastrowid))
                return self.reply(201,{"version_id":c.lastrowid,"number":n,"sha256":digest(content)})
            m=re.fullmatch(r"/api/versions/(\d+)/(comments|decisions)",path or "")
            if m:
                version=int(m.group(1))
                row=db.execute("""SELECT v.id,v.project_id FROM versions v
                   JOIN reviewers r ON r.project_id=v.project_id AND r.user_id=?
                   WHERE v.id=?""",(user,version)).fetchone()
                if not row:return self.reply(403,{"error":"REVIEWER_REQUIRED"})
                if m.group(2)=="comments":
                    txt=data.get("text")
                    if not isinstance(txt,str) or not 1<=len(txt.strip())<=1000:return self.reply(400,{"error":"INVALID_COMMENT"})
                    with db:
                        db.execute("INSERT INTO comments(version_id,reviewer_id,text,created) VALUES(?,?,?,?)",
                                   (version,user,txt.strip(),utc()))
                        audit(db,user,row["project_id"],"COMMENT",str(version))
                    return self.reply(201,{"ok":True})
                decision=data.get("decision")
                if decision not in ("APPROVE","REJECT"):return self.reply(400,{"error":"INVALID_DECISION"})
                with db:
                    try:
                        db.execute("INSERT INTO approvals(version_id,reviewer_id,decision,created) VALUES(?,?,?,?)",
                                   (version,user,decision,utc()))
                    except sqlite3.IntegrityError:return self.reply(409,{"error":"DECISION_ALREADY_RECORDED"})
                    audit(db,user,row["project_id"],"DECISION",str(version)+":"+decision)
                return self.reply(201,{"decision":decision})
            return self.reply(404,{"error":"NOT_FOUND"})

def serve(port=8787):
    initialize()
    host=os.getenv("APPROVEDESK_HOST","127.0.0.1")
    if host not in ("127.0.0.1","localhost","::1"):raise RuntimeError("LOCALHOST_ONLY_NOT_PRODUCTION")
    server=ThreadingHTTPServer((host,int(port)),Application)
    print("ApproveDesk LOCAL MVP ready at http://"+host+":"+str(port),flush=True)
    server.serve_forever()

if __name__=="__main__":
    serve(int(os.getenv("APPROVEDESK_PORT","8787")))
