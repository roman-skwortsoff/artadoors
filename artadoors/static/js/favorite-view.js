// Открытие модального окна
function openModal(imageUrl) {
    const modal = document.getElementById("imageModal");
    const modalImage = document.getElementById("modalImage");
    modal.style.display = "flex"; // Устанавливаем Flexbox для отображения
    modalImage.src = imageUrl; // Задаём изображение
}

// Закрытие модального окна
function closeModal() {
    const modal = document.getElementById("imageModal");
    const modalImage = document.getElementById("modalImage");
    modal.style.display = "none"; // Скрываем модальное окно
    modalImage.src = ""; // Очищаем изображение
}