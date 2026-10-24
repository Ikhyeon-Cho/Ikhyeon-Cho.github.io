---
layout: page
permalink: /publications/
title: Publications
nav: true
nav_order: 1
---
<style>{% include academic.css %}</style>
<p class="academic-page-intro">Complete academic publication record, organized by publication type. <em>This design preview includes provisional titles and placeholder author metadata; missing UR and KRoC records have not been fabricated.</em></p>

<div class="academic-publications">
  <section class="academic-publication-group" id="journal-articles">
    <h2>Journal Articles</h2>
    <div class="publications">
      {% bibliography --group_by none --query @*[category=journal] %}
    </div>
  </section>
  <section class="academic-publication-group" id="international-conference">
    <h2>Conference Papers</h2>
    <p class="academic-pending-record">UR conference record — title, authors, year, and publication type require verification before addition.</p>
  </section>
  <section class="academic-publication-group" id="domestic-conference">
    <h2>Domestic Conference Papers &amp; Presentations</h2>
    <p class="academic-pending-record">KRoC records — bibliographic details and paper/abstract/presentation status pending verification.</p>
  </section>
  <section class="academic-publication-group" id="manuscripts">
    <h2>Manuscripts Under Review</h2>
    <p class="academic-review-note">The following manuscripts are <strong>under review, not published or accepted</strong>. No journal or conference venue is claimed.</p>
    <div class="publications">
      {% bibliography --group_by none --query @*[category=manuscript] %}
    </div>
  </section>
</div>
