/*
  This file is part of Wikipedia2Book
  <https://github.com/gmoulard/wikipedia2book>.
  Copyright (c) 2026 Guillaume Moulard.

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU Affero General Public License as published
  by the Free Software Foundation, version 3.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Affero General Public License for more details.

  You should have received a copy of the GNU Affero General Public License
  along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/

let installPrompt = null;

function installable() {
  return window.matchMedia('(pointer: coarse)').matches && !window.matchMedia('(display-mode: standalone)').matches && !navigator.standalone;
}

function isIos() {
  return /iphone|ipad|ipod/i.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
}

function setupInstallLink() {
  const button = document.getElementById('installButton');
  const hint = document.getElementById('installHint');
  if (!button || !installable()) return;
  window.addEventListener('beforeinstallprompt', (event) => {
    event.preventDefault();
    installPrompt = event;
    button.hidden = false;
  });
  window.addEventListener('appinstalled', () => { button.hidden = true; hint.hidden = true; });
  if (isIos()) button.hidden = false;
  button.addEventListener('click', async () => {
    if (!installPrompt) { hint.hidden = !hint.hidden; return; }
    installPrompt.prompt();
    const choice = await installPrompt.userChoice;
    installPrompt = null;
    if (choice.outcome === 'accepted') button.hidden = true;
  });
}

document.addEventListener('DOMContentLoaded', () => {
  applyTranslations();
  setupInstallLink();
  if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js').catch((error) => console.error('Service worker', error));
});
