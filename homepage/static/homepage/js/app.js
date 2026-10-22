/* Фильтры меняют только видимость карточек, исходные JSON-данные сохраняются. */
"use strict";

(() => {
  const panel = document.querySelector("[data-request-filters]");
  const list = document.querySelector("[data-request-list]");
  if (!panel || !list) return;
  const cards = Array.from(list.querySelectorAll("[data-request-item]"));
  const search = panel.querySelector("[data-search-input]");
  const format = panel.querySelector("[data-format-input]");
  const active = panel.querySelector("[data-active-input]");
  const count = document.querySelector("[data-results-count]");
  const empty = document.querySelector("[data-no-results]");
  panel.hidden = cards.length === 0;
  const normalize = (value) => value.toLocaleLowerCase("ru").replaceAll("ё", "е");

  function update() {
    const words = normalize(search.value.trim()).split(/\s+/).filter(Boolean);
    let visible = 0;
    for (const card of cards) {
      const matches = words.every((word) => normalize(card.dataset.search).includes(word))
        && (!format.value || card.dataset.format === format.value)
        && (!active.checked || card.dataset.closed === "false");
      card.hidden = !matches;
      if (matches) visible += 1;
    }
    count.textContent = `Показано ${visible} из ${cards.length} запросов`;
    empty.hidden = visible !== 0 || cards.length === 0;
  }
  panel.addEventListener("input", update);
  panel.addEventListener("change", update);
  document.querySelectorAll("[data-reset-filters]").forEach((button) => {
    button.addEventListener("click", () => {
      search.value = "";
      format.value = "";
      active.checked = false;
      update();
      search.focus();
    });
  });
  update();
})();
