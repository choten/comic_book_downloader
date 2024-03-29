/*
 * This file is part of Adblock Plus <https://adblockplus.org/>,
 * Copyright (C) 2006-present eyeo GmbH
 *
 * Adblock Plus is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 3 as
 * published by the Free Software Foundation.
 *
 * Adblock Plus is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Adblock Plus.  If not, see <http://www.gnu.org/licenses/>.
 */

"use strict";

const {getMessage} = browser.i18n;

let lastFilterQuery = null;

browser.runtime.sendMessage({type: "types.get"})
  .then(filterTypes =>
  {
    const filterTypesElem = document.getElementById("filter-type");
    const filterStyleElem = document.createElement("style");
    for (const type of filterTypes)
    {
      filterStyleElem.innerHTML +=
        `#items[data-filter-type=${type}] tr:not([data-type=${type}])` +
        "{display: none;}";
      const optionNode = document.createElement("option");
      optionNode.appendChild(document.createTextNode(type));
      filterTypesElem.appendChild(optionNode);
    }
    document.body.appendChild(filterStyleElem);
  });

function generateFilter(request, domainSpecific)
{
  let filter = request.url.replace(/^[\w-]+:\/+(?:www\.)?/, "||");
  const options = [];

  if (request.type == "POPUP")
  {
    options.push("popup");

    if (request.url == "about:blank")
      domainSpecific = true;
  }

  if (request.type == "CSP")
    options.push("csp");

  if (domainSpecific)
    options.push("domain=" + request.docDomain);

  if (options.length > 0)
    filter += "$" + options.join(",");

  return filter;
}

function createActionButton(action, stringId, filter)
{
  const button = document.createElement("span");

  button.textContent = getMessage(stringId);
  button.classList.add("action");

  button.addEventListener("click", () =>
  {
    browser.runtime.sendMessage({
      type: "filters." + action,
      text: filter
    });
  }, false);

  return button;
}

function onUrlClick(event)
{
  if (event.button != 0)
    return;

  // Firefox doesn't support the openResource API yet
  if (!("openResource" in browser.devtools.panels))
    return;

  browser.devtools.panels.openResource(event.target.href);
  event.preventDefault();
}

function createRecord(request, filter, template)
{
  const row = document.importNode(template, true);
  row.dataset.type = request.type;

  row.querySelector(".domain").textContent = request.docDomain;
  row.querySelector(".type").textContent = request.type;

  const urlElement = row.querySelector("[data-i18n='devtools_request_url']");
  const actionWrapper = row.querySelector(".action-wrapper");

  if (request.url)
  {
    const originalUrl = urlElement.querySelector("[data-i18n-index='0']");
    originalUrl.classList.add("url");
    originalUrl.textContent = request.url;
    originalUrl.setAttribute("href", request.url);
    originalUrl.setAttribute("target", "_blank");

    if (request.type != "POPUP")
    {
      originalUrl.addEventListener("click", onUrlClick);
    }

    if (request.rewrittenUrl)
    {
      const rewrittenUrl = urlElement.querySelector("[data-i18n-index='1'");
      rewrittenUrl.classList.add("url-rewritten");
      rewrittenUrl.textContent = request.rewrittenUrl;
      rewrittenUrl.setAttribute("href", request.rewrittenUrl);
      rewrittenUrl.addEventListener("click", onUrlClick);
      rewrittenUrl.setAttribute("target", "_blank");
    }
    else
    {
      urlElement.innerHTML = "";
      urlElement.appendChild(originalUrl);
    }
  }
  else
  {
    urlElement.innerHTML = "&nbsp;";
  }

  if (filter)
  {
    const filterElement = row.querySelector(".filter");
    const originElement = row.querySelector(".origin");

    filterElement.textContent = filter.text;
    row.dataset.state = filter.whitelisted ? "whitelisted" : "blocked";

    if (filter.subscription)
      originElement.textContent = filter.subscription;
    else
    {
      if (filter.userDefined)
        originElement.textContent = getMessage("devtools_filter_origin_custom");
      else
        originElement.textContent = getMessage("devtools_filter_origin_none");

      originElement.classList.add("unnamed");
    }

    if (!filter.whitelisted && request.type != "ELEMHIDE")
    {
      actionWrapper.appendChild(createActionButton(
        "add", "devtools_action_unblock", "@@" + generateFilter(request, false)
      ));
    }

    if (filter.userDefined)
    {
      actionWrapper.appendChild(createActionButton(
        "remove", "devtools_action_remove", filter.text
      ));
    }
  }
  else
  {
    actionWrapper.appendChild(createActionButton(
      "add", "devtools_action_block",
      generateFilter(request, request.specificOnly)
    ));
  }

  if (lastFilterQuery && shouldFilterRow(row, lastFilterQuery))
    row.classList.add("filtered-by-search");

  return row;
}

function shouldFilterRow(row, query)
{
  const elementsToSearch = [
    row.getElementsByClassName("filter"),
    row.getElementsByClassName("origin"),
    row.getElementsByClassName("type"),
    row.getElementsByClassName("url")
  ];

  for (const elements of elementsToSearch)
  {
    for (const element of elements)
    {
      if (element.innerText.search(query) != -1)
        return false;
    }
  }
  return true;
}

function performSearch(table, query)
{
  for (const row of table.rows)
  {
    if (shouldFilterRow(row, query))
      row.classList.add("filtered-by-search");
    else
      row.classList.remove("filtered-by-search");
  }
}

function cancelSearch(table)
{
  for (const row of table.rows)
    row.classList.remove("filtered-by-search");
}

document.addEventListener("DOMContentLoaded", () =>
{
  const container = document.getElementById("items");
  const table = container.querySelector("tbody");
  const template = document.querySelector("template").content.firstElementChild;

  document.querySelector("[data-i18n='devtools_footer'] > a")
    .addEventListener("click", () =>
    {
      ext.devtools.inspectedWindow.reload();
    }, false);

  document.getElementById("filter-state").addEventListener("change", (event) =>
  {
    container.dataset.filterState = event.target.value;
  }, false);

  document.getElementById("filter-type").addEventListener("change", (event) =>
  {
    container.dataset.filterType = event.target.value;
  }, false);

  ext.onMessage.addListener((message) =>
  {
    switch (message.type)
    {
      case "add-record":
        table.appendChild(createRecord(message.request, message.filter,
                                       template));
        break;

      case "update-record":
        const oldRow = table.getElementsByTagName("tr")[message.index];
        const newRow = createRecord(message.request, message.filter, template);
        oldRow.parentNode.replaceChild(newRow, oldRow);
        newRow.classList.add("changed");
        container.classList.add("has-changes");
        break;

      case "remove-record":
        const row = table.getElementsByTagName("tr")[message.index];
        row.parentNode.removeChild(row);
        container.classList.add("has-changes");
        break;

      case "reset":
        table.innerHTML = "";
        container.classList.remove("has-changes");
        break;
    }
  });

  window.addEventListener("message", (event) =>
  {
    switch (event.data.type)
    {
      case "performSearch":
        performSearch(table, event.data.queryString);
        lastFilterQuery = event.data.queryString;
        break;
      case "cancelSearch":
        cancelSearch(table);
        lastFilterQuery = null;
        break;
    }
  });

  // Since Chrome 54 the themeName is accessible, for earlier versions we must
  // assume the default theme is being used.
  // https://bugs.chromium.org/p/chromium/issues/detail?id=608869
  const theme = ext.devtools.panels.themeName || "default";
  document.body.classList.add(theme);
}, false);
