/* ==================================================================
   PlainSheet — consent notice and Google Consent Mode v2 signals.

   Loaded synchronously in <head>, before anything that could set a
   cookie. It does three things:

     1. Declares every consent signal as denied before any tag runs.
     2. Asks the visitor once, and remembers the answer.
     3. Tells anything listening (assets/ads.js) what was decided.

   Nothing advertising-related is requested until a visitor says yes.
   ================================================================== */
(function () {
  'use strict';

  var cfg = (window.PLAINSHEET || {}).consent || {};
  var VERSION = cfg.version || 1;
  var REMEMBER_DAYS = cfg.remember || 180;
  var KEY = 'ps.consent';

  /* ---- Consent Mode v2 ------------------------------------------ */
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = window.gtag || gtag;

  gtag('consent', 'default', {
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied',
    analytics_storage: 'denied',
    functionality_storage: 'granted',
    security_storage: 'granted',
    wait_for_update: 1500
  });

  /* ---- Stored decision ------------------------------------------ */
  var memory = null;   /* used when localStorage is unavailable */

  function read() {
    var raw;
    try { raw = window.localStorage.getItem(KEY); } catch (e) { return memory; }
    if (!raw) return memory;
    var saved;
    try { saved = JSON.parse(raw); } catch (e) { return null; }
    if (!saved || saved.version !== VERSION) return null;
    var age = (Date.now() - (saved.time || 0)) / 86400000;
    if (age > REMEMBER_DAYS) return null;
    return saved;
  }

  function write(state) {
    memory = state;
    try { window.localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) { /* private mode */ }
  }

  function apply(state, announce) {
    var ads = state.ads ? 'granted' : 'denied';
    gtag('consent', 'update', {
      ad_storage: ads,
      ad_user_data: ads,
      ad_personalization: ads,
      analytics_storage: state.measurement ? 'granted' : 'denied'
    });
    api.state = state;
    if (announce !== false) {
      window.dispatchEvent(new CustomEvent('ps:consent', { detail: state }));
    }
  }

  function decide(ads, measurement) {
    var state = { version: VERSION, time: Date.now(), ads: !!ads, measurement: !!measurement };
    write(state);
    apply(state);
    close();
  }

  /* ---- The notice ------------------------------------------------ */
  var bar = null;

  var TEXT = {
    en: {
      label: 'Cookie choices',
      title: 'Advertising cookies',
      intro: 'The editor needs none: your resume never leaves your browser. The rest of the ' +
             'site is paid for by advertising, and our ad partner would like to store a ' +
             'cookie to measure and personalise what you see. Your call, changeable later ' +
             'on any page.',
      manage: 'Choose individually',
      reject: 'Reject',
      accept: 'Accept',
      save: 'Save my choice',
      privacy: 'Read the privacy notice',
      necessary: ['Strictly necessary',
                  'Remembering this choice, and the draft the editor keeps on your own ' +
                  'device. Never shared.'],
      ads: ['Advertising',
            'Lets our ad partner store an identifier so it can measure performance and ' +
            'personalise ads. Rejecting means no ads are loaded at all.'],
      measurement: ['Measurement',
                    'Aggregate statistics about which pages are read. Never used to build ' +
                    'a profile of you.'],
      href: 'privacy.html'
    },
    de: {
      label: 'Cookie-Auswahl',
      title: 'Cookies für Werbung',
      intro: 'Der Editor braucht keine: Ihr Lebenslauf verlässt Ihren Browser nicht. Die ' +
             'übrige Seite finanziert sich über Werbung, und unser Werbepartner möchte ' +
             'dafür ein Cookie setzen, um Werbung zu messen und zu personalisieren. Das ' +
             'entscheiden Sie — auf jeder Seite auch später wieder.',
      manage: 'Einzeln auswählen',
      reject: 'Ablehnen',
      accept: 'Zustimmen',
      save: 'Auswahl speichern',
      privacy: 'Zur Datenschutzerklärung',
      necessary: ['Unbedingt erforderlich',
                  'Diese Entscheidung und der Arbeitsstand, den der Editor auf Ihrem ' +
                  'eigenen Gerät behält. Wird nie geteilt.'],
      ads: ['Werbung',
            'Erlaubt unserem Werbepartner, eine Kennung zu setzen, um Werbung zu messen ' +
            'und zu personalisieren. Bei Ablehnung wird überhaupt keine Werbung geladen.'],
      measurement: ['Reichweitenmessung',
                    'Zusammengefasste Statistik darüber, welche Seiten gelesen werden. Nie ' +
                    'für ein Profil über Sie.'],
      href: 'datenschutz.html'
    }
  };

  function strings() {
    return TEXT[(document.documentElement.lang || 'en').slice(0, 2)] || TEXT.en;
  }

  /* data-root is written into every page by tools/build.py, so no guessing. */
  function root() {
    return document.documentElement.getAttribute('data-root') || '';
  }

  function privacyHref() {
    var t = strings();
    return root() + (t === TEXT.de ? 'de/' : '') + t.href;
  }

  function markup() {
    var t = strings();
    function option(cat, pair) {
      return '<label class="copt"><input type="checkbox" data-cat="' + cat + '">' +
             '<span><strong>' + pair[0] + '</strong>' + pair[1] + '</span></label>';
    }
    return [
      '<div class="cbar-in">',
      '<div><strong>' + t.title + '</strong><p>' + t.intro + '</p></div>',
      '<div class="cbar-btns">',
      '<button type="button" class="lnk" data-c="manage">' + t.manage + '</button>',
      '<button type="button" class="btn ghost" data-c="reject">' + t.reject + '</button>',
      '<button type="button" class="btn" data-c="accept">' + t.accept + '</button>',
      '</div>',
      '</div>',
      '<div class="cbar-detail" hidden>',
      '<div class="in">',
      '<label class="copt fixed"><input type="checkbox" checked disabled>',
      '<span><strong>' + t.necessary[0] + '</strong>' + t.necessary[1] + '</span></label>',
      option('ads', t.ads),
      option('measurement', t.measurement),
      '<span class="copt"><span><a href="' + privacyHref() + '">' + t.privacy + '</a><br>',
      '<button type="button" class="lnk" data-c="save">' + t.save + '</button></span></span>',
      '</div>',
      '</div>'
    ].join('');
  }

  function build() {
    if (bar) return bar;
    bar = document.createElement('aside');
    bar.className = 'cbar';
    bar.setAttribute('role', 'dialog');
    bar.setAttribute('aria-label', strings().label);
    bar.innerHTML = markup();
    bar.addEventListener('click', function (ev) {
      var what = ev.target.getAttribute && ev.target.getAttribute('data-c');
      if (!what) return;
      if (what === 'accept') return decide(true, true);
      if (what === 'reject') return decide(false, false);
      if (what === 'manage') {
        var panel = bar.querySelector('.cbar-detail');
        panel.hidden = !panel.hidden;
        if (!panel.hidden) panel.querySelector('input:not([disabled])').focus();
      }
      if (what === 'save') {
        decide(bar.querySelector('[data-cat="ads"]').checked,
               bar.querySelector('[data-cat="measurement"]').checked);
      }
    });
    document.body.appendChild(bar);
    return bar;
  }

  function open() {
    var el = build();
    var current = api.state;
    if (current) {
      el.querySelector('[data-cat="ads"]').checked = !!current.ads;
      el.querySelector('[data-cat="measurement"]').checked = !!current.measurement;
      el.querySelector('.cbar-detail').hidden = false;
    }
    el.hidden = false;
  }

  function close() { if (bar) bar.hidden = true; }

  /* ---- Public surface -------------------------------------------- */
  var api = {
    state: null,
    open: open,
    /** Call fn now if a decision exists, and again whenever it changes. */
    onChange: function (fn) {
      window.addEventListener('ps:consent', function (ev) { fn(ev.detail); });
      if (api.state) fn(api.state);
    },
    /** True when the visitor has agreed to advertising. */
    allowsAds: function () { return !!(api.state && api.state.ads); },
    /** Forget the decision and ask again. Handy while testing. */
    reset: function () {
      try { window.localStorage.removeItem(KEY); } catch (e) { /* ignore */ }
      memory = null;
      api.state = null;
      location.reload();
    }
  };
  window.Consent = api;

  function start() {
    var saved = read();
    if (saved) {
      apply(saved);
    } else {
      open();
    }
    /* Any element with data-consent-settings reopens the notice. */
    document.addEventListener('click', function (ev) {
      var trigger = ev.target.closest && ev.target.closest('[data-consent-settings]');
      if (trigger) { ev.preventDefault(); open(); }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
