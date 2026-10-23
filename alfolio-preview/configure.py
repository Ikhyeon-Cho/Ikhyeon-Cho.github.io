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
  "footer_fixed": "false", "max_width": "860px", "navbar_fixed": "false"
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
# Apply small, tracked text/style overrides. Keep upstream about layout and bibliography rendering.
about=(Path(__file__).resolve().parent/"overrides"/"about.md").read_text()
style=(Path(__file__).resolve().parent/"overrides"/"academic.css").read_text()
about=about.replace("{% include academic.css %}",style)
(root/"_pages"/"about.md").write_text(about)
# Site-level layout overrides; al_folio_core and Jekyll-Scholar remain installed.
layouts=root/"_layouts"
layouts.mkdir(exist_ok=True)
for name in ("about","bib"):
  layout=(Path(__file__).resolve().parent/"overrides"/f"layout-{name}.liquid")
  (layouts/f"{name}.liquid").write_text(layout.read_text())
(root/"_pages"/"publications.md").write_text("""---
layout: page
permalink: /publications/
title: Publications
nav: true
nav_order: 1
---
<div class="publications">
{% bibliography %}
</div>
""")
# Ensure shared academic link style applies on Publications page as well as Home.
pub=root/"_pages"/"publications.md"
ps=pub.read_text()
ps=ps.replace('<div class="publications">', '<style>'+style+'</style>\n<div class="publications">', 1)
pub.write_text(ps)
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
  abbr = {ICRA},
  selected = {true},
  pdf = {https://example.com/demo-icra-paper.pdf},
  code = {https://example.com/demo-icra-code},
  website = {https://example.com/demo-icra-project}
}
@inproceedings{demo2025replace,
  title = {DEMO ONLY: Example Robotic Mapping Paper — Replace Me},
  author = {Name, Your and Coauthor, Example},
  booktitle = {Fictional Conference (Not a Publication)},
  year = {2025},
  abbr = {CVPR},
  selected = {true},
  pdf = {https://example.com/demo-cvpr-paper.pdf},
  code = {https://example.com/demo-cvpr-code},
  website = {https://example.com/demo-cvpr-project}
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
