document.addEventListener('DOMContentLoaded', function () {
    const sizeSelect = document.querySelector('#size-select');
    const handleSelect = document.querySelector('#handle-select');
    const thresholdSelectYes = document.querySelector('#threshold-yes');
    const thresholdSelectNo = document.querySelector('#threshold-no');
    const apertureSize = document.getElementById('aperture-size');
    const boxSize = document.getElementById('box-size');
    const glassSize = document.getElementById('glass-size');
    const handleName = document.getElementById('handle-name');
    const thresholdCell = document.getElementById('threshold');
    const airSupplyCell = document.getElementById('air-supply');
    const openingSideRadios = document.querySelectorAll('input[name="Открывание"]');
    const openingSideCell = document.getElementById('opening-side');

    let addThreshold = false; // Переменная для отслеживания выбора порога

    // Обработчик выбора порога
    function updateThresholdDetails() {
        const isThreshold = thresholdSelectYes.checked;

        // Обновляем значение "Порог" в таблице
        thresholdCell.textContent = isThreshold ? 'с порогом' : 'без порога';

        // Обновляем значение "Приточка воздуха" в таблице
        airSupplyCell.textContent = isThreshold ? '15-20мм' : '20мм';
    }

    // Добавляем обработчики событий
    thresholdSelectYes.addEventListener('change', updateThresholdDetails);
    thresholdSelectNo.addEventListener('change', updateThresholdDetails);

    // Инициализация значений при загрузке страницы
    updateThresholdDetails();

    // Обработчик выбора стороны открывания
    function updateOpeningSide() {
        const selectedSide = Array.from(openingSideRadios).find(radio => radio.checked);
        if (selectedSide) {
            // Обновляем значение "Открывание" в таблице
            openingSideCell.textContent = selectedSide.value;
        }
    }

    // Добавляем обработчики событий для стороны открывания
    openingSideRadios.forEach(radio => radio.addEventListener('change', updateOpeningSide));

    // Инициализация значений при загрузке страницы для стороны открывания
    updateOpeningSide();

    function updateCharacteristics(size) {
        if (!size) {
            apertureSize.textContent = '—';
            boxSize.textContent = '—';
            glassSize.textContent = '—';
            return;
        }

        try {
            const [width, height] = size.split('*').map(Number);
            if (isNaN(width) || isNaN(height)) {
                throw new Error('Invalid size format');
            }

            const boxWidth = width - 10 + (addThreshold ? 10 : 0); // Учитываем порог
            const boxHeight = height - 10;
            const glassWidth = width - 75;
            const glassHeight = height - 100;

            apertureSize.textContent = `${width}*${height} мм`;
            boxSize.textContent = `${boxWidth}*${boxHeight} мм`;
            glassSize.textContent = `${glassWidth}*${glassHeight} мм`;
        } catch (error) {
            console.error('Error parsing size:', error);
            apertureSize.textContent = 'Ошибка';
            boxSize.textContent = 'Ошибка';
            glassSize.textContent = 'Ошибка';
        }
    }

    function updateHandleName(handle) {
        handleName.textContent = handle ? handle : '—';
    }

    // Обработчик изменения размера
    sizeSelect.addEventListener('change', function () {
        const selectedOption = sizeSelect.options[sizeSelect.selectedIndex];
        const size = selectedOption.getAttribute('data-size');
        updateCharacteristics(size);
    });

    // Обработчик изменения ручки
    handleSelect.addEventListener('change', function () {
        const selectedOption = handleSelect.options[handleSelect.selectedIndex];
        const handle = selectedOption.getAttribute('data-name');
        updateHandleName(handle);
    });

    // Обработчик выбора порога
    function updateThreshold() {
        addThreshold = thresholdSelectYes.checked; // Проверяем, выбрано ли "Да"
        const selectedOption = sizeSelect.options[sizeSelect.selectedIndex];
        if (selectedOption) {
            const size = selectedOption.getAttribute('data-size');
            updateCharacteristics(size);
        }
    }

    thresholdSelectYes.addEventListener('change', updateThreshold);
    thresholdSelectNo.addEventListener('change', updateThreshold);

    // Инициализация характеристик при загрузке страницы
    const selectedSizeOption = sizeSelect.options[sizeSelect.selectedIndex];
    if (selectedSizeOption) {
        const size = selectedSizeOption.getAttribute('data-size');
        updateCharacteristics(size);
    }

    const selectedHandleOption = handleSelect.options[handleSelect.selectedIndex];
    if (selectedHandleOption) {
        const handle = selectedHandleOption.getAttribute('data-name');
        updateHandleName(handle);
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const basePrice = parseFloat(document.getElementById('base-price').value);
    const sizeSelect = document.getElementById('size-select');
    const handleSelect = document.getElementById('handle-select');
    const thresholdRadios = document.querySelectorAll('input[name="Порог"]');
    const totalPriceElement = document.getElementById('total-price');

    // Функция для пересчета цены
    function updateTotalPrice() {
        let totalPrice = basePrice;

        // Добавляем увеличение цены за размер
        const selectedSize = sizeSelect.options[sizeSelect.selectedIndex];
        if (selectedSize) {
            const sizePriceIncrease = parseFloat(selectedSize.getAttribute('data-price-increase')) || 0;
            totalPrice += sizePriceIncrease;
        }

        // Добавляем увеличение цены за ручку
        const selectedHandle = handleSelect.options[handleSelect.selectedIndex];
        if (selectedHandle) {
            const handlePriceIncrease = parseFloat(selectedHandle.getAttribute('data-price-increase')) || 0;
            totalPrice += handlePriceIncrease;
        }

        // Добавляем стоимость порога
        const selectedThreshold = Array.from(thresholdRadios).find(radio => radio.checked);
        if (selectedThreshold) {
            const thresholdPriceIncrease = parseFloat(selectedThreshold.getAttribute('data-price-increase')) || 0;
            totalPrice += thresholdPriceIncrease;
        }

        // Обновляем цену на странице
        totalPriceElement.textContent = totalPrice.toFixed(0); // Округляем до целого числа
    }

    // Добавляем обработчики событий для пересчета цены
    sizeSelect.addEventListener('change', updateTotalPrice);
    handleSelect.addEventListener('change', updateTotalPrice);
    thresholdRadios.forEach(radio => radio.addEventListener('change', updateTotalPrice));

    // Инициализация цены при загрузке страницы
    updateTotalPrice();
});