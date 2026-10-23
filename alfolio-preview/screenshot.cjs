const { chromium } = require("playwright");
require("fs").mkdirSync("alfolio-preview/screenshots",{recursive:true});
(async () => {
 const browser = await chromium.launch({headless:true});
 for (const [name,width,height] of [["desktop",1440,900],["mobile",390,844]]) {
   const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
   const response=await page.goto("http://127.0.0.1:4000/", {waitUntil:"networkidle"});
   if (!response?.ok()) throw new Error("Home page failed: "+name);
   const body=await page.locator("body").innerText();
   if (!body.includes("DEMO ONLY")) throw new Error("BibTeX selected paper not rendered: "+name);
   const bibLinks = await page.getByText("Bib",{exact:true}).count();
   if (bibLinks>0) throw new Error("Bib button remains visible: "+name);
   const resourceHrefs=await page.locator('.publications a[href*="example.com/demo-"]').evaluateAll(links=>links.map(a=>a.getAttribute('href')));
   if(resourceHrefs.length<3) throw new Error("Expected native PDF/Code/Project resources: "+name+"; got "+JSON.stringify(resourceHrefs));
   console.log(name, "Resource hrefs",resourceHrefs);
   const sw=await page.evaluate(()=>document.documentElement.scrollWidth);
   if (sw>width+2) throw new Error("Horizontal overflow: "+name+" "+sw);
   await page.screenshot({path:"alfolio-preview/screenshots/"+name+".png",fullPage:true});
   await page.close();
 }
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
