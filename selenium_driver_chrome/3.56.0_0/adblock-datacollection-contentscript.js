'use strict';

/* For ESLint: List any global identifiers used in this file below */
/* global chrome */

let pairs = [];
const matchSelectors = [];
const chunkSize = 1000;
function* genFunc() {
  let i = pairs.length;
  while (i > 0) {
    i -= 1;
    yield pairs.splice((-1 * chunkSize), chunkSize);
  }
}

chrome.runtime.sendMessage({ type: 'getSelectors' }).then((response) => {
  if (document.readyState !== 'loading') {
    pairs = response.selectors;

    const interval = setInterval(() => {
      const val = genFunc().next();
      if (val.done) {
        clearInterval(interval);
        if (matchSelectors.length > 0) {
          const noDuplicates = Array.from(new Set(matchSelectors)); // remove any duplicates
          chrome.runtime.sendMessage({
            type: 'datacollection.elementHide',
            selectors: noDuplicates,
          });
        }
      } else {
        const selectors = val.value;
        for (const selector of selectors) {
          for (const element of document.querySelectorAll(selector)) {
            // Only consider selectors that actually have an effect on the
            // computed styles, and aren't overridden by rules with higher
            // priority, or haven't been circumvented in a different way.
            if (getComputedStyle(element).display === 'none') {
              matchSelectors.push(selector);
            }
          }
        }
      }
    }, 10); // pause 10 milli-seconds between each chunck
  }
});
