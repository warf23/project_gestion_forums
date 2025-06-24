document.addEventListener('DOMContentLoaded', () => {

    // --- Modal Logic ---
    window.openModal = function(modalId) {
        document.getElementById(modalId).classList.remove('hidden');
        document.getElementById(modalId).classList.add('flex');
    }

    window.closeModal = function(modalId) {
        document.getElementById(modalId).classList.add('hidden');
        document.getElementById(modalId).classList.remove('flex');
    }
    
    // Close modal on outside click
    document.querySelectorAll('.fixed.inset-0').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal(modal.id);
            }
        });
    });


    // --- Stand Map Interaction ---
    const standGrid = document.getElementById('standGrid');
    const modalStandIdEl = document.getElementById('modalStandId');
    const modalReservationSelect = document.getElementById('modalReservationSelect');
    const confirmStandReservationBtn = document.getElementById('confirmStandReservationBtn');
    let selectedStandId = null;

    standGrid.addEventListener('click', (e) => {
        const stand = e.target.closest('.stand');
        // Only act on available stands (those without the 'cursor-not-allowed' class)
        if (stand && !stand.classList.contains('cursor-not-allowed')) {
            selectedStandId = stand.dataset.id;
            modalStandIdEl.textContent = selectedStandId;
            openModal('reserveStandModal');
        }
    });

    confirmStandReservationBtn.addEventListener('click', () => {
        const reservationId = modalReservationSelect.value;

        if (!reservationId) {
            Swal.fire({
                icon: 'error',
                title: 'Oups...',
                text: 'Veuillez sélectionner une réservation à assigner.',
            });
            return;
        }

        fetch('/admin/reserve_stand', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                reservation_id: reservationId,
                stand_id: selectedStandId,
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'Succès !',
                    text: data.message,
                }).then(() => {
                    // Reload the page to see the changes
                    window.location.reload();
                });
            } else {
                 Swal.fire({
                    icon: 'error',
                    title: 'Erreur',
                    text: data.message || 'Une erreur est survenue.',
                });
            }
        });
    });
});