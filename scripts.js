document.getElementById('contact-form').addEventListener('submit', function(e) {
  e.preventDefault();
  document.getElementById('contact-form').classList.add('hidden');
  document.getElementById('thank-you').classList.remove('hidden');
});


function changeImage(el) {
  const mainImage = document.getElementById("main-image");
  mainImage.src = el.src;

  // включаем лупу только при выборе миниатюры
  enableZoom(mainImage);
}

function enableZoom(img) {
  // Убираем старые элементы
  document.querySelectorAll(".img-zoom-lens, .img-zoom-result").forEach(el => el.remove());

  const lens = document.createElement("div");
  lens.classList.add("img-zoom-lens");

  const result = document.createElement("div");
  result.classList.add("img-zoom-result");

  img.parentElement.appendChild(lens);
  img.parentElement.appendChild(result);

  const cx = result.offsetWidth / lens.offsetWidth;
  const cy = result.offsetHeight / lens.offsetHeight;

  result.style.backgroundImage = `url('${img.src}')`;
  result.style.backgroundSize = `${img.width * cx}px ${img.height * cy}px`;

  // события мыши
  lens.addEventListener("mousemove", moveLens);
  img.addEventListener("mousemove", moveLens);

  // события для тач
  lens.addEventListener("touchmove", moveLens);
  img.addEventListener("touchmove", moveLens);

  // скрытие лупы при выходе
  img.addEventListener("mouseleave", removeZoom);
  img.addEventListener("touchend", removeZoom);

  function moveLens(e) {
    e.preventDefault();

    let clientX, clientY;
    if (e.type.includes("touch")) {
      clientX = e.touches[0].clientX;
      clientY = e.touches[0].clientY;
    } else {
      clientX = e.clientX;
      clientY = e.clientY;
    }

    const rect = img.getBoundingClientRect();
    let x = clientX - rect.left - lens.offsetWidth / 2;
    let y = clientY - rect.top - lens.offsetHeight / 2;

    if (x < 0) x = 0;
    if (y < 0) y = 0;
    if (x > img.width - lens.offsetWidth) x = img.width - lens.offsetWidth;
    if (y > img.height - lens.offsetHeight) y = img.height - lens.offsetHeight;

    lens.style.left = x + "px";
    lens.style.top = y + "px";

    result.style.left = clientX + 20 + "px";
    result.style.top = clientY + 20 + "px";
    result.style.position = "fixed";

    result.style.backgroundPosition = `-${x * cx}px -${y * cy}px`;
  }

  function removeZoom() {
    lens.remove();
    result.remove();
  }
}
