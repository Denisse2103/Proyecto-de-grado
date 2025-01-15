// app_principal/static/app_principal/js/manage_equipos.js

document.addEventListener('DOMContentLoaded', function() {
    // Obtener el elemento que contiene la URL de la API
    const container = document.querySelector('.container');
    const getEquiposURL = container.getAttribute('data-get-equipos-url');

    // Obtener elementos del DOM
    const selectSala = document.getElementById('select_sala');
    const addEquipoBtn = document.getElementById('addEquipoBtn');
    const deleteAllEquiposBtn = document.getElementById('deleteAllEquiposBtn');
    const addEquipoModal = document.getElementById('addEquipoModal');
    const editEquipoModal = document.getElementById('editEquipoModal');
    const closeButtons = document.querySelectorAll('.close-button');
    const addEquipoForm = document.getElementById('addEquipoForm');
    const editEquipoForm = document.getElementById('editEquipoForm');
    const equiposTableBody = document.getElementById('equipos_table_body');

    let currentSala = ''; // Variable para almacenar la Sala seleccionada

    // Función para abrir el modal
    function openModal(modal) {
        modal.style.display = 'flex'; // Usar Flex para centrar
    }

    // Función para cerrar el modal
    function closeModal(modal) {
        modal.style.display = 'none';
    }

    // Función para limpiar la tabla de equipos
    function clearEquiposTable() {
        equiposTableBody.innerHTML = '';
    }

    // Función para cargar equipos de una Sala específica
    function loadEquipos(sala) {
        if (!sala) {
            clearEquiposTable();
            return;
        }

        // Obtener el token CSRF desde la cookie
        const csrftoken = getCookie('csrftoken');

        // Enviar la solicitud para obtener equipos de la Sala
        fetch(getEquiposURL, {  // Usar la URL obtenida desde el HTML
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: JSON.stringify({ sala }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const equipos = data.equipos;
                clearEquiposTable();

                if (equipos.length === 0) {
                    equiposTableBody.innerHTML = `
                        <tr>
                            <td colspan="15">No hay equipos biomédicos asignados a esta Sala.</td>
                        </tr>
                    `;
                    return;
                }

                equipos.forEach(equipo => {
                    const row = document.createElement('tr');
                    row.id = `equipo-row-${equipo.nombre}`;

                    row.innerHTML = `
                        <td>${equipo.nombre}</td>
                        <td>${equipo.marca}</td>
                        <td>${equipo.modelo}</td>
                        <td>${equipo.serie}</td>
                        <td>${equipo.clasificacion_riesgo}</td>
                        <td>${equipo.registro_invima}</td>
                        <td>${equipo.lote}</td>
                        <td>${equipo.vida_util}</td>
                        <td>${equipo.voltaje}</td>
                        <td>${equipo.corriente}</td>
                        <td>${equipo.potencia}</td>
                        <td>${equipo.kwh}</td>
                        <td>${equipo.consumibles}</td>
                        <td>${equipo.accesorios}</td>
                        <td class="action-buttons">
                            <button class="edit-equipo-btn" data-nombre="${equipo.nombre}"
                                    data-marca="${equipo.marca}"
                                    data-modelo="${equipo.modelo}"
                                    data-serie="${equipo.serie}"
                                    data-clasificacion_riesgo="${equipo.clasificacion_riesgo}"
                                    data-registro_invima="${equipo.registro_invima}"
                                    data-lote="${equipo.lote}"
                                    data-vida_util="${equipo.vida_util}"
                                    data-voltaje="${equipo.voltaje}"
                                    data-corriente="${equipo.corriente}"
                                    data-potencia="${equipo.potencia}"
                                    data-kwh="${equipo.kwh}"
                                    data-consumibles="${equipo.consumibles}"
                                    data-accesorios="${equipo.accesorios}"
                                    data-salas="${equipo.salas}">Editar</button>
                            <button class="delete-equipo-btn" data-nombre="${equipo.nombre}" data-sala="${currentSala}">Eliminar</button>
                        </td>
                    `;

                    equiposTableBody.appendChild(row);
                });
            } else {
                clearEquiposTable();
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: data.message,
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Ocurrió un problema al cargar los equipos biomédicos.',
            });
        });
    }

    // Manejar la selección de Sala
    selectSala.addEventListener('change', function() {
        const salaSeleccionada = this.value;
        currentSala = salaSeleccionada;
        console.log('Sala seleccionada:', currentSala); // Depuración
        loadEquipos(salaSeleccionada);
    });

    // Manejar la apertura de los modales
    addEquipoBtn.addEventListener('click', function() {
        // Obtener las Salas seleccionadas en el selector principal
        const selectedSala = selectSala.value;

        if (!selectedSala) {
            Swal.fire({
                icon: 'warning',
                title: 'Atención',
                text: 'Por favor, selecciona una Sala antes de agregar un equipo.',
            });
            return;
        }

        openModal(addEquipoModal);
    });

    // Manejar la apertura del modal de edición usando delegación de eventos
    document.addEventListener('click', function(event) {
        if (event.target && event.target.classList.contains('edit-equipo-btn')) {
            const nombre = event.target.getAttribute('data-nombre');
            const marca = event.target.getAttribute('data-marca');
            const modelo = event.target.getAttribute('data-modelo');
            const serie = event.target.getAttribute('data-serie');
            const clasificacion_riesgo = event.target.getAttribute('data-clasificacion_riesgo');
            const registro_invima = event.target.getAttribute('data-registro_invima');
            const lote = event.target.getAttribute('data-lote');
            const vida_util = event.target.getAttribute('data-vida_util');
            const voltaje = event.target.getAttribute('data-voltaje');
            const corriente = event.target.getAttribute('data-corriente');
            const potencia = event.target.getAttribute('data-potencia');
            const kwh = event.target.getAttribute('data-kwh');
            const consumibles = event.target.getAttribute('data-consumibles');
            const accesorios = event.target.getAttribute('data-accesorios');
            const salas = event.target.getAttribute('data-salas'); // Ahora presente

            // Llenar el formulario de edición con los datos actuales
            document.getElementById('original_nombre_equipo').value = nombre;
            document.getElementById('edit_nombre').value = nombre;
            document.getElementById('edit_marca').value = marca;
            document.getElementById('edit_modelo').value = modelo;
            document.getElementById('edit_serie').value = serie;
            document.getElementById('edit_clasificacion_riesgo').value = clasificacion_riesgo;
            document.getElementById('edit_registro_invima').value = registro_invima;
            document.getElementById('edit_lote').value = lote;
            document.getElementById('edit_vida_util').value = vida_util;
            document.getElementById('edit_voltaje').value = voltaje;
            document.getElementById('edit_corriente').value = corriente;
            document.getElementById('edit_potencia').value = potencia;
            document.getElementById('edit_kwh').value = kwh;
            document.getElementById('edit_consumibles').value = consumibles;
            document.getElementById('edit_accesorios').value = accesorios;

            // Seleccionar las Salas asignadas
            const editSalasContainer = document.getElementById('edit_salas_container');
            const salasArray = salas.split(',').map(sala => sala.trim());
            for (let checkbox of editSalasContainer.querySelectorAll('input[name="salas"]')) {
                if (salasArray.includes(checkbox.value)) {
                    checkbox.checked = true;
                } else {
                    checkbox.checked = false;
                }
            }

            // Abrir el modal de edición
            openModal(editEquipoModal);
        }
    });

    // Manejar la eliminación de Equipos individuales usando delegación de eventos
    document.addEventListener('click', function(event) {
        if (event.target && event.target.classList.contains('delete-equipo-btn')) {
            const nombre = event.target.getAttribute('data-nombre');
            const sala = event.target.getAttribute('data-sala'); // Obtener la Sala desde el atributo data-sala

            // Depuración: Mostrar los valores en la consola
            console.log('Eliminar equipo:', nombre, 'de la Sala:', sala);

            if (!sala) {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'No se ha proporcionado una Sala para eliminar el equipo.',
                });
                return;
            }

            Swal.fire({
                title: '¿Estás seguro?',
                text: `¿Quieres eliminar el equipo biomédico "${nombre}" de la Sala "${sala}"? Esta acción no se puede deshacer.`,
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'Sí, eliminar',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    // Obtener el token CSRF desde la cookie
                    const csrftoken = getCookie('csrftoken');

                    // Enviar la solicitud de eliminación al backend
                    fetch('/api/delete-equipo/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrftoken,
                            'X-Requested-With': 'XMLHttpRequest',
                        },
                        body: JSON.stringify({ nombre, sala }), // Incluir la Sala en la solicitud
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            // Eliminar la fila de la tabla
                            const row = document.getElementById(`equipo-row-${nombre}`);
                            if (row) {
                                row.parentNode.removeChild(row);
                            }

                            Swal.fire({
                                icon: 'success',
                                title: 'Eliminado',
                                text: data.message,
                                timer: 2000,
                                showConfirmButton: false,
                            });
                        } else {
                            Swal.fire({
                                icon: 'error',
                                title: 'Error',
                                text: data.message,
                            });
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        Swal.fire({
                            icon: 'error',
                            title: 'Error',
                            text: 'Ocurrió un problema al eliminar el equipo biomédico.',
                        });
                    });
                }
            });
        }
    });

    // Manejar la eliminación de todos los Equipos Biomédicos
    deleteAllEquiposBtn.addEventListener('click', function() {
        Swal.fire({
            title: '¿Estás seguro?',
            text: '¿Quieres eliminar **todos los equipos biomédicos**? Esta acción no se puede deshacer.',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Sí, eliminar todos',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                // Obtener el token CSRF desde la cookie
                const csrftoken = getCookie('csrftoken');

                // Enviar la solicitud de eliminación al backend
                fetch('/api/delete-all-equipos/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken,
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    body: JSON.stringify({}), // No se necesitan datos adicionales
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        // Eliminar todas las filas de la tabla
                        clearEquiposTable();

                        Swal.fire({
                            icon: 'success',
                            title: 'Éxito',
                            text: data.message,
                            timer: 2000,
                            showConfirmButton: false,
                        });
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Error',
                            text: data.message,
                        });
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: 'Ocurrió un problema al eliminar todos los equipos biomédicos.',
                    });
                });
            }
        });
    });

    // Manejar el cierre de los modales al hacer clic en el botón de cierre
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (this.parentElement.parentElement.id === 'addEquipoModal') {
                closeModal(addEquipoModal);
            } else if (this.parentElement.parentElement.id === 'editEquipoModal') {
                closeModal(editEquipoModal);
            }
        });
    });

    // Cerrar los modales al hacer clic fuera de ellos
    window.addEventListener('click', function(event) {
        if (event.target == addEquipoModal) {
            closeModal(addEquipoModal);
        }
        if (event.target == editEquipoModal) {
            closeModal(editEquipoModal);
        }
    });

    // Manejar el envío del formulario de agregar Equipo Biomédico
    addEquipoForm.addEventListener('submit', function(event) {
        event.preventDefault();

        // Obtener los datos del formulario
        const nombre = document.getElementById('add_nombre').value.trim();
        const marca = document.getElementById('add_marca').value.trim();
        const modelo = document.getElementById('add_modelo').value.trim();
        const serie = document.getElementById('add_serie').value.trim();
        const clasificacion_riesgo = document.getElementById('add_clasificacion_riesgo').value.trim();
        const registro_invima = document.getElementById('add_registro_invima').value.trim();
        const lote = document.getElementById('add_lote').value.trim();
        const vida_util = document.getElementById('add_vida_util').value.trim();
        const voltaje = document.getElementById('add_voltaje').value.trim();
        const corriente = document.getElementById('add_corriente').value.trim();
        const potencia = document.getElementById('add_potencia').value.trim();
        const kwh = document.getElementById('add_kwh').value.trim();
        const consumibles = document.getElementById('add_consumibles').value.trim();
        const accesorios = document.getElementById('add_accesorios').value.trim();

        // Obtener los nuevos campos
        const consumibles_dia = document.getElementById('add_consumibles_dia').value.trim();
        const peso_kg = document.getElementById('add_peso_kg').value.trim();
        const clasificacion = document.getElementById('add_clasificacion').value.trim();

        // Obtener las Salas seleccionadas en el formulario de agregar
        const addSalasContainer = document.getElementById('add_salas_container');
        const selectedSalas = Array.from(addSalasContainer.querySelectorAll('input[name="salas"]:checked')).map(input => input.value);

        // Validar los campos
        if (!nombre || !marca || !modelo || !serie || !clasificacion_riesgo || !registro_invima ||
            !lote || !vida_util || !voltaje || !corriente || !potencia || !kwh ||
            !consumibles || !accesorios || !consumibles_dia || !peso_kg || !clasificacion) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Por favor, completa todos los campos.',
            });
            return;
        }

        if (selectedSalas.length === 0) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Por favor, selecciona al menos una Sala.',
            });
            return;
        }

        // Obtener el token CSRF desde la cookie
        const csrftoken = getCookie('csrftoken');

        // Enviar la solicitud de agregar Equipo Biomédico al backend
        fetch('/api/add-equipo/', {  // Mantener la URL correcta
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: JSON.stringify({
                nombre, marca, modelo, serie, clasificacion_riesgo,
                registro_invima, lote, vida_util, voltaje,
                corriente, potencia, kwh, consumibles,
                accesorios, salas: selectedSalas,
                consumibles_dia, peso_kg, clasificacion // Nuevos campos añadidos
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Recargar los equipos para la Sala actual
                loadEquipos(currentSala);

                // Mostrar mensaje de éxito
                Swal.fire({
                    icon: 'success',
                    title: 'Éxito',
                    text: data.message,
                    timer: 2000,
                    showConfirmButton: false,
                });

                // Cerrar el modal y limpiar el formulario
                closeModal(addEquipoModal);
                addEquipoForm.reset();

                // Desmarcar todas las Salas en el formulario
                addSalasContainer.querySelectorAll('input[name="salas"]').forEach(input => input.checked = false);
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: data.message,
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Ocurrió un problema al agregar el equipo biomédico.',
            });
        });
    });

    // Manejar el envío del formulario de editar Equipo Biomédico
    editEquipoForm.addEventListener('submit', function(event) {
        event.preventDefault();

        // Obtener los datos del formulario
        const original_nombre = document.getElementById('original_nombre_equipo').value.trim();
        const nombre = document.getElementById('edit_nombre').value.trim();
        const marca = document.getElementById('edit_marca').value.trim();
        const modelo = document.getElementById('edit_modelo').value.trim();
        const serie = document.getElementById('edit_serie').value.trim();
        const clasificacion_riesgo = document.getElementById('edit_clasificacion_riesgo').value.trim();
        const registro_invima = document.getElementById('edit_registro_invima').value.trim();
        const lote = document.getElementById('edit_lote').value.trim();
        const vida_util = document.getElementById('edit_vida_util').value.trim();
        const voltaje = document.getElementById('edit_voltaje').value.trim();
        const corriente = document.getElementById('edit_corriente').value.trim();
        const potencia = document.getElementById('edit_potencia').value.trim();
        const kwh = document.getElementById('edit_kwh').value.trim();
        const consumibles = document.getElementById('edit_consumibles').value.trim();
        const accesorios = document.getElementById('edit_accesorios').value.trim();

        // Obtener las Salas seleccionadas en el formulario de editar
        const editSalasContainer = document.getElementById('edit_salas_container');
        const selectedSalas = Array.from(editSalasContainer.querySelectorAll('input[name="salas"]:checked')).map(input => input.value);

        // Validar los campos
        if (!original_nombre || !nombre || !marca || !modelo || !serie || !clasificacion_riesgo || !registro_invima ||
            !lote || !vida_util || !voltaje || !corriente || !potencia || !kwh ||
            !consumibles || !accesorios) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Por favor, completa todos los campos obligatorios.',
            });
            return;
        }

        if (selectedSalas.length === 0) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Por favor, selecciona al menos una Sala.',
            });
            return;
        }

        // Obtener el token CSRF desde la cookie
        const csrftoken = getCookie('csrftoken');

        // Enviar la solicitud de edición al backend
        fetch('/api/edit-equipo/', {  // Mantener la URL correcta
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: JSON.stringify({
                original_nombre, nombre, marca, modelo, serie, clasificacion_riesgo,
                registro_invima, lote, vida_util, voltaje, corriente, potencia,
                kwh, consumibles, accesorios, salas: selectedSalas
                // Si decides incluir los nuevos campos en la edición, agrégalos aquí
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Recargar los equipos para la Sala actual
                loadEquipos(currentSala);

                Swal.fire({
                    icon: 'success',
                    title: 'Éxito',
                    text: data.message,
                    timer: 2000,
                    showConfirmButton: false,
                });

                // Cerrar el modal
                closeModal(editEquipoModal);
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: data.message,
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Ocurrió un problema al editar el equipo biomédico.',
            });
        });
    });

    // Función para obtener el valor de una cookie por su nombre
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Verificar si la cookie empieza con el nombre deseado
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Cargar equipos si hay una Sala preseleccionada (opcional)
    if (currentSala) {
        loadEquipos(currentSala);
    }
});
