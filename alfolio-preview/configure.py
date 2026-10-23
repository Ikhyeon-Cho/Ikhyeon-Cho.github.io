"""Configure the REAL upstream al-folio checkout solely for CI design validation."""
from pathlib import Path
import re, shutil, struct, zlib

root=Path(__file__).resolve().parent.parent/"alfolio-src"
cfg=root/"_config.yml"
s=cfg.read_text()
edits={
  "first_name": "Your", "middle_name": '""', "last_name": "Name",
  "url": '""', "baseurl": '""', "search_enabled": "false",
  "enable_darkmode": "false", "last_updated": "false",
  "footer_fixed": "false", "max_width": "860px"
}
for key,val in edits.items():
  pattern=rf"^{re.escape(key)}:\s*[^\n]*$"
  s,n=re.subn(pattern, f"{key}: {val}", s, count=1, flags=re.M)
  if n!=1: raise RuntimeError(f"Missing upstream setting: {key}")
# No dark fixed footer and no unlicensed stock-photo attribution in a minimal academic site.
s=re.sub(r'(?m)^footer_text: >[^\n]*\n(?:^  .*\n)+', 'footer_text: ""\n', s, count=1)
s=s.replace("imagemagick:\n  enabled: true", "imagemagick:\n  enabled: false")
cfg.write_text(s)

# Keep the upstream Jekyll layout, Scholar plugin, theme and Gemfile unchanged.
about="""---
layout: about
title: about
permalink: /
subtitle: Ph.D. Candidate in Robotics · Expected Graduation 2026
profile:
  align: right
  image: profile-placeholder.png
  image_circular: false
  more_info: ""
selected_papers: true
social: false
announcements:
  enabled: false
latest_posts:
  enabled: false
---
<style>
:root {
  --global-theme-color: #285f7f;
  --global-hover-color: #285f7f;
  --global-footer-bg-color: #f7f8f9;
  --global-footer-text-color: #52616c;
  --global-footer-link-color: #285f7f;
}
body { font-family: Arial, Helvetica, sans-serif; }
.post-header .post-title { font-size: 2.5rem; font-weight: 400; }
.post-header .desc { font-size: 1rem; }
.post article h2 { font-size: 1.52rem; font-weight: 400; margin-top: 1.7rem; margin-bottom: 0.7rem; }
.post article > h2 { text-transform: capitalize; }
.profile.float-right { width: 26%; max-width: 172px; margin-left: 24px; margin-bottom: 12px; }
.profile figure { margin-bottom: 0; }
.profile img { box-shadow: none !important; border-radius: 2px !important; }
.publications .bibliography li { margin-bottom: 1.15rem; }
.publications .title { font-weight: 500; }
footer { border-top: 1px solid #e5e9ec; font-size: .78rem; }
@media (max-width: 575px) {
  .post-header .post-title { font-size: 2.05rem; }
  .post article h2 { font-size: 1.4rem; }
  .profile.float-right { float: right !important; width: 31%; max-width: 110px; margin-left: 16px; margin-bottom: 10px; }
  .post { overflow-wrap: anywhere; }
}
</style>

I am a Ph.D. candidate working in robotics, autonomous driving, and 3D environment perception.

## Research Interests

My research focuses on **3D scene understanding**, **robotic perception**, and **spatial representations for autonomous systems**. This is placeholder text for design validation, not a finalized research statement.
"""
(root/"_pages"/"about.md").write_text(about)
(root/"_pages"/"publications.md").write_text("""---
layout: page
permalink: /publications/
title: publications
nav: true
nav_order: 1
---
<div class="publications">
{% bibliography %}
</div>
""")
for p in (root/"_pages").glob("*"):
  if p.is_file() and p.name not in {"about.md","publications.md","404.md"}: p.unlink()
for d in ["_news","_posts","_projects","_books","_teachings","_talks","assets/jupyter"]:
  p=root/d
  if p.exists(): shutil.rmtree(p)

# Explicitly fake paper entries ONLY to test that the upstream bibliography renders.
(root/"_bibliography"/"papers.bib").write_text("""---
---
@inproceedings{demo2026replace,
  title = {DEMO ONLY: Example 3D Perception Paper — Replace Me},
  author = {Name, Your and Coauthor, Example},
  booktitle = {Fictional Conference (Not a Publication)},
  year = {2026},
  abbr = {DEMO},
  selected = {true},
  bibtex_show = {true}
}
@inproceedings{demo2025replace,
  title = {DEMO ONLY: Example Robotic Mapping Paper — Replace Me},
  author = {Name, Your and Coauthor, Example},
  booktitle = {Fictional Conference (Not a Publication)},
  year = {2025},
  abbr = {DEMO},
  selected = {true},
  bibtex_show = {true}
}
""")

# Generate a simple neutral placeholder PNG without additional dependencies.
w,h=280,340
pixel=bytes((235,239,243))
scan=b"\x00"+pixel*w
raw=scan*h
def chunk(tag,dat):
  return struct.pack(">I",len(dat))+tag+dat+struct.pack(">I",zlib.crc32(tag+dat)&0xffffffff)
png=b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",struct.pack(">IIBBBBB",w,h,8,2,0,0,0))+chunk(b"IDAT",zlib.compress(raw))+chunk(b"IEND",b"")
(root/"assets"/"img"/"profile-placeholder.png").write_bytes(png)
print("Configured actual al-folio source", root)
print("Gemfile, plugin list, upstream about layout & Jekyll Scholar retained.")
