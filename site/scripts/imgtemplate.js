document.addEventListener("DOMContentLoaded", () => {
  const gallery = document.querySelector('.gallery-thumb');
  if (!gallery) return;

  // Получаем все прямые изображения внутри
  const images = Array.from(gallery.querySelectorAll('img'));

  images.forEach(img => {
    const wrapper = document.createElement('div');
    wrapper.classList.add('gallery-item');

    // Перемещаем изображение в wrapper
    img.parentNode.insertBefore(wrapper, img);
    wrapper.appendChild(img);
  });
});
