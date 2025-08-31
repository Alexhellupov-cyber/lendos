const container = document.querySelector(".gallery-container");
const images = document.querySelectorAll(".gallery-img");
const captionText = document.getElementById("caption-text");

let currentIndex = 0;

const captions = [
  "Підбор автомобіля",
  "Перевірка авто перед купівлею",
  "Пригін авто з Європи/США",
  "Консультація"
];

const prevBtn = document.getElementById("prev");
const nextBtn = document.getElementById("next");

function updateGallery() {
  container.style.transform = `translateX(${-currentIndex * 100}%)`;

  // Плавное исчезновение и появление текста
  captionText.style.opacity = 0;
  setTimeout(() => {
    captionText.textContent = captions[currentIndex];
    captionText.style.opacity = 1;
  }, 300);
}

prevBtn.addEventListener("click", () => {
  currentIndex--;
  if (currentIndex < 0) currentIndex = images.length - 1;
  updateGallery();
});

nextBtn.addEventListener("click", () => {
  currentIndex++;
  if (currentIndex >= images.length) currentIndex = 0;
  updateGallery();
});

// Автопереключение каждые 4 секунды
setInterval(() => {
  currentIndex++;
  if (currentIndex >= images.length) currentIndex = 0;
  updateGallery();
}, 4000);
