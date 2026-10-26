import assert from "node:assert/strict";
import {chromium} from "playwright-core";
import {existsSync} from "node:fs";
const chrome=process.env.CHROMIUM_BIN;
if(!chrome||!existsSync(chrome))throw Error("SYSTEM_CHROMIUM_REQUIRED");
const base="http://127.0.0.1:8787";
const browser=await chromium.launch({headless:true,executablePath:chrome,
 args:process.env.CI?["--no-sandbox","--disable-dev-shm-usage"]:[]});
const ownerContext=await browser.newContext();
const reviewerContext=await browser.newContext();
const owner=await ownerContext.newPage();
const reviewer=await reviewerContext.newPage();
async function register(page,email){
 await page.goto(base);
 await page.locator("#email").fill(email);
 await page.locator("#password").fill("SufficientlyLong_2026!");
 await page.locator("#register").click();
 await page.waitForFunction(()=>document.querySelector("#account").textContent.includes("Signed in:"));
}
try{
 await register(owner,"browser-owner@example.test");
 await register(reviewer,"browser-reviewer@example.test");
 await owner.locator("#projectName").fill("Website approval launch");
 await owner.locator("#projectForm button").click();
 await owner.waitForFunction(()=>document.querySelector("#status").textContent.includes("Project created"));
 const pid=await owner.locator("#projects").inputValue();
 assert.ok(Number(pid)>0);
 await owner.locator("#reviewerEmail").fill("browser-reviewer@example.test");
 await owner.locator("#reviewerForm button").click();
 await owner.waitForFunction(()=>document.querySelector("#status").textContent.includes("Reviewer invited"));
 await owner.locator("#fileName").fill("concept.txt");
 await owner.locator("#fileContent").fill("New marketing creative: revision one");
 await owner.locator("#uploadForm button").click();
 await owner.waitForFunction(()=>document.querySelector("#status").textContent.includes("revision 1 saved"));
 await reviewer.locator("#refresh").click();
 await reviewer.waitForFunction(()=>document.querySelectorAll("#projects option").length>1);
 await reviewer.locator("#projects").selectOption(pid);
 await reviewer.waitForFunction(()=>document.querySelectorAll("#versions option").length>1);
 await reviewer.locator("#commentText").fill("Reviewed and approved by client.");
 await reviewer.locator("#commentForm button").click();
 await reviewer.waitForFunction(()=>document.querySelector("#status").textContent.includes("comment persisted"));
 await reviewer.locator("#approve").click();
 await reviewer.waitForFunction(()=>document.querySelector("#status").textContent.includes("decision saved"));
 await owner.reload();
 await owner.waitForFunction(()=>document.querySelector("#account").textContent.includes("Signed in:"));
 await owner.locator("#projects").selectOption(pid);
 await owner.waitForFunction(()=>document.querySelector("#details").textContent.includes('"decision": "APPROVE"'));
 const detail=await owner.locator("#details").innerText();
 assert.match(detail,/APPROVE/);
 assert.match(detail,/Reviewed and approved/);
 assert.match(detail,/event_hash/);
 console.log(JSON.stringify({result:"PASS",flow:"OWNER_BROWSER_API_SQLITE_REVIEWER_BROWSER_AUDIT_OWNER_BROWSER",
  distinct_user_sessions:2,persisted_decision:true,audit_event:true,ai_inference:"NOT_TESTED",
  independent_qa:"NOT_PERFORMED",release:"DENIED"}));
}finally{
 await ownerContext.close();await reviewerContext.close();await browser.close();
}
