// Splash screen all'apertura (presente solo in index.html, avvio della PWA)
const splash = document.getElementById('splash');
if (splash) {
  setTimeout(() => {
    splash.classList.add('hide');
    setTimeout(() => splash.remove(), 400);
  }, 2200);
}

// Registrazione service worker (offline-friendly per le pagine statiche) con
// aggiornamento automatico: quando una nuova versione prende il controllo,
// la pagina si ricarica da sola una volta sola, senza che l'utente debba
// chiudere e riaprire l'app manualmente.
if ('serviceWorker' in navigator) {
  let refreshing = false;
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    if (refreshing) return;
    refreshing = true;
    window.location.reload();
  });

  window.addEventListener('load', () => {
    navigator.serviceWorker.register('service-worker.js').then((reg) => {
      document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible') reg.update();
      });
    }).catch(() => {});
  });
}

// Copia testo (usato per l'IBAN) con fallback a selezione manuale
function copyText(sourceId, btnId) {
  const el = document.getElementById(sourceId);
  const btn = document.getElementById(btnId);
  const text = el.innerText.trim();
  const restore = () => setTimeout(() => { btn.innerText = btn.dataset.originalLabel; }, 1500);

  if (!btn.dataset.originalLabel) btn.dataset.originalLabel = btn.innerText;

  const fallbackSelect = () => {
    const range = document.createRange();
    range.selectNode(el);
    window.getSelection().removeAllRanges();
    window.getSelection().addRange(range);
    btn.innerText = 'SELEZIONATO';
    restore();
  };

  const writeAttempt = navigator.clipboard?.writeText(text) ?? Promise.reject();
  const timeout = new Promise((_, reject) => setTimeout(reject, 1200));

  Promise.race([writeAttempt, timeout]).then(() => {
    btn.innerText = 'COPIATO ✓';
    restore();
  }).catch(fallbackSelect);
}

// Samsung Internet spesso fallisce l'installazione PWA (bug noto del browser,
// non del sito) -- suggerisce di riaprire con Chrome, dove funziona.
if (/SamsungBrowser/i.test(navigator.userAgent)) {
  const note = document.getElementById('samsung-note');
  if (note) note.style.display = 'flex';
}

// Banner "Aggiungi a schermata Home" (Android/Chrome espone beforeinstallprompt; iOS/Safari no)
let deferredInstallPrompt = null;

window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredInstallPrompt = e;
  if (sessionStorage.getItem('installBannerDismissed')) return;
  document.getElementById('install-banner')?.classList.add('show');
});

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('install-btn')?.addEventListener('click', async () => {
    if (!deferredInstallPrompt) return;
    deferredInstallPrompt.prompt();
    await deferredInstallPrompt.userChoice;
    deferredInstallPrompt = null;
    document.getElementById('install-banner')?.classList.remove('show');
  });

  document.getElementById('install-dismiss')?.addEventListener('click', () => {
    sessionStorage.setItem('installBannerDismissed', '1');
    document.getElementById('install-banner')?.classList.remove('show');
  });
});
