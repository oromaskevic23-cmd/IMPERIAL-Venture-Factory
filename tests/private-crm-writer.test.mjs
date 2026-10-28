import test from "node:test";
import assert from "node:assert/strict";
import {validateIssue,receiptSha256,SourceRejected,API,REPO} from "../supabase/functions/imperial-commercial-private-writer/core.mjs";
const consent = [
"- [x] I understand this issue is public and contains no secrets, personal data, payment details, or confidential material.",
"- [x] I understand any price, delivery and live system access require separate human agreement and explicit approval.",
];
function sample() {return {
 number:42, url:API+"/issues/42", html_url:"https://github.com/"+REPO+"/issues/42",
 state:"open", user:{login:"external-reviewer",type:"User"},labels:[],
 title:"[Audit request] webhook delay",body:[
 "What should be assessed?",
 "Public, non-confidential description of the problem",
 "Expected first deliverable",
 "Public issue privacy and scope confirmation", ...consent
 ].join("\n")
};}
test("eligible sanitized source reference only",()=>{
  assert.deepEqual(validateIssue(sample(),42),{number:42,source_ref:"github:"+REPO+"#42"});
});
test("rejected owner/system test",()=>{
 for(const mod of [
    x=>{x.user.login="oromaskevic23-cmd";},
    x=>{x.body+="\nSYSTEM TEST ONLY — NO CUSTOMER";},
    x=>{x.pull_request={url:"https://example.test"};},
 ]) {const x=sample();mod(x);assert.throws(()=>validateIssue(x,42),SourceRejected);}
});
test("source must be exact and open",()=>{
 for(const mod of [
    x=>{x.url="https://api.github.com/repos/attacker/repo/issues/42";},
    x=>{x.number=43;},
    x=>{x.state="closed";},
 ]) {const x=sample();mod(x);assert.throws(()=>validateIssue(x,42),SourceRejected);}
});
test("privacy and consent fail closed",()=>{
 for(const mod of [
    x=>{x.body+="\nowner@example.com";},
    x=>{x.body+="\nAuthorization: Bearer abcdefghijklmnop123456";},
    x=>{x.body=x.body.replace(consent[1],consent[1].replace("[x]","[ ]"));},
    x=>{x.labels=[{name:"privacy-review-required"}];},
 ]) {const x=sample();mod(x);assert.throws(()=>validateIssue(x,42),SourceRejected);}
});
test("digest matches the canonical Python SQL receipt",async()=>{
 assert.equal(await receiptSha256(32),"535a8bb6c51d4dd3d1255cf054cd9118adab749de67f543c076f4b5ab350d1db");
});
test("reject bad numeric IDs",()=>{for(const n of [0, true, NaN, 1.5, 10000000000000])
 assert.throws(()=>validateIssue(sample(),n),SourceRejected);});
