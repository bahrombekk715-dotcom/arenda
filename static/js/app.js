const tg = window.Telegram.WebApp;
tg.expand();

let scooters = [];
let selectedScooter = null;
let selectedRentalType = null;

async function loadScooters() {
    try {
        const response = await fetch('/api/scooters');
        scooters = await response.json();
        displayScooters();
    } catch (error) {
        console.error('Skuterlarni yuklashda xatolik:', error);
        document.getElementById('scooters-grid').innerHTML =
            '<div class="loading">❌ Xatolik yuz berdi</div>';
    }
}

function displayScooters() {
    const grid = document.getElementById('scooters-grid');

    if (scooters.length === 0) {
        grid.innerHTML = '<div class="loading">Hozircha skuterlar yo\'q</div>';
        return;
    }

    grid.innerHTML = scooters.map(scooter => `
        <div class="scooter-card" onclick="openRentalModal(${scooter.id})">
            <div class="scooter-image">
                ${scooter.image_url ?
                    `<img src="${scooter.image_url}" alt="${scooter.name}" style="width:100%;height:100%;object-fit:cover;">` :
                    '🛴'
                }
            </div>
            <div class="scooter-info">
                <div class="scooter-name">${scooter.name}</div>
                <div class="scooter-model">${scooter.model}</div>
                <span class="status-badge ${scooter.status === 'rented' ? 'rented' : ''}">
                    ${scooter.status === 'available' ? '✓ Mavjud' : '✗ Ijarada'}
                </span>
                <div class="price-section">
                    <div class="price-item">
                        <div class="price-label">Haftalik</div>
                        <div class="price-value">${formatPrice(scooter.price_weekly)}</div>
                    </div>
                    <div class="price-item">
                        <div class="price-label">Oylik</div>
                        <div class="price-value">${formatPrice(scooter.price_monthly)}</div>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

function formatPrice(price) {
    return new Intl.NumberFormat('uz-UZ').format(price) + ' so\'m';
}

function openRentalModal(scooterId) {
    selectedScooter = scooters.find(s => s.id === scooterId);
    if (!selectedScooter) return;

    if (selectedScooter.status !== 'available') {
        tg.showAlert('❌ Bu skuter hozirda ijarada');
        return;
    }

    const modal = document.getElementById('rental-modal');
    const modalBody = document.getElementById('modal-body');

    modalBody.innerHTML = `
        <div class="modal-header">
            <h2>🛴 ${selectedScooter.name}</h2>
            <p style="color: var(--text-secondary);">${selectedScooter.model}</p>
        </div>

        <div class="info-section">
            <h3>📋 Ijara shartlari:</h3>
            <ul>
                <li>Pasport nusxasi talab qilinadi</li>
                <li>Shaxsiy foto yuklash kerak</li>
                <li>Skuter bilan video suratga olish</li>
                <li>To'lov oldindan amalga oshiriladi</li>
            </ul>
        </div>

        <div class="rental-options">
            <div class="rental-option" onclick="selectRentalType('weekly')">
                <div class="rental-option-header">
                    <span class="rental-type">📅 Haftalik ijara</span>
                    <span class="rental-price">${formatPrice(selectedScooter.price_weekly)}</span>
                </div>
                <div class="rental-description">7 kunlik ijara muddati</div>
            </div>

            <div class="rental-option" onclick="selectRentalType('monthly')">
                <div class="rental-option-header">
                    <span class="rental-type">📆 Oylik ijara</span>
                    <span class="rental-price">${formatPrice(selectedScooter.price_monthly)}</span>
                </div>
                <div class="rental-description">30 kunlik ijara muddati (Tejamkorroq!)</div>
            </div>
        </div>

        <button class="btn btn-primary btn-block" onclick="confirmRental()" id="confirm-btn" disabled>
            Ijarani tasdiqlash
        </button>
    `;

    modal.classList.add('show');
}

function selectRentalType(type) {
    selectedRentalType = type;

    document.querySelectorAll('.rental-option').forEach(option => {
        option.classList.remove('selected');
    });

    event.target.closest('.rental-option').classList.add('selected');
    document.getElementById('confirm-btn').disabled = false;
}

function confirmRental() {
    if (!selectedScooter || !selectedRentalType) return;

    const rentalData = {
        scooter_id: selectedScooter.id,
        scooter_name: selectedScooter.name,
        rental_type: selectedRentalType,
        price: selectedRentalType === 'weekly' ?
            selectedScooter.price_weekly :
            selectedScooter.price_monthly
    };

    tg.sendData(JSON.stringify(rentalData));
    tg.close();
}

function closeModal() {
    document.getElementById('rental-modal').classList.remove('show');
    selectedScooter = null;
    selectedRentalType = null;
}

document.querySelector('.close').addEventListener('click', closeModal);

window.onclick = function(event) {
    const modal = document.getElementById('rental-modal');
    if (event.target === modal) {
        closeModal();
    }
}

tg.ready();
tg.MainButton.setText('Orqaga qaytish');
tg.MainButton.onClick(() => tg.close());

loadScooters();
