
  // --- Цена ---
  var priceSlider = document.getElementById('priceSlider');
  noUiSlider.create(priceSlider, {
    start: [2790, 109990],
    connect: true,
    step: 500,
    range: { 'min': 0, 'max': 120000 }
  });
  var minPrice = document.getElementById('minPriceInput');
  var maxPrice = document.getElementById('maxPriceInput');
  priceSlider.noUiSlider.on('update', function(values, handle) {
    if (handle === 0) minPrice.value = Math.round(values[0]);
    else maxPrice.value = Math.round(values[1]);
  });
  minPrice.addEventListener('change', function() {
    priceSlider.noUiSlider.set([this.value, null]);
  });
  maxPrice.addEventListener('change', function() {
    priceSlider.noUiSlider.set([null, this.value]);
  });

  // --- Год выпуска ---
  var yearSlider = document.getElementById('yearSlider');
  noUiSlider.create(yearSlider, {
    start: [1990, 2025],
    connect: true,
    step: 1,
    range: { 'min': 1990, 'max': 2025 }
  });
  var minYear = document.getElementById('minYearInput');
  var maxYear = document.getElementById('maxYearInput');
  yearSlider.noUiSlider.on('update', function(values, handle) {
    if (handle === 0) minYear.value = Math.round(values[0]);
    else maxYear.value = Math.round(values[1]);
  });
  minYear.addEventListener('change', function() {
    yearSlider.noUiSlider.set([this.value, null]);
  });
  maxYear.addEventListener('change', function() {
    yearSlider.noUiSlider.set([null, this.value]);
  });

  // --- Пробег ---
  var mileageSlider = document.getElementById('mileageSlider');
  noUiSlider.create(mileageSlider, {
    start: [0, 300000],
    connect: true,
    step: 1000,
    range: { 'min': 0, 'max': 300000 }
  });
  var minMileage = document.getElementById('minMileageInput');
  var maxMileage = document.getElementById('maxMileageInput');
  mileageSlider.noUiSlider.on('update', function(values, handle) {
    if (handle === 0) minMileage.value = Math.round(values[0]);
    else maxMileage.value = Math.round(values[1]);
  });
  minMileage.addEventListener('change', function() {
    mileageSlider.noUiSlider.set([this.value, null]);
  });
  maxMileage.addEventListener('change', function() {
    mileageSlider.noUiSlider.set([null, this.value]);
  });

  function applyFilter() {
  const minPrice = parseInt(document.getElementById("minPriceInput").value);
  const maxPrice = parseInt(document.getElementById("maxPriceInput").value);
  const minYear = parseInt(document.getElementById("minYearInput").value);
  const maxYear = parseInt(document.getElementById("maxYearInput").value);
  const minMileage = parseInt(document.getElementById("minMileageInput").value);
  const maxMileage = parseInt(document.getElementById("maxMileageInput").value);

  const cards = document.querySelectorAll(".catalog-grid .card");

  cards.forEach(card => {
    let visible = true;

    // --- цена ---

    let priceText = card.querySelector(".price")?.innerText || "";
    priceText = priceText
      .replace(/\s/g, "")        // убираем все пробелы (обычные, неразрывные, узкие и т.п.)
      .replace(/[^\d]/g, "");    // убираем всё, что не цифры
    const price = parseInt(priceText, 10) || 0;
    if (price < minPrice || price > maxPrice) visible = false;


    // --- год выпуска ---
    const yearMatch = card.innerText.match(/\b(19|20)\d{2}\b/);
    const year = yearMatch ? parseInt(yearMatch[0]) : 0;
    if (year < minYear || year > maxYear) visible = false;

    // --- пробег ---
    const mileageMatch = card.innerText.match(/\d{1,6}(?=\s*км)/);
    const mileage = mileageMatch ? parseInt(mileageMatch[0]) : 0;
    if (mileage < minMileage || mileage > maxMileage) visible = false;

    // --- показываем / скрываем ---
    card.style.display = visible ? "block" : "none";
  });
}


function resetFilter() {
  // Сброс цены
  priceSlider.noUiSlider.set([0, 200000]);
  document.getElementById("minPriceInput").value = 0;
  document.getElementById("maxPriceInput").value = 200000;

  // Сброс года
  yearSlider.noUiSlider.set([1990, 2025]);
  document.getElementById("minYearInput").value = 1990;
  document.getElementById("maxYearInput").value = 2025;

  // Сброс пробега
  mileageSlider.noUiSlider.set([0, 300000]);
  document.getElementById("minMileageInput").value = 0;
  document.getElementById("maxMileageInput").value = 300000;

  // Показать все карточки
  const cards = document.querySelectorAll(".catalog-grid .card");
  cards.forEach(card => card.style.display = "block");
}

function toggleFilter() {
  const mobileFilter = document.querySelector('.filters-mobile');
  mobileFilter.classList.toggle('active');
}

  function toggleFilter() {
    const filter = document.querySelector('.filters-mobile');
    filter.classList.toggle('active');
  }

  // Инициализация ползунков noUiSlider
  function initSliders() {
    const priceSlider = document.getElementById('priceSlider');
    const yearSlider = document.getElementById('yearSlider');
    const mileageSlider = document.getElementById('mileageSlider');

    noUiSlider.create(priceSlider, {
      start: [2790, 109990],
      connect: true,
      range: { min: 0, max: 120000 },
      tooltips: [true, true],
      orientation: 'horizontal'
    });

    noUiSlider.create(yearSlider, {
      start: [1990, 2025],
      connect: true,
      range: { min: 1990, max: 2025 },
      tooltips: [true, true],
      orientation: 'horizontal'
    });

    noUiSlider.create(mileageSlider, {
      start: [0, 300000],
      connect: true,
      range: { min: 0, max: 300000 },
      tooltips: [true, true],
      orientation: 'horizontal'
    });
  }

  window.addEventListener('DOMContentLoaded', initSliders);


  // Подключаем noUiSlider через CDN
// <script src="https://cdnjs.cloudflare.com/ajax/libs/noUiSlider/15.7.0/nouislider.min.js"></script>

function initMobileSliders() {
  const priceSlider = document.getElementById('priceSliderMobile');
  noUiSlider.create(priceSlider, {
    start: [2790, 109990],
    connect: true,
    step: 500,
    range: { min: 0, max: 120000 },
    orientation: 'horizontal'
  });

  priceSlider.noUiSlider.on('update', function(values){
    document.getElementById('minPriceMobile').value = Math.round(values[0]);
    document.getElementById('maxPriceMobile').value = Math.round(values[1]);
  });

  const yearSlider = document.getElementById('yearSliderMobile');
  noUiSlider.create(yearSlider, {
    start: [1990, 2025],
    connect: true,
    step: 1,
    range: { min: 1990, max: 2025 },
    orientation: 'horizontal'
  });

  yearSlider.noUiSlider.on('update', function(values){
    document.getElementById('minYearMobile').value = Math.round(values[0]);
    document.getElementById('maxYearMobile').value = Math.round(values[1]);
  });

  const mileageSlider = document.getElementById('mileageSliderMobile');
  noUiSlider.create(mileageSlider, {
    start: [0, 300000],
    connect: true,
    step: 1000,
    range: { min: 0, max: 300000 },
    orientation: 'horizontal'
  });

  mileageSlider.noUiSlider.on('update', function(values){
    document.getElementById('minMileageMobile').value = Math.round(values[0]);
    document.getElementById('maxMileageMobile').value = Math.round(values[1]);
  });
}

// Инициализация при загрузке страницы
window.addEventListener('DOMContentLoaded', initMobileSliders);

// Функция показа/скрытия фильтра
function toggleFilter() {
  document.getElementById('mobileFilters').classList.toggle('active');
}
