"""Configure the REAL upstream al-folio checkout solely for CI design validation."""
from pathlib import Path
import re, shutil, struct, zlib

root=Path(__file__).resolve().parent.parent/"alfolio-src"
cfg=root/"_config.yml"
s=cfg.read_text()
edits={
  "first_name": "Ikhyeon", "middle_name": '""', "last_name": "Cho",
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
# Match author highlighting to the profile name without changing bibliography engine.
s=s.replace("last_name: [Einstein]", "last_name: [Cho]")
s=s.replace("first_name: [Albert, A.]", "first_name: [Ikhyeon, I.]")
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
# Single-source page files: no hidden copies of the page body in this script.
for name in ("publications","projects"):
  page=(Path(__file__).resolve().parent/"overrides"/f"{name}.md").read_text()
  page=page.replace("{% include academic.css %}",style)
  (root/"_pages"/f"{name}.md").write_text(page)
for p in (root/"_pages").glob("*"):
  if p.is_file() and p.name not in {"about.md","publications.md","projects.md","404.md"}: p.unlink()
for d in ["_news","_posts","_projects","_books","_teachings","_talks","assets/jupyter"]:
  p=root/d
  if p.exists(): shutil.rmtree(p)

# Explicitly provisional records: names/status from the review brief, not real verified BibTeX.
# No fabricated author list, venue for under-review work, DOI, or live resource URLs.
(root/"_bibliography"/"papers.bib").write_text("""---
---
@article{lesta,
  title = {LeSTA (full publication title pending verification)},
  author = {Pending, Author List},
  journal = {IEEE Robotics and Automation Letters (RA-L)},
  year = {2024},
  category = {journal},
  abbr = {RA-L},
  selected = {true},
  preview = {lesta.svg},
  pdf = {https://example.com/PREVIEW-ONLY-lesta-paper},
  code = {https://example.com/PREVIEW-ONLY-lesta-code},
  website = {https://example.com/PREVIEW-ONLY-lesta-project}
}
@unpublished{terrablox,
  title = {Terrablox (full manuscript title pending verification)},
  author = {Pending, Author List},
  year = {2026},
  category = {manuscript},
  note = {Manuscript under review — NOT PUBLISHED},
  selected = {true},
  preview = {terrablox.svg}
}
@unpublished{mapgloc,
  title = {MapGLoc (full manuscript title pending verification)},
  author = {Pending, Author List},
  year = {2026},
  category = {manuscript},
  note = {Manuscript under review — NOT PUBLISHED},
  selected = {true},
  preview = {mapgloc.svg}
}
@article{multiagent,
  title = {Multi-Agent Path Finding (full publication title pending verification)},
  author = {Pending, Author List},
  journal = {Sensors},
  year = {2026},
  category = {journal},
  abbr = {Sensors},
  selected = {true},
  preview = {multi-agent.svg},
  pdf = {https://example.com/PREVIEW-ONLY-multiagent-paper}
}
@article{odsbot,
  title = {ODS-Bot (full publication title pending verification)},
  author = {Pending, Author List},
  journal = {IEEE Access},
  year = {2022},
  category = {journal},
  abbr = {IEEE Access},
  selected = {true},
  preview = {ods-bot.svg},
  website = {/projects/#ods-bot}
}
""")

# Explicit placeholder vector art for design validation. Replace with genuine PNG/GIF.
# These are abstract schematics, not real research results or photographs.
art=root/"assets"/"img"/"publication_preview"
art.mkdir(parents=True,exist_ok=True)
project_art=root/"assets"/"img"/"project_preview"
project_art.mkdir(parents=True,exist_ok=True)
def placeholder(_label,idx,large=False):
  palettes=[
    ("#e7edf1","#6b929e","#9ab5aa"),
    ("#e7eae6","#918d75","#bdafa0"),
    ("#e8edf2","#67839f","#8aa6b8"),
    ("#ecedf1","#777e9e","#afb9c4"),
    ("#eff0ee","#708b85","#a9b8b0"),
    ("#e5edef","#5e8992","#90b2b5"),
    ("#eaedf1","#697c9d","#b1bac5"),
    ("#e9ede8","#7a8e81","#b5c5b5")
  ]
  bg,ink,muted=palettes[idx%len(palettes)]
  w,h=(480,330) if large else (300,210)
  circles="".join(f'<circle cx="{(j*67+idx*31)%w}" cy="{(j*47+idx*19)%h}" r="{3+j%5}" fill="{ink}" opacity="0.32"/>' for j in range(36))
  lines="".join(f'<path d="M {10+j*21} {h-29} Q {w/2} {(j*17)%h} {w-9} {15+j*14}" stroke="{muted}" stroke-width="1.3" opacity="0.55" fill="none"/>' for j in range(8))
  # No white label panel or embedded text: paper/project titles live in the adjacent HTML.
  return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="{w}" height="{h}" fill="{bg}"/>{lines}{circles}</svg>'
for idx,(filename,label) in enumerate([
  ("lesta.svg","LeSTA"),("terrablox.svg","Terrablox"),
  ("mapgloc.svg","MapGLoc"),("multi-agent.svg","Multi-Agent Planning"),
  ("ods-bot.svg","ODS-Bot")
]):
  (art/filename).write_text(placeholder(label,idx))
for idx,(filename,label) in enumerate([
  ("fastdem.svg","FastDEM"),("multi-robot.svg","Multi-Robot Navigation"),
  ("ods-bot.svg","ODS-Bot")
],5):
  (project_art/filename).write_text(placeholder(label,idx,large=True))

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
