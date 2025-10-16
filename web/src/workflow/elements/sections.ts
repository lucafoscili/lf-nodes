export const createSection = {
  result: () => {
    const section = document.createElement('div');
    section.className = 'result-section';
    const h3 = document.createElement('h3');
    h3.textContent = 'Result';
    section.appendChild(h3);

    return section;
  },
};
