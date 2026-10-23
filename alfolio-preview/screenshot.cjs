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
   const navText=await page.locator("#navbar").textContent();
   if (!navText.includes("About")||!navText.includes("Publications")) throw new Error("Title Case navigation missing: "+navText);
   const selectedTitle=await page.locator(".post article h2").allTextContents();
   if (!selectedTitle.some(t=>t.trim()==="Selected Publications")) throw new Error("Title Case Selected Publications missing: "+JSON.stringify(selectedTitle));
   const titleBox=await page.locator(".academic-hero .post-title").boundingBox();
   const photoBox=await page.locator(".academic-hero .academic-portrait").boundingBox();
   if (!titleBox||!photoBox||Math.abs(titleBox.y-photoBox.y)>24) throw new Error("Photo not aligned to name on "+name+" "+JSON.stringify({titleBox,photoBox}));
   const labels=(await page.locator(".publications .links a").allTextContents()).map(t=>t.trim());
   for (const required of ["Paper","Code","Project"]){
     if (!labels.includes(required)) throw new Error("Missing "+required+" resource link on "+name+" "+JSON.stringify(labels));
   }
   if (labels.includes("Website")||labels.includes("PDF")||labels.includes("Bib")) throw new Error("Old links still visible "+JSON.stringify(labels));
   const borderWidth=await page.locator(".publications .links a").first().evaluate(el=>getComputedStyle(el).borderTopWidth);
   if(borderWidth!=="0px") throw new Error("Outline remains on resource links: "+borderWidth);
   const bibLinks = await page.getByText("Bib",{exact:true}).count();
   if (bibLinks>0) throw new Error("Bib button remains visible: "+name);
   const resourceHrefs=await page.locator('.publications a[href*="example.com/demo-"]').evaluateAll(links=>links.map(a=>a.getAttribute('href')));
   if(resourceHrefs.length<3) throw new Error("Expected native PDF/Code/Project resources: "+name+"; got "+JSON.stringify(resourceHrefs));
   console.log(name, "Resource hrefs",resourceHrefs);
   const sw=await page.evaluate(()=>document.documentElement.scrollWidth);
   if (sw>width+2) throw new Error("Horizontal overflow: "+name+" "+sw);
   await page.screenshot({path:"alfolio-preview/screenshots/"+name+".png",fullPage:true});
   const publicationResponse=await page.goto("http://127.0.0.1:4000/publications/",{waitUntil:"networkidle"});
   if(!publicationResponse?.ok())throw new Error("Publications page failed "+name);
   const publicationResources=(await page.locator(".publications .links a").allTextContents()).map(s=>s.trim());
   for(const label of ["Paper","Code","Project"]){ if(!publicationResources.includes(label))throw new Error("Missing "+label+" on Publications page "+name); }
   if(publicationResources.some(s=>["Website","Bib","PDF"].includes(s))) throw new Error("Unexpected publication resource labels "+JSON.stringify(publicationResources));
   const pubBorder=await page.locator(".publications .links a").first().evaluate(el=>getComputedStyle(el).borderTopWidth);
   if(pubBorder!=="0px")throw new Error("Publications page link border remains "+name+" "+pubBorder);
   await page.screenshot({path:"alfolio-preview/screenshots/publications-"+name+".png",fullPage:true});
   await page.close();
 }
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
