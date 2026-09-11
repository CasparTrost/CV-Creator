/* ==================================================================
   PlainSheet — advertising slots.

   Reads assets/site-config.js, waits for assets/consent.js, and fills
   every <div class="ad" data-slot="…"> on the page.

   Three states a slot can be in:

     ad     a real ad unit, once the visitor accepted advertising and
            a publisher ID and unit ID are configured
     house  our own promo, when ads are off, unconfigured or rejected;
            keeps the page looking finished instead of showing a hole
     empty  hidden entirely, when the placement is switched off

   Slots are only filled as they approach the viewport. An ad nobody
   scrolls to is an impression nobody sees, and unseen impressions are
   what drag a publisher's viewability score down.
   ================================================================== */
(function () {
  'use strict';

  var cfg = (window.PLAINSHEET || {}).ads || {};
  var slotIds = cfg.slots || {};
  var scriptRequested = false;
  var housesShown = 0;

  function depth() {
    return /\/(templates|guides|examples)\//.test(location.pathname) ? '../' : '';
  }

  /* ---- House promo ----------------------------------------------- */
  var HOUSE = [
    {
      href: 'editor.html',
      mark: 'PS',
      title: 'Write your resume here, free',
      text: 'Sixteen layouts, a live A4 page, and a PDF at the end. No account.'
    },
    {
      href: 'templates.html',
      mark: '16',
      title: 'Sixteen layouts to start from',
      text: 'Single column for employer portals, sidebar for a human reader.'
    },
    {
      href: 'guides/index.html',
      mark: '¶',
      title: 'How to write the thing',
      text: 'Plain guides to bullet points, skills, length and applicant tracking.'
    }
  ];

  function house(box, index) {
    /* One is a useful pointer; three on a page is begging. The rest of the
       slots collapse so the page reads as finished rather than unsold. */
    if (housesShown >= 1) {
      box.setAttribute('data-state', 'empty');
      return;
    }
    housesShown += 1;
    var promo = HOUSE[index % HOUSE.length];
    var a = document.createElement('a');
    a.className = 'ad-house';
    a.href = depth() + promo.href;
    a.innerHTML = '<span class="ic" aria-hidden="true">' + promo.mark + '</span>' +
                  '<span><strong>' + promo.title + '</strong>' +
                  '<span>' + promo.text + '</span></span>';
    box.appendChild(a);
    box.setAttribute('data-state', 'house');
  }

  /* ---- Real ad units --------------------------------------------- */
  function loadAdSense() {
    if (scriptRequested) return;
    scriptRequested = true;
    var s = document.createElement('script');
    s.async = true;
    s.crossOrigin = 'anonymous';
    s.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=' +
            encodeURIComponent(cfg.client);
    document.head.appendChild(s);
  }

  function unit(box, slotName) {
    loadAdSense();
    var ins = document.createElement('ins');
    ins.className = 'adsbygoogle';
    ins.setAttribute('data-ad-client', cfg.client);
    if (slotIds[slotName]) ins.setAttribute('data-ad-slot', slotIds[slotName]);
    ins.setAttribute('data-ad-format', box.getAttribute('data-format') || 'auto');
    ins.setAttribute('data-full-width-responsive', 'true');
    box.appendChild(ins);
    box.setAttribute('data-state', 'ad');
    try {
      (window.adsbygoogle = window.adsbygoogle || []).push({});
    } catch (e) {
      box.setAttribute('data-state', 'house');
      box.removeChild(ins);
    }
  }

  /* ---- Deciding what a slot gets --------------------------------- */
  function fill(box, index) {
    if (box.getAttribute('data-state')) return;          /* already handled */
    var name = box.getAttribute('data-slot') || '';
    var canServe = cfg.enabled && cfg.client &&
                   (window.Consent ? window.Consent.allowsAds() : false);

    if (!canServe && cfg.enabled && cfg.client && cfg.serveAfterReject &&
        window.Consent && window.Consent.state) {
      canServe = true;                                   /* explicitly opted in by the operator */
    }

    box.textContent = '';
    if (canServe) {
      var label = document.createElement('small');
      label.textContent = 'advertisement';
      box.appendChild(label);
      unit(box, name);
    } else if (cfg.enabled === false) {
      box.setAttribute('data-state', 'empty');
    } else {
      house(box, index);
    }
  }

  function watch() {
    var boxes = [].slice.call(document.querySelectorAll('.ad[data-slot]'));
    if (!boxes.length) return;

    if (!('IntersectionObserver' in window)) {
      boxes.forEach(fill);
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        io.unobserve(entry.target);
        fill(entry.target, boxes.indexOf(entry.target));
      });
    }, { rootMargin: (cfg.lazyMargin || 500) + 'px 0px' });
    boxes.forEach(function (box) { io.observe(box); });
  }

  /* ---- Measurement ----------------------------------------------- */
  function analytics() {
    var a = (window.PLAINSHEET || {}).analytics || {};
    if (!a.provider || a.provider === 'none' || !a.id) return;

    if (a.provider === 'plausible') {
      /* Cookieless and aggregate, so it does not wait on consent. */
      var p = document.createElement('script');
      p.defer = true;
      p.setAttribute('data-domain', a.id);
      p.src = 'https://plausible.io/js/script.js';
      document.head.appendChild(p);
      return;
    }
    if (a.provider === 'ga4') {
      /* Cookie-based, so it waits for the measurement category. */
      var started = false;
      window.Consent && window.Consent.onChange(function (state) {
        if (started || !state.measurement) return;
        started = true;
        var g = document.createElement('script');
        g.async = true;
        g.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(a.id);
        document.head.appendChild(g);
        window.gtag('js', new Date());
        window.gtag('config', a.id, { anonymize_ip: true });
      });
    }
  }

  function start() {
    watch();
    analytics();
    /* A late yes should fill the slots that are already on screen. */
    if (window.Consent) {
      window.Consent.onChange(function () {
        if (!(window.Consent.allowsAds() && cfg.enabled && cfg.client)) return;
        housesShown = 0;
        document.querySelectorAll('.ad[data-slot]').forEach(function (box) {
          var state = box.getAttribute('data-state');
          if (state === 'house' || state === 'empty') {
            box.removeAttribute('data-state');
            fill(box, 0);
          }
        });
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
