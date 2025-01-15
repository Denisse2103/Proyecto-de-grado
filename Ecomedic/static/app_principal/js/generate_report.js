// app_principal/static/app_principal/js/generate_report.js

/**
 * Función para añadir días a una fecha.
 * @param {Date} date - La fecha inicial.
 * @param {number} days - Número de días a añadir.
 * @returns {Date} - La nueva fecha con los días añadidos.
 */
function addDays(date, days) {
    const result = new Date(date);
    result.setDate(result.getDate() + days);
    return result;
}

/**
 * Obtiene el token CSRF desde el formulario oculto.
 * @returns {string} - El token CSRF.
 */
function getCSRFToken() {
    const csrfForm = document.getElementById('csrf-form');
    const csrfTokenInput = csrfForm ? csrfForm.querySelector('[name=csrfmiddlewaretoken]') : null;
    return csrfTokenInput ? csrfTokenInput.value : '';
}

/**
 * Obtiene y muestra los equipos asociados a una sala seleccionada.
 */
function fetchEquipos() {
    const sala = document.getElementById('sala').value;
    const equiposList = document.getElementById('equipos');
    
    if (!sala) {
        equiposList.innerHTML = '';
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
        equiposList.innerHTML = '<li>Error al cargar equipos.</li>';
    });
}

/**
 * Genera el reporte enviando los datos al backend.
 */
function generarReporte() {
    const sala = document.getElementById('sala').value;
    const fechaInicio = document.getElementById('fechaInicio').value;
    const fechaFin = document.getElementById('fechaFin').value;
    const csrfToken = getCSRFToken();

    if (!sala || !fechaInicio || !fechaFin) {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Por favor, completa todos los campos.',
        });
        return;
    }

    // Validación adicional para asegurar que el rango de fechas no exceda 7 días
    const startDate = new Date(fechaInicio);
    const endDate = new Date(fechaFin);
    const diffTime = endDate - startDate;
    const diffDays = diffTime / (1000 * 60 * 60 * 24) + 1; // Inclusivo

    if (diffDays > 7) {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'El rango de fechas no puede exceder 7 días.',
        });
        return;
    }

    // Recolectar las horas por día
    const horasInputs = document.querySelectorAll('.hora-dia-input');
    let horasPorDia = [];

    try {
        horasInputs.forEach(input => {
            const horas = parseFloat(input.value);
            if (isNaN(horas) || horas < 0 || horas > 24) {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Por favor, ingresa un número válido de horas (0-24) para cada día.',
                });
                throw new Error('Horas por día inválidas');
            }
            horasPorDia.push(horas);
        });
    } catch (error) {
        // Error ya manejado en Swal
        return;
    }

    // Enviar los datos al backend
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
                text: 'Reporte generado con éxito.',
                timer: 2000,
                showConfirmButton: false,
            }).then(() => {
                // Redireccionar a la página del reporte
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
 * Limita la fechaFin basada en la fechaInicio y genera los inputs de horas por día.
 */
function limitFechaFin() {
    const fechaInicioInput = document.getElementById('fechaInicio');
    const fechaFinInput = document.getElementById('fechaFin');
    const horasContainer = document.getElementById('horas-container');

    fechaInicioInput.addEventListener('change', function() {
        const startDate = new Date(this.value);
        if (isNaN(startDate)) {
            fechaFinInput.min = '';
            fechaFinInput.max = '';
            fechaFinInput.disabled = true;
            horasContainer.innerHTML = ''; // Limpiar los inputs de horas
            return;
        }

        const maxEndDate = addDays(startDate, 6); // Máximo 6 días después de fechaInicio para total de 7 días

        // Formatear las fechas al formato YYYY-MM-DD
        const year = maxEndDate.getFullYear();
        const month = String(maxEndDate.getMonth() + 1).padStart(2, '0');
        const day = String(maxEndDate.getDate()).padStart(2, '0');
        const maxDateStr = `${year}-${month}-${day}`;

        // Establecer el mínimo y máximo permitido para fechaFin
        fechaFinInput.min = this.value; // No puede ser antes de fechaInicio
        fechaFinInput.max = maxDateStr; // No puede exceder fechaInicio +6 días
        fechaFinInput.value = this.value; // Inicializar fechaFin al valor de fechaInicio
        fechaFinInput.disabled = false;

        // Generar los inputs de horas por día para la fechaInicio seleccionada
        generarHorasPorDia(this.value, this.value);
    });

    fechaFinInput.addEventListener('change', function() {
        const startDate = new Date(fechaInicioInput.value);
        const endDate = new Date(this.value);
        if (isNaN(endDate)) {
            horasContainer.innerHTML = ''; // Limpiar los inputs de horas
            return;
        }

        const diffTime = endDate - startDate;
        const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24)) + 1; // Inclusivo

        if (diffDays > 7) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'El rango de fechas no puede exceder 7 días.',
            });
            this.value = fechaInicioInput.value; // Restablecer fechaFin al fechaInicio
            generarHorasPorDia(this.value, this.value);
            return;
        }

        // Generar los inputs de horas por día basados en el nuevo rango
        generarHorasPorDia(fechaInicioInput.value, this.value);
    });
}

/**
 * Genera dinámicamente los inputs de horas por día basados en el rango de fechas seleccionado.
 * @param {string} fechaInicio - La fecha de inicio en formato YYYY-MM-DD.
 * @param {string} fechaFin - La fecha de fin en formato YYYY-MM-DD.
 */
function generarHorasPorDia(fechaInicio, fechaFin) {
    const horasContainer = document.getElementById('horas-container');
    horasContainer.innerHTML = ''; // Limpiar cualquier input previo

    const startDate = new Date(fechaInicio);
    const endDate = new Date(fechaFin);

    // Calcular la cantidad de días
    const diffTime = endDate - startDate;
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24)) + 1; // Inclusivo

    for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
        const currentDate = new Date(d);
        const year = currentDate.getFullYear();
        const month = String(currentDate.getMonth() + 1).padStart(2, '0');
        const day = String(currentDate.getDate()).padStart(2, '0');
        const dateStr = `${year}-${month}-${day}`;

        // Crear el contenedor para cada día
        const div = document.createElement('div');
        div.classList.add('hora-dia');

        // Crear la etiqueta
        const label = document.createElement('label');
        label.setAttribute('for', `hora-${dateStr}`);
        label.textContent = `Horas para ${dateStr}:`;

        // Crear el input
        const input = document.createElement('input');
        input.type = 'number';
        input.id = `hora-${dateStr}`;
        input.name = `hora-${dateStr}`;
        input.min = '0';
        input.max = '24';
        input.step = '0.1';
        input.required = true;
        input.classList.add('hora-dia-input');

        // Opcional: Prellenar con un valor predeterminado, por ejemplo, 8
        input.value = '8';

        // Añadir la etiqueta y el input al contenedor
        div.appendChild(label);
        div.appendChild(input);

        // Añadir el contenedor al container principal
        horasContainer.appendChild(div);
    }
}

/**
 * Establece las fechas predeterminadas al cargar la página.
 */
function setDefaultDates() {
    const fechaInicioInput = document.getElementById('fechaInicio');
    const fechaFinInput = document.getElementById('fechaFin');

    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    const todayStr = `${year}-${month}-${day}`;

    fechaInicioInput.value = todayStr;

    const maxEndDate = addDays(today, 6); // Máximo 6 días después de fechaInicio para total de 7 días

    const maxYear = maxEndDate.getFullYear();
    const maxMonth = String(maxEndDate.getMonth() + 1).padStart(2, '0');
    const maxDay = String(maxEndDate.getDate()).padStart(2, '0');
    const maxDateStr = `${maxYear}-${maxMonth}-${maxDay}`;

    fechaFinInput.min = todayStr;
    fechaFinInput.max = maxDateStr;
    fechaFinInput.value = todayStr; // Por defecto, misma fecha que fechaInicio
    fechaFinInput.disabled = false;

    // Generar los inputs de horas por día inicialmente
    generarHorasPorDia(todayStr, todayStr);
}

/**
 * Inicializa las funciones al cargar la página.
 */
document.addEventListener('DOMContentLoaded', function() {
    setDefaultDates();
    limitFechaFin();
});
