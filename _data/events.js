// Data-driven event listing.
//
// Add an event by appending an object to `events` below. The template layer
// never needs editing: upcoming/past sorting and human-readable date labels
// are all derived here at build time.

const TIME_ZONE = "Australia/Melbourne";

const events = [
  {
    slug: "future-ghosts",
    title: "Future Ghosts",
    tagline: "An evening of Poetry and Spoken Word @ The Count's",
    note: "Light refreshments available for purchase at the bar",
    venue: "The Ian Potter Centre for Performing Arts",
    address: "48 Exhibition Walk, Clayton VIC 3168, Australia",
    mapLink:
      "https://www.google.com/maps/search/?api=1&query=48+Exhibition+Walk,+Clayton+VIC+3168,+Australia",
    start: "2025-10-14T18:00:00+11:00",
    end: "2025-10-14T20:00:00+11:00",
    poster: {
      image: "/images/future-ghosts.webp",
      alt: "Future Ghosts — poetry and spoken word, painted in a cosmic, ghostly palette",
    },
    funding:
      "Future Ghosts is supported by funding from The School of Languages, Literatures, Cultures & Linguistics, Monash University.",
  },
];

const dateFmt = new Intl.DateTimeFormat("en-AU", {
  weekday: "long",
  day: "numeric",
  month: "long",
  year: "numeric",
  timeZone: TIME_ZONE,
});

const timeFmt = new Intl.DateTimeFormat("en-AU", {
  hour: "2-digit",
  minute: "2-digit",
  hour12: false,
  timeZone: TIME_ZONE,
});

function decorate(event) {
  const start = new Date(event.start);
  const end = new Date(event.end);
  return {
    ...event,
    startISO: event.start,
    dateLabel: dateFmt.format(start),
    timeLabel: `${timeFmt.format(start)} – ${timeFmt.format(end)}`,
    isPast: end.getTime() < Date.now(),
  };
}

module.exports = () => {
  const all = events
    .map(decorate)
    .sort((a, b) => new Date(a.start) - new Date(b.start));

  const upcoming = all.filter((e) => !e.isPast);
  const past = all.filter((e) => e.isPast).reverse(); // most recent first

  return {
    all,
    upcoming,
    past,
    next: upcoming[0] || null,
    // The single most relevant event to feature on the home page: the next
    // upcoming show, or — if the calendar is quiet — the most recent one.
    featured: upcoming[0] || past[0] || null,
  };
};
