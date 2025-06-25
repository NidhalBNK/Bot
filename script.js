const data = [
  { name: "تاجر ثقة", status: "trusted", note: "تعامل ممتاز" },
  { name: "نصاب_123", status: "fraud", note: "نصب وسرقة!" }
];

document.getElementById('searchInput').addEventListener('input', function() {
  const value = this.value.trim();
  const resultDiv = document.getElementById('result');
  resultDiv.innerHTML = '';

  if (value.length === 0) return;

  const person = data.find(entry => entry.name.includes(value));

  if (person) {
    const card = document.createElement('div');
    card.className = `card ${person.status}`;
    card.innerHTML = `<h2>${person.name}</h2><p>${person.note}</p>`;
    resultDiv.appendChild(card);
  } else {
    const card = document.createElement('div');
    card.className = 'card unknown';
    card.innerHTML = `<h2>غير مسجل</h2><p>لم يتم العثور على معلومات</p>`;
    resultDiv.appendChild(card);
  }
});
