const { chromium } = require("playwright");
(async () => {
 const browser = await chromium.launch({headless:true});
 for (const [name,width,height] of [["desktop",1440,900],["mobile",390,844]]) {
   const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
   const response=await page.goto("http://127.0.0.1:4000/", {waitUntil:"networkidle"});
   if (!response?.ok()) throw new Error("Home page failed: "+name);
   const body=await page.locator("body").innerText();
   if (!body.includes("DEMO ONLY")) throw new Error("BibTeX selected paper not rendered: "+name);
   const sw=await page.evaluate(()=>document.documentElement.scrollWidth);
   if (sw>width+2) throw new Error("Horizontal overflow: "+name+" "+sw);
   await page.screenshot({path:"alfolio-preview/screenshots/"+name+".png",fullPage:true});
   await page.close();
 }
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
