(() => {
  const pagination = document.querySelector('[data-pagination]');
  const list = document.querySelector('[data-post-list]');

  if (!pagination || !list) {
    return;
  }

  const cards = Array.from(list.querySelectorAll('[data-post-card]'));
  const pageSize = Number.parseInt(pagination.dataset.pageSize || '10', 10);

  if (!Number.isFinite(pageSize) || pageSize < 1 || cards.length <= pageSize) {
    pagination.hidden = true;
    return;
  }

  const prevButton = pagination.querySelector('[data-page-prev]');
  const nextButton = pagination.querySelector('[data-page-next]');
  const pageNumbers = pagination.querySelector('[data-page-numbers]');

  if (!prevButton || !nextButton || !pageNumbers) {
    pagination.hidden = true;
    return;
  }

  const totalPages = Math.ceil(cards.length / pageSize);
  let currentPage = 1;
  const pageButtons = [];

  const setCardVisibility = () => {
    cards.forEach((card, index) => {
      const pageFromMarkup = Number.parseInt(card.dataset.page || '', 10);
      const cardPage = Number.isFinite(pageFromMarkup)
        ? pageFromMarkup
        : Math.floor(index / pageSize) + 1;

      const isVisible = cardPage === currentPage;
      card.classList.toggle('is-hidden-by-page', !isVisible);
      card.setAttribute('aria-hidden', String(!isVisible));
    });
  };

  const updateControls = () => {
    prevButton.disabled = currentPage === 1;
    nextButton.disabled = currentPage === totalPages;

    pageButtons.forEach((button, index) => {
      const pageNumber = index + 1;
      const isCurrent = pageNumber === currentPage;

      button.classList.toggle('is-active', isCurrent);

      if (isCurrent) {
        button.setAttribute('aria-current', 'page');
      } else {
        button.removeAttribute('aria-current');
      }
    });
  };

  const goToPage = (page, shouldScroll = true) => {
    const parsedPage = Number.parseInt(page, 10);

    if (!Number.isFinite(parsedPage)) {
      return;
    }

    currentPage = Math.min(Math.max(parsedPage, 1), totalPages);
    setCardVisibility();
    updateControls();

    if (shouldScroll) {
      list.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  for (let pageIndex = 1; pageIndex <= totalPages; pageIndex += 1) {
    const item = document.createElement('li');
    const button = document.createElement('button');

    button.type = 'button';
    button.className = 'pagination-page';
    button.textContent = String(pageIndex);
    button.setAttribute('aria-label', `Ver página ${pageIndex} de ${totalPages}`);
    button.addEventListener('click', () => goToPage(pageIndex));

    pageButtons.push(button);
    item.appendChild(button);
    pageNumbers.appendChild(item);
  }

  prevButton.addEventListener('click', () => goToPage(currentPage - 1));
  nextButton.addEventListener('click', () => goToPage(currentPage + 1));

  pagination.hidden = false;
  goToPage(1, false);
})();
