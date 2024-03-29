'use strict';

/* For ESLint: List any global identifiers used in this file below */
/* global chrome */

// Binds keypress enter to trigger click action on
// default button or trigger click action on focused
// button.
function bindEnterClickToDefault($dialog) {
  if (window.GLOBAL_BIND_ENTER_CLICK_TO_DEFAULT) {
    return;
  }
  window.GLOBAL_BIND_ENTER_CLICK_TO_DEFAULT = true;
  $('html').bind('keypress', (e) => {
    if (e.keyCode === 13 && $('button:focus').size() <= 0) {
      e.preventDefault();
      $dialog.find('.adblock-default-button').filter(':visible').click();
    }
  });
}

// Set RTL for Arabic and Hebrew users in blacklist and whitelist wizards
function setTextDirection($dialog) {
  const langRTL = ('ar', 'he');
  const lang = navigator.language.match(/^[a-z]+/i)[0];
  const textDirection = langRTL.includes(lang) ? 'rtl' : 'ltr';
  $dialog.attr('dir', textDirection);
}

// Inputs:
//   - $base : jQuery Element to attach the CSS as children
//   - callback : function to call when loading is complete
function loadWizardResources($base, callback) {
  function loadCss(src) {
    const url = chrome.extension.getURL(src);
    const link = $('<link rel="stylesheet" type="text/css" />')
      .attr('href', url)
      .addClass('adblock-ui-stylesheet');
    $base.append(link);
  }

  function loadFont(name, style, weight, unicodeRange) {
    return new FontFace('Lato', `url(${chrome.extension.getURL(`/fonts/${name}.woff`)}`, { style, weight, unicodeRange });
  }

  loadCss('adblock-uiscripts-adblock-wizard.css');

  // load fonts programmatically
  // Referencing the fonts in CSS do not load the fonts properly (reason unknown)
  // but programmatically loading them performs reliably.
  const fonts = [];
  fonts.push(loadFont('lato-regular', 'normal', 'normal', 'U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD'));
  fonts.push(loadFont('lato-ext-regular', 'normal', 'normal', 'U+0100-024F, U+0259, U+1E00-1EFF, U+2020, U+20A0-20AB, U+20AD-20CF, U+2113, U+2C60-2C7F, U+A720-A7FF'));
  fonts.push(loadFont('lato-ext-italic', 'italic', 'normal', 'U+0100-024F, U+0259, U+1E00-1EFF, U+2020, U+20A0-20AB, U+20AD-20CF, U+2113, U+2C60-2C7F, U+A720-A7FF'));
  fonts.push(loadFont('lato-italic', 'italic', 'normal', 'U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD'));
  fonts.push(loadFont('lato-ext-bolditalic', 'italic', 'bold', 'U+0100-024F, U+0259, U+1E00-1EFF, U+2020, U+20A0-20AB, U+20AD-20CF, U+2113, U+2C60-2C7F, U+A720-A7FF'));
  fonts.push(loadFont('lato-bolditalic', 'italic', 'bold', 'U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD'));
  fonts.push(loadFont('lato-ext-bold', 'normal', 'bold', 'U+0100-024F, U+0259, U+1E00-1EFF, U+2020, U+20A0-20AB, U+20AD-20CF, U+2113, U+2C60-2C7F, U+A720-A7FF'));
  fonts.push(loadFont('lato-bold', 'normal', 'bold', 'U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD'));
  fonts.push(new FontFace('Material Icons', `url(${chrome.extension.getURL('/icons/MaterialIcons-Regular.woff2')}`, { style: 'normal', weight: 'normal' }));
  fonts.push(new FontFace('AdBlock Icons', `url(${chrome.extension.getURL('/icons/adblock-icons.woff2')}`, { style: 'normal', weight: 'normal' }));

  Promise.all(fonts).then((loaded) => {
    for (let i = 0; i < loaded.length; i++) {
      // documents.fonts supported in Chrome 60+ and documents.fonts.add() is experimental
      // https://developer.mozilla.org/en-US/docs/Web/API/FontFaceSet#Browser_compatibility
      // https://developer.mozilla.org/en-US/docs/Web/API/Document/fonts#Browser_compatibility
      document.fonts.add(loaded[i]);
    }
    callback();
  }).catch(() => {
    callback();
  });
}

// required return value for tabs.executeScript
/* eslint-disable-next-line no-unused-expressions */
'';

//# sourceURL=/uiscripts/load_wizard_resources.js
