document.addEventListener('DOMContentLoaded', function () {
    // Элементы кнопок
    const descriptionTab = document.getElementById('description-tab');
    const characteristicsTab = document.getElementById('characteristics-tab');

    // Элементы контента
    const descriptionContent = document.getElementById('description-content');
    const characteristicsContent = document.getElementById('characteristics-content');

    // Функция переключения
    function switchTab(selectedTab) {
        if (selectedTab === 'description') {
            // Показать описание, скрыть характеристики
            descriptionContent.classList.add('visible');
            characteristicsContent.classList.remove('visible');
            descriptionTab.classList.add('active');
            characteristicsTab.classList.remove('active');
        } else if (selectedTab === 'characteristics') {
            // Показать характеристики, скрыть описание
            characteristicsContent.classList.add('visible');
            descriptionContent.classList.remove('visible');
            characteristicsTab.classList.add('active');
            descriptionTab.classList.remove('active');
        }
    }

    // Навешиваем обработчики событий
    descriptionTab.addEventListener('click', function () {
        switchTab('description');
    });

    characteristicsTab.addEventListener('click', function () {
        switchTab('characteristics');
    });

    // Устанавливаем начальное состояние (показ описания)
    switchTab('description');
});

document.getElementById('scroll-to-details').addEventListener('click', function() {
    const target = document.getElementById('product-details');
    const offset = 90; // Высота навигационной панели
    const targetPosition = target.getBoundingClientRect().top + window.scrollY; // Позиция элемента относительно всей страницы
    const offsetPosition = targetPosition - offset; // Вычитаем высоту панели

    window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth' // Плавная прокрутка
    });

    // Нажимаем на кнопку, чтобы переключить вкладку (добавляем небольшую задержку, если нужно)
    setTimeout(() => {
        document.getElementById('description-tab').click();
    }, 300); // Задержка 300 мс, чтобы скролл успел завершиться
});

document.getElementById('scroll-to-characteristics').addEventListener('click', function() {
    const target = document.getElementById('product-details');
    const offset = 90; // Высота фиксированной панели
    const targetPosition = target.getBoundingClientRect().top + window.scrollY;
    const offsetPosition = targetPosition - offset;

    // Скроллим до блока с учетом высоты панели
    window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
    });

    // Нажимаем на кнопку, чтобы переключить вкладку (добавляем небольшую задержку, если нужно)
    setTimeout(() => {
        document.getElementById('characteristics-tab').click();
    }, 300); // Задержка 300 мс, чтобы скролл успел завершиться
});


document.addEventListener("DOMContentLoaded", () => {
    const radioInputs = document.querySelectorAll('input[name="Открывание"]');
    const doorItems = document.querySelectorAll(".card-info-general-door__item");

    // Функция для управления классами
    function updateSelectedState() {
        // Сначала снимаем класс 'selected' у всех элементов
        doorItems.forEach(item => item.classList.remove("selected"));

        // Находим выбранную радиокнопку
        const selectedInput = document.querySelector('input[name="Открывание"]:checked');
        if (selectedInput) {
            const parentItem = selectedInput.closest(".door-option").querySelector(".card-info-general-door__item");
            if (parentItem) {
                parentItem.classList.add("selected");
            }
        }
    }

    // Навешиваем слушатель на каждую радиокнопку
    radioInputs.forEach(input => {
        input.addEventListener("change", updateSelectedState);
    });

    // Инициализируем состояние при загрузке страницы
    updateSelectedState();
});

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