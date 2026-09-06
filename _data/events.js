// Data-driven event listing.
//
// Add an event by appending an object to `events` below. The template layer
// never needs editing: upcoming/past sorting and human-readable date labels
// are all derived here at build time.
//
// A "coming soon" event has no date yet. Omit `start`/`end` and set
// `comingSoon: true`; the decorate step below skips date formatting and the
// templates fall back to a "date to be announced" treatment.

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
      width: 1447,
      height: 1811,
    },
    funding:
      "Future Ghosts is supported by funding from The School of Languages, Literatures, Cultures & Linguistics, Monash University.",
  },
  {
    slug: "bodies-of-water",
    title: "Bodies of Water",
    tagline: "An evening of Poetry and Spoken Word @ The Count's",
    note: "Light refreshments provided. Drinks available at the bar",
    venue: "The Ian Potter Centre for Performing Arts",
    address: "48 Exhibition Walk, Clayton VIC 3168, Australia",
    mapLink:
      "https://www.google.com/maps/search/?api=1&query=48+Exhibition+Walk,+Clayton+VIC+3168,+Australia",
    start: "2026-10-15T18:00:00+11:00",
    end: "2026-10-15T20:00:00+11:00",
    poster: {
      image: "/images/bodies-of-water.webp",
      alt: "Bodies of Water — poetry and spoken word, over a painting of a river winding through marshland",
      width: 1000,
      height: 706,
    },
    funding:
      "Future Karaoke is supported by funding from The School of Languages, Literatures, Cultures & Linguistics, Monash University.",
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
  if (event.comingSoon) {
    // No date yet: nothing to format, and it's never "past".
    return { ...event, isComingSoon: true, isPast: false };
  }
  const start = new Date(event.start);
  const end = new Date(event.end);
  return {
    ...event,
    isComingSoon: false,
    startISO: event.start,
    dateLabel: dateFmt.format(start),
    timeLabel: `${timeFmt.format(start)} – ${timeFmt.format(end)}`,
    isPast: end.getTime() < Date.now(),
  };
}

module.exports = () => {
  const all = events.map(decorate).sort((a, b) => {
    // Dated events sort chronologically; undated "coming soon" events sort to
    // the end so a concrete date always takes precedence when featuring.
    if (a.isComingSoon || b.isComingSoon) {
      return (a.isComingSoon ? 1 : 0) - (b.isComingSoon ? 1 : 0);
    }
    return new Date(a.start) - new Date(b.start);
  });

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
