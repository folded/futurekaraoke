---
layout: base.njk
title: Future Karaoke
---

<div class="hero">
  <div class="hero-card">
    <h1>A place for imagination and sharing</h1>
    <p class="lede">Poetry, spoken word and live experiment on a warm, unhurried stage. Five-minute slots for polished pieces, works-in-progress, and the beautifully unfinished.</p>
  </div>
</div>

{% if events.featured %}
{% set ev = events.featured %}
<section class="feature reveal" aria-label="{% if ev.isComingSoon %}Coming soon{% elif ev.isPast %}Most recent{% else %}Next{% endif %} event">
  <p class="section-kicker">{% if ev.isComingSoon %}Coming soon{% elif ev.isPast %}Most recently{% else %}Next up{% endif %} · {{ ev.title }}</p>
  {% include "poster.njk" %}
</section>
{% endif %}

{# When the featured slot is taken by an upcoming/coming-soon show, still keep
   the most recent past event's poster on the page below it. #}
{% set recent = events.past[0] %}
{% if recent and recent.slug != events.featured.slug %}
{% set ev = recent %}
<section class="feature reveal" aria-label="Most recent event">
  <p class="section-kicker">Most recently · {{ ev.title }}</p>
  {% include "poster.njk" %}
</section>
{% endif %}
