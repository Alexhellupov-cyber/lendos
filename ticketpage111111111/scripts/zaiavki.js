document.getElementById('contact-form').addEventListener('submit', function(e) {
  e.preventDefault();

  const name = document.querySelector('input[placeholder="Ваше имя"]').value;
  const phone = document.querySelector('input[placeholder="Телефон"]').value;
  const message = document.querySelector('textarea').value;

  // достаем название авто из блока main-photo
  const carTitle = document.querySelector('.main-photo h2').innerText;

  const BOT_TOKEN = "8224864234:AAHIaDFNrCNuA_dqwJlHXLUUaBhPy8XUXEc";
  const CHAT_ID = "542079843";


 const text = `🚗 Автомобиль: ${carTitle}\n\n👤 Имя: ${name}\n📞 Телефон: ${phone}\n💬 Сообщение: ${message}`;

  fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id: CHAT_ID,
      text: text,
      parse_mode: "HTML"
    })
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById('contact-form').classList.add('hidden');
    document.getElementById('thank-you').classList.remove('hidden');
  })
  .catch(err => {
    alert("Ошибка отправки: " + err);
  });
});