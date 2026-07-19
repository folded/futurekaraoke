---
layout: base.njk
title: Future Karaoke
---

<div class="hero">
  <p class="eyebrow">Multi-disciplinary performance night</p>
  <h1>A place for imagination <br>and sharing</h1>
  <p class="lede">Poetry, spoken word and live experiment on a warm, unhurried stage — five-minute slots for polished pieces, works-in-progress and the beautifully unfinished.</p>
  <p class="cta-row">
    <a class="cta cta-primary" href="mailto:{{ site.email.speak }}">Sign up to perform</a>
    <a class="cta cta-ghost" href="/events/">See what's on</a>
  </p>
</div>

{% if events.featured %}
{% set ev = events.featured %}
<section class="feature reveal" aria-label="{% if ev.isPast %}Most recent{% else %}Next{% endif %} event">
  <p class="section-kicker">{% if ev.isPast %}Most recently{% else %}Next up{% endif %} · {{ ev.title }}</p>
  {% include "poster.njk" %}
</section>
{% endif %}
