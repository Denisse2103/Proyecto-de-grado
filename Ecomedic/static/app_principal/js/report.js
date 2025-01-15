// app_principal/static/app_principal/js/report.js

document.addEventListener('DOMContentLoaded', function() {
    /**
     * Función para obtener el token CSRF desde el formulario oculto
     * @returns {string} Token CSRF
     */
    function getCSRFToken() {
        const csrfForm = document.getElementById('csrf-form');
        const csrfTokenInput = csrfForm ? csrfForm.querySelector('[name=csrfmiddlewaretoken]') : null;
        return csrfTokenInput ? csrfTokenInput.value : '';
    }

    /**
     * Función para inicializar los gráficos usando Chart.js
     */
    function initCharts() {
        // Datos para el gráfico de Consumo Energético
        const consumoCanvas = document.getElementById('consumoChart');
        const consumoPorDia = JSON.parse(consumoCanvas.getAttribute('data-consumo-por-dia'));
        const diasConsumo = parseInt(consumoCanvas.getAttribute('data-dias'), 10);

        // Generar etiquetas de días
        const etiquetasDias = [];
        for (let i = 1; i <= diasConsumo; i++) {
            etiquetasDias.push('Día ' + i);
        }

        // Configuración del Gráfico de Consumo Energético
        const ctxConsumo = consumoCanvas.getContext('2d');
        new Chart(ctxConsumo, {
            type: 'line',
            data: {
                labels: etiquetasDias,
                datasets: [{
                    label: 'Consumo Energético (kWh)',
                    data: consumoPorDia,
                    backgroundColor: 'rgba(0, 144, 118, 0.2)',
                    borderColor: 'rgba(0, 144, 118, 1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Consumo Energético (kWh)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Días'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Consumo Energético por Día'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                    },
                    legend: {
                        display: false
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        });

        // Datos para el gráfico de Emisiones de CO₂
        const emisionesCanvas = document.getElementById('emisionesChart');
        const emisionesPorDia = JSON.parse(emisionesCanvas.getAttribute('data-emisiones-por-dia'));
        const diasEmisiones = parseInt(emisionesCanvas.getAttribute('data-dias'), 10);

        // Generar etiquetas de días
        const etiquetasDiasEmisiones = etiquetasDias; // Usar las mismas etiquetas

        // Configuración del Gráfico de Emisiones de CO₂
        const ctxEmisiones = emisionesCanvas.getContext('2d');
        new Chart(ctxEmisiones, {
            type: 'line',
            data: {
                labels: etiquetasDiasEmisiones,
                datasets: [{
                    label: 'Emisiones de CO₂ (kg)',
                    data: emisionesPorDia,
                    backgroundColor: 'rgba(211, 47, 47, 0.2)',
                    borderColor: 'rgba(211, 47, 47, 1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Emisiones de CO₂ (kg)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Días'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Emisiones de CO₂ por Día'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                    },
                    legend: {
                        display: false
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        });
    }

    /**
     * Función para actualizar la lista de equipos basada en la sala seleccionada
     */
    function fetchEquipos() {
        const sala = document.getElementById('sala').value;
        if (!sala) {
            document.getElementById('equipos').innerHTML = '';
            return;
        }

        const csrfToken = getCSRFToken();

        fetch('/get-equipos/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: JSON.stringify({ sala }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            const equiposList = document.getElementById('equipos');
            equiposList.innerHTML = ''; // Limpiar la lista actual

            if (data.status === 'error') {
                equiposList.innerHTML = `<li>${data.message}</li>`;
            } else {
                if (data.equipos.length === 0) {
                    equiposList.innerHTML = '<li>No hay equipos para esta sala.</li>';
                } else {
                    data.equipos.forEach(equipo => {
                        equiposList.innerHTML += `<li>${equipo}</li>`;
                    });
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            const equiposList = document.getElementById('equipos');
            equiposList.innerHTML = '<li>Error al cargar equipos.</li>';
        });
    }

    /**
     * Función para generar el reporte
     */
    function generarReporte() {
        const sala = document.getElementById('sala').value;
        const fechaInicio = document.getElementById('fechaInicio').value;
        const fechaFin = document.getElementById('fechaFin').value;
        const horasPorDia = []; // Suponiendo que tienes inputs para cada día
        const numDias = parseInt(document.getElementById('numDias').value, 10); // Suponiendo que tienes un input para el número de días

        for (let i = 1; i <= numDias; i++) {
            const horasInput = document.getElementById(`horaDia${i}`);
            const horas = horasInput ? parseFloat(horasInput.value) : 0;
            horasPorDia.push(horas);
        }

        const csrfToken = getCSRFToken();

        // Validación básica
        if (!sala || !fechaInicio || !fechaFin || horasPorDia.length === 0) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Por favor, completa todos los campos.',
            });
            return;
        }

        fetch('/generar-reporte/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: JSON.stringify({ sala, fechaInicio, fechaFin, horasPorDia }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'error') {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: data.message,
                });
            } else {
                Swal.fire({
                    icon: 'success',
                    title: 'Éxito',
                    text: data.message,
                    timer: 2000,
                    showConfirmButton: false,
                }).then(() => {
                    // Redirigir a la URL de reporte
                    window.location.href = data.redirect_url;
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Ocurrió un problema. Inténtalo de nuevo más tarde.',
            });
        });
    }

    /**
     * Asignar eventos a los elementos del DOM
     */
    function assignEventListeners() {
        // Evento para cuando cambia la sala
        const salaSelect = document.getElementById('sala');
        if (salaSelect) {
            salaSelect.addEventListener('change', fetchEquipos);
        }

        // Evento para el botón de generación de reporte
        const generarBtn = document.getElementById('generarReporteBtn');
        if (generarBtn) {
            generarBtn.addEventListener('click', generarReporte);
        }
    }

    // Inicializar todo
    initCharts();
    assignEventListeners();
});
