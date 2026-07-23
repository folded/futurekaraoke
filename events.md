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
  <article class="event-card reveal">
    <h3>{{ ev.title }}{% if ev.isComingSoon %} <span class="event-badge">Coming soon</span>{% endif %}</h3>
    <p class="event-tagline">{{ ev.tagline }}</p>
    {%- if ev.note %}
    <p class="event-note">{{ ev.note }}</p>
    {%- endif %}
    {%- if ev.isComingSoon %}
    <p class="event-note">Date and venue to be announced — register your interest and we'll tell you the moment the next date lands.</p>
    <p class="event-actions">
      <a class="cta cta-primary" href="mailto:{{ site.email.speak }}">Get on the list</a>
    </p>
    {%- else %}
    <dl class="event-details">
      <dt>Where</dt>
      <dd>{{ ev.venue }}<br><a href="{{ ev.mapLink }}" target="_blank" rel="noopener">{{ ev.address }}</a></dd>
      <dt>When</dt>
      <dd><time datetime="{{ ev.startISO }}">{{ ev.dateLabel }} · {{ ev.timeLabel }}</time></dd>
    </dl>
    <p class="event-actions">
      <a class="cta cta-primary" href="mailto:{{ site.email.tickets }}">RSVP (free)</a>
      <a class="cta cta-ghost" href="mailto:{{ site.email.speak }}">Perform</a>
    </p>
    {%- endif %}
    {%- if ev.funding %}
    <p class="event-funding">{{ ev.funding }}</p>
    {%- endif %}
  </article>
  {% endfor %}
  {% else %}
  <div class="event-card reveal empty-state">
    <h3>No shows on the calendar right now</h3>
    <p>We're between nights — but not for long. Register your interest to perform and we'll let you know the moment the next date lands.</p>
    <p class="event-actions"><a class="cta cta-primary" href="mailto:{{ site.email.speak }}">Get on the list</a></p>
  </div>
  {% endif %}
</section>

{% if events.past.length %}
<section class="past-events" aria-label="Past events">
  <h2 class="section-label">Previously</h2>
  {% for ev in events.past %}
  <article class="event-card event-card--past reveal">
    <h3>{{ ev.title }}</h3>
    <p class="event-tagline">{{ ev.tagline }}</p>
    <p class="event-when"><time datetime="{{ ev.startISO }}">{{ ev.dateLabel }}</time> · {{ ev.venue }}</p>
  </article>
  {% endfor %}
</section>
{% endif %}
