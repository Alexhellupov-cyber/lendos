function enableZoom(img) {
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

  lens.addEventListener("mousemove", moveLens);
  img.addEventListener("mousemove", moveLens);

  lens.addEventListener("touchmove", moveLens);
  img.addEventListener("touchmove", moveLens);

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

    // позиция результата в зависимости от ширины экрана
    if (window.innerWidth <= 768) {
      // мобильная версия → слева сверху
      result.style.left = rect.left + "px";
      result.style.top = rect.top - result.offsetHeight - 10 + "px";
      result.style.position = "fixed";
    } else {
      // десктоп → справа снизу от курсора
      result.style.left = clientX + 20 + "px";
      result.style.top = clientY + 20 + "px";
      result.style.position = "fixed";
    }

    result.style.backgroundPosition = `-${x * cx}px -${y * cy}px`;
  }

  function removeZoom() {
    lens.remove();
    result.remove();
  }
}
