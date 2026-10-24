const { chromium } = require("playwright");
const fs = require("fs");
fs.mkdirSync("alfolio-preview/screenshots",{recursive:true});
const base = "http://127.0.0.1:4000";
function check(value,message){ if(!value) throw new Error(message); }
async function screenshotAndCheck(page,url,file,width,name){
 const response=await page.goto(base+url,{waitUntil:"networkidle"});
 check(response?.ok(),name+" failed to load "+url);
 await page.locator('img').evaluateAll(images=>images.forEach(im=>im.loading="eager"));
 await page.waitForTimeout(700);
 const overflow=await page.evaluate(()=>document.documentElement.scrollWidth);
 check(overflow<=width+2,name+" horizontal overflow "+overflow+" > "+width);
 await page.screenshot({path:"alfolio-preview/screenshots/"+file,fullPage:true});
}
(async()=>{
 const browser=await chromium.launch({headless:true});
 try {
  for(const [name,width,height] of [["desktop",1440,900],["mobile",390,844]]){
   const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
   // Home: 5 selected from al-folio native Jekyll Scholar.
   await screenshotAndCheck(page,"/",name+".png",width,name+" Home");
   const navText=(await page.locator("#navbar").textContent())||"";
   for(const label of ["About","Publications","Projects"])
     check(navText.includes(label),name+" missing nav "+label);
   const titleBox=await page.locator(".academic-hero .post-title").boundingBox();
   const portrait=await page.locator(".academic-hero .academic-portrait").boundingBox();
   check(!!portrait&&!!titleBox&&Math.abs(titleBox.y-portrait.y)<25,name+" profile picture not aligned with name");
   check((await page.locator(".academic-home .academic-hero .post-title").innerText()).includes("Ikhyeon Cho"),name+" unexpected heading");
   const homeHeadings=(await page.locator(".academic-home article h2").allInnerTexts()).map(s=>s.trim());
   for(const label of ["Research Interests","Selected Publications","Research Software & Systems"])
     check(homeHeadings.includes(label),name+" Home missing heading "+label+"; got "+homeHeadings);
   const five=await page.locator(".academic-home .publications ol.bibliography li").count();
   check(five===5,name+" expected 5 selected publications; got "+five);
   check(await page.locator('.academic-feature-project-row[href*="/projects/#fastdem"]').count()===1,name+" FastDEM preview missing");
   const heroThumb=await page.locator(".academic-home .publications .abbr").first().boundingBox();
   const fullHomeText=await page.locator("body").innerText();
   for(const paper of ["LeSTA","Terrablox","MapGLoc","Multi-Agent Path Finding","ODS-Bot"])
     check(fullHomeText.includes(paper),name+" missing "+paper);
   check(fullHomeText.includes("NOT PUBLISHED"),name+" under review disclaimer missing");
   const reviewBadges=page.locator(".academic-home .publications .abbr abbr.badge").filter({hasText:"Under Review"});
   check(await reviewBadges.count()===2,name+" expected exactly 2 Under Review status badges on Home");
   const color=await reviewBadges.first().evaluate(el=>getComputedStyle(el).backgroundColor);
   check(color==="rgb(104, 117, 129)",name+" expected neutral gray badge; got "+color);

   const resources=(await page.locator(".academic-home .publications .links a").allInnerTexts()).map(x=>x.trim());
   for(const label of ["Paper","Code","Project"])check(resources.includes(label),name+" missing resource "+label);
   check(!resources.some(x=>["Bib","Website","PDF"].includes(x)),name+" stale resource labels");
   const firstResource=page.locator(".academic-home .publications .links a").first();
   check(await firstResource.evaluate(e=>getComputedStyle(e).borderTopWidth)==="0px",name+" Home resource border");
   // Full bibliography: grouped, compact, not a duplicate of selected section.
   await screenshotAndCheck(page,"/publications/","publications-"+name+".png",width,name+" Publications");
   const sections=page.locator(".academic-publication-group");
   check(await sections.count()===4,name+" expected four publication groups");
   const journalCount=await page.locator("#journal-articles ol.bibliography li").count();
   const draftCount=await page.locator("#manuscripts ol.bibliography li").count();
   check(journalCount===3&&draftCount===2,name+" wrong groups "+journalCount+"/"+draftCount);
   const manuscriptBadges=page.locator("#manuscripts .abbr abbr.badge").filter({hasText:"Under Review"});
   check(await manuscriptBadges.count()===2,name+" expected 2 review badges on Publications");
   const journalBadges=await page.locator("#journal-articles .abbr abbr.badge").allTextContents();
   check(journalBadges.every(x=>!x.includes("Under Review")),name+" status must not appear on published articles");

   check((await page.locator("#manuscripts").innerText()).includes("not published or accepted"),name+" under review status not explicit");
   check((await page.locator("#international-conference").innerText()).includes("require verification"),name+" UR placeholder omitted");
   check((await page.locator("#domestic-conference").innerText()).includes("pending verification"),name+" KRoC placeholder omitted");
   const compactThumb=await page.locator("#journal-articles .publications .abbr").first().boundingBox();
   check(!!heroThumb&&!!compactThumb&&compactThumb.width<heroThumb.width,
      name+" Publications thumbnail should be smaller than Home: "+JSON.stringify({heroThumb,compactThumb}));
   const pubResources=(await page.locator(".academic-publications .links a").allInnerTexts()).map(x=>x.trim());
   check(!pubResources.some(x=>["Bib","Website","PDF"].includes(x)),name+" stale labels Publications");
   if(pubResources.length)check(await page.locator(".academic-publications .links a").first().evaluate(e=>getComputedStyle(e).borderTopWidth)==="0px",name+" Publications resource border");
   // Projects: large image-led rows, no card grid.
   await screenshotAndCheck(page,"/projects/","projects-"+name+".png",width,name+" Projects");
   check(await page.locator(".academic-project-row").count()===3,name+" expected 3 project rows");
   for(const slug of ["fastdem","multi-robot-navigation","ods-bot"])
     check(await page.locator("#"+slug).count()===1,name+" missing project "+slug);
   check(await page.locator('.academic-project-list .academic-project-row img[src*="/project_preview/"]').count()===3,name+" missing project previews");
   const imgStatuses=await page.locator('.academic-project-list img').evaluateAll(imgs=>imgs.map(x=>({src:x.getAttribute("src"),ok:x.complete&&x.naturalWidth>0})));
   check(imgStatuses.every(x=>x.ok),name+" broken project preview "+JSON.stringify(imgStatuses));
   // Generated preview art must not contain the previous opaque white caption panel or embedded labels.
   const svgChecks=await page.evaluate(async()=>{
     const assets=[...["lesta","terrablox","mapgloc","multi-agent","ods-bot"].map(n=>"/assets/img/publication_preview/"+n+".svg"),
       ...["fastdem","multi-robot","ods-bot"].map(n=>"/assets/img/project_preview/"+n+".svg")];
     return Promise.all(assets.map(async url=>{
       const resp=await fetch(url);
       const body=await resp.text();
       return {url,status:resp.status,hasPanel:body.includes('fill="#ffffff"')||body.includes('ILLUSTRATIVE PLACEHOLDER')||body.includes('<text')};
     }));
   });
   check(svgChecks.every(x=>x.status===200&&!x.hasPanel),name+" white thumbnail label panel still present: "+JSON.stringify(svgChecks));
   const projectText=await page.locator(".academic-project-list").innerText();
   check(projectText.includes("Hyundai Motor Company")&&projectText.includes("Hyundai Mobis"),name+" project metadata missing");
   console.log(name,JSON.stringify({selected:five,journalCount,draftCount,projects:3,homeThumbnailWidth:heroThumb.width,fullThumbnailWidth:compactThumb.width}));
   await page.close();
  }
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
