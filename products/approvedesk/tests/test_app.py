import http.cookiejar, json, os, sys, unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from urllib.error import HTTPError
from urllib.request import HTTPCookieProcessor, Request, build_opener
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import app

class Client:
 def __init__(self,root):
  self.root=root;self.jar=http.cookiejar.CookieJar();self.opener=build_opener(HTTPCookieProcessor(self.jar));self.csrf=""
 def request(self,method,path,data=None,csrf=True):
  h={"Accept":"application/json"}
  if data is not None:
   h["Content-Type"]="application/json"
   if csrf:h["X-CSRF-Token"]=self.csrf
  r=Request(self.root+path,data=json.dumps(data).encode() if data is not None else None,headers=h,method=method)
  try:
   x=self.opener.open(r,timeout=6);code=x.status;payload=x.read()
  except HTTPError as e:code=e.code;payload=e.read()
  return code,json.loads(payload)
 def post(self,p,d,csrf=True):return self.request("POST",p,d,csrf)
 def get(self,p):return self.request("GET",p)
 def register(self,email):
  c,d=self.post("/api/register",{"email":email,"password":"Long_enough_password_2026!"})
  assert c==200,(c,d)
  self.csrf=d["csrf"];return d["user_id"]

class Integration(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.dir=TemporaryDirectory();app.DB_PATH=os.path.join(cls.dir.name,"unit.sqlite3");app.initialize()
  cls.server=ThreadingHTTPServer(("127.0.0.1",0),app.Application)
  cls.thread=Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
  cls.root="http://127.0.0.1:"+str(cls.server.server_port)
 @classmethod
 def tearDownClass(cls):
  cls.server.shutdown();cls.server.server_close();cls.thread.join();cls.dir.cleanup()
 def setUp(self):
  with app.LOCK,app.connect() as db:
   for table in ["audit","approvals","comments","versions","reviewers","projects","sessions","users"]:
    db.execute("DELETE FROM "+table)
  self.owner=Client(self.root);self.review=Client(self.root);self.other=Client(self.root)
  self.owner_id=self.owner.register("owner@example.test")
  self.review_id=self.review.register("reviewer@example.test")
  self.other.register("other@example.test")
 def new(self):
  c,d=self.owner.post("/api/projects",{"name":"Real project"})
  self.assertEqual(c,201);return d["project_id"]
 def test_full_review_and_audit_persist(self):
  p=self.new();url="/api/projects/"+str(p)
  self.assertEqual(self.owner.post(url+"/reviewers",{"email":"reviewer@example.test"})[0],201)
  c,version=self.owner.post(url+"/versions",{"filename":"rev.txt","content":"First revision"})
  self.assertEqual(c,201);v=str(version["version_id"])
  self.assertEqual(self.review.post("/api/versions/"+v+"/comments",{"text":"Please approve"})[0],201)
  self.assertEqual(self.review.post("/api/versions/"+v+"/decisions",{"decision":"APPROVE"})[0],201)
  c,data=self.owner.get(url)
  self.assertEqual(c,200);self.assertEqual(data["versions"][0]["approvals"][0]["decision"],"APPROVE")
  c,export=self.owner.get(url+"/export");self.assertEqual(c,200)
  self.assertEqual(len(export["audit"]),5)
  prev="0"*64
  for event in export["audit"]:
   self.assertEqual(event["prev_hash"],prev);prev=event["event_hash"]
  with app.connect() as db:
   self.assertEqual(db.execute("SELECT COUNT(*) FROM versions").fetchone()[0],1)
   self.assertEqual(db.execute("SELECT COUNT(*) FROM approvals").fetchone()[0],1)
 def test_cross_tenant_access(self):
  p=self.new();url="/api/projects/"+str(p)
  self.assertEqual(self.other.get(url)[0],404)
  self.assertEqual(self.other.get(url+"/export")[0],404)
  self.assertEqual(self.other.post(url+"/versions",{"filename":"a.txt","content":"data"})[0],404)
  self.assertEqual(self.review.get(url)[0],404)
  self.owner.post(url+"/reviewers",{"email":"reviewer@example.test"})
  self.assertEqual(self.review.get(url)[0],200)
  self.assertEqual(self.review.get(url+"/export")[0],403)
  self.assertEqual(self.review.post(url+"/versions",{"filename":"a.txt","content":"data"})[0],403)
 def test_csrf_and_missing_authority(self):
  p=self.new()
  self.assertEqual(self.owner.post("/api/projects",{"name":"blocked"},csrf=False)[0],403)
  self.assertEqual(Client(self.root).post("/api/projects",{"name":"blocked"})[0],403)
  self.assertEqual(self.owner.get("/api/projects/"+str(p)+"?wrong=yes")[0],404)
 def test_file_limit_and_version_sequence(self):
  p=self.new();url="/api/projects/"+str(p)+"/versions"
  for name in ("../bad.txt","evil.html","a.txt/../b.txt"):
   self.assertEqual(self.owner.post(url,{"filename":name,"content":"data"})[0],400)
  self.assertEqual(self.owner.post(url,{"filename":"ok.txt","content":"x"*30000})[0],400)
  self.assertEqual(self.owner.post(url,{"filename":"ok.txt","content":"v1"})[0],201)
  self.assertEqual(self.owner.post(url,{"filename":"ok.txt","content":"v2"})[0],201)
  _,data=self.owner.get("/api/projects/"+str(p))
  self.assertEqual([x["number"] for x in data["versions"]],[1,2])
 def test_duplicate_approval_and_owner_self_review(self):
  p=self.new();url="/api/projects/"+str(p)
  self.owner.post(url+"/reviewers",{"email":"reviewer@example.test"})
  _,v=self.owner.post(url+"/versions",{"filename":"x.txt","content":"v1"})
  dec="/api/versions/"+str(v["version_id"])+"/decisions"
  self.assertEqual(self.owner.post(dec,{"decision":"APPROVE"})[0],403)
  self.assertEqual(self.review.post(dec,{"decision":"APPROVE"})[0],201)
  self.assertEqual(self.review.post(dec,{"decision":"REJECT"})[0],409)
 def test_wrong_login_and_logout(self):
  x=Client(self.root)
  self.assertEqual(x.post("/api/login",{"email":"owner@example.test","password":"Wrong_password_2026!"})[0],401)
  self.assertEqual(self.owner.post("/api/logout",{})[0],200)
  self.assertEqual(self.owner.get("/api/projects")[0],401)
