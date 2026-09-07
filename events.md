---
layout: base.njk
title: Events
description: Upcoming and past Future Karaoke performance nights — poetry, spoken word and live experiment.
---

<div class="page-head">
  <h1>Events</h1>
</div>

<section aria-label="Upcoming events">
  <h2 class="section-label">What's on</h2>
  {% if events.upcoming.length %}
  {% for ev in events.upcoming %}
  <div class="feature reveal">
    <p class="section-kicker">{% if ev.isComingSoon %}Coming soon · {% endif %}{{ ev.title }}</p>
    {% include "poster.njk" %}
  </div>
  {% if ev.workshop and not ev.workshop.isPast %}
  {% include "workshop.njk" %}
  {% endif %}
  {% endfor %}
  {% else %}
  <div class="event-card reveal empty-state">
    <h3>No shows on the calendar right now</h3>
    <p>We're between nights — but not for long. Register your interest to perform and we'll let you know the moment the next date lands.</p>
    <p class="event-actions"><a class="btn" href="mailto:{{ site.email.speak }}">Get on the list</a></p>
  </div>
  {% endif %}
</section>

{% if events.past.length %}
<section class="past-events" aria-label="Past events">
  <h2 class="section-label">Previously</h2>
  {% for ev in events.past %}
  <div class="feature reveal">
    <p class="section-kicker">{{ ev.title }}</p>
    {% include "poster.njk" %}
  </div>
  {% endfor %}
</section>
{% endif %}
