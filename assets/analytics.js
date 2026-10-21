/*
 * Personal site metrics: Google Analytics 4 + Yandex Metrika.
 * Dedicated counters for https://maxstrix324.github.io/.
 * Third-party analytics load only after explicit consent.
 */
(function () {
  "use strict";

  const CONFIG = {
    googleMeasurementId: "G-L18YE7WY1F", // Personal website GA4 measurement ID
    yandexCounterId: 113706082        // Personal website Yandex Metrika counter
  };
  const CONSENT_KEY = "maxstrix324-analytics-consent-v1";
  const gaId = /^G-[A-Z0-9]+$/.test(CONFIG.googleMeasurementId)
    ? CONFIG.googleMeasurementId : "";
  const ymId = Number.isSafeInteger(CONFIG.yandexCounterId) && CONFIG.yandexCounterId > 0
    ? CONFIG.yandexCounterId : 0;

  // Analytics is optional and completely inactive before configuration.
  if (!gaId && !ymId) return;

  let storedConsent = null;
  try { storedConsent = window.localStorage.getItem(CONSENT_KEY); }
  catch (_) { /* Browsers can disable localStorage. */ }
  let consentGranted = storedConsent === "granted";
  let started = false;

  function saveChoice(choice) {
    storedConsent = choice;
    try { window.localStorage.setItem(CONSENT_KEY, choice); }
    catch (_) { /* The session still follows the user's choice. */ }
  }

  function addScript(src) {
    const node = document.createElement("script");
    node.async = true;
    node.src = src;
    document.head.appendChild(node);
  }

  function startGoogle() {
    if (!gaId) return;
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
    // Basic Consent Mode v2: no Google tag is loaded before opt-in.
    window.gtag("consent", "default", {
      analytics_storage: "denied",
      ad_storage: "denied",
      ad_user_data: "denied",
      ad_personalization: "denied"
    });
    window.gtag("consent", "update", { analytics_storage: "granted" });
    window.gtag("js", new Date());
    window.gtag("config", gaId, {
      allow_google_signals: false,
      allow_ad_personalization_signals: false
    });
    addScript("https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(gaId));
  }

  function startYandex() {
    if (!ymId) return;
    window.ym = window.ym || function () {
      (window.ym.a = window.ym.a || []).push(arguments);
    };
    window.ym.l = Date.now();
    window.ym(ymId, "init", {
      clickmap: false,
      trackLinks: false,
      accurateTrackBounce: true,
      webvisor: false
    });
    addScript("https://mc.yandex.ru/metrika/tag.js?id=" + encodeURIComponent(String(ymId)));
  }

  function startAnalytics() {
    if (started || !consentGranted) return;
    started = true;
    startGoogle();
    startYandex();
  }

  function trackGitHubRepoClick(event) {
    if (!consentGranted || !started) return;
    const link = event.target.closest("a[href]");
    if (!link) return;
    let url;
    try { url = new URL(link.href, window.location.href); }
    catch (_) { return; }
    if (url.hostname.toLowerCase() !== "github.com") return;
    const parts = url.pathname.split("/").filter(Boolean);
    if (parts.length < 2 || parts[0].toLowerCase() !== "maxstrix324") return;
    const repository = parts[1];
    if (!/^[a-z0-9_.-]+$/i.test(repository)) return;
    if (gaId && typeof window.gtag === "function") {
      window.gtag("event", "github_repository_click", { repository: repository });
    }
    // Create an event goal called github_repository_click in the Yandex UI.
    if (ymId && typeof window.ym === "function") {
      window.ym(ymId, "reachGoal", "github_repository_click", { repository: repository });
    }
  }

  function makeConsentBanner() {
    const panel = document.createElement("div");
    panel.id = "analytics-consent";
    panel.className = "analytics-consent";
    panel.setAttribute("role", "region");
    panel.setAttribute("aria-label", "Настройки аналитики");
    panel.hidden = true;
    panel.innerHTML =
      '<div class="analytics-consent-inner">' +
        '<div><strong>Статистика посещений</strong><p>Можно разрешить Google Analytics и Яндекс.Метрику, чтобы видеть посещаемость сайта и интерес к проектам. Без согласия аналитика не загружается. <a href="/privacy/">Подробнее</a></p></div>' +
        '<div class="analytics-consent-actions">' +
          '<button type="button" data-consent="declined">Не разрешать</button>' +
          '<button type="button" class="analytics-consent-allow" data-consent="granted">Разрешить</button>' +
        '</div>' +
      '</div>';
    document.body.appendChild(panel);
    panel.addEventListener("click", function (event) {
      const button = event.target.closest("[data-consent]");
      if (!button) return;
      const next = button.getAttribute("data-consent");
      if (next !== "granted" && next !== "declined") return;
      const revoke = consentGranted && next === "declined";
      saveChoice(next);
      consentGranted = next === "granted";
      panel.hidden = true;
      if (consentGranted) startAnalytics();
      // Reload to stop already initialized scripts on withdrawal.
      if (revoke) window.location.reload();
    });
    if (!storedConsent) panel.hidden = false;

    const footerLinks = document.querySelector(".footer-links");
    if (footerLinks) {
      const settings = document.createElement("a");
      settings.href = "#analytics-consent";
      settings.textContent = "Настройки аналитики";
      settings.addEventListener("click", function (event) {
        event.preventDefault();
        panel.hidden = false;
        const firstButton = panel.querySelector("button");
        if (firstButton) firstButton.focus();
      });
      footerLinks.appendChild(settings);
    }
  }

  document.addEventListener("click", trackGitHubRepoClick, { passive: true });
  makeConsentBanner();
  if (consentGranted) startAnalytics();
}());
