// app_principal/static/app_principal/js/manage_clasificacion_residuos.js

document.addEventListener('DOMContentLoaded', function() {
    // Obtener el elemento que contiene la URL de la API
    const container = document.querySelector('.container');
    const getResiduosURL = container.getAttribute('data-get-residuos-url');

    // Obtener elementos del DOM
    const addResiduoBtn = document.getElementById('addResiduoBtn');
    const deleteAllResiduosBtn = document.getElementById('deleteAllResiduosBtn');
    const addResiduoModal = document.getElementById('addResiduoModal');
    const editResiduoModal = document.getElementById('editResiduoModal');
    const closeButtons = document.querySelectorAll('.close-button');
    const addResiduoForm = document.getElementById('addResiduoForm');
    const editResiduoForm = document.getElementById('editResiduoForm');
    const residuosTableBody = document.getElementById('residuos_table_body');

    // Función para abrir el modal
    function openModal(modal) {
        modal.style.display = 'flex'; // Usar Flex para centrar
    }

    // Función para cerrar el modal
    function closeModal(modal) {
        modal.style.display = 'none';
    }

    // Función para limpiar la tabla de residuos
    function clearResiduosTable() {
        residuosTableBody.innerHTML = '';
    }

    // Función para cargar todas las clasificaciones de residuos
    function loadResiduos() {
        // Obtener el token CSRF desde la cookie
        const csrftoken = getCookie('csrftoken');

        // Enviar la solicitud para obtener residuos
        fetch(getResiduosURL, {  // Usar la URL obtenida desde el HTML
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: JSON.stringify({}),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const residuos = data.residuos;
                clearResiduosTable();

                if (residuos.length === 0) {
                    residuosTableBody.innerHTML = `
                        <tr>
                            <td colspan="3">No hay clasificaciones de residuos disponibles.</td>
                        </tr>
                    `;
                    return;
                }

                residuos.forEach(residuo => {
                    const row = document.createElement('tr');
                    row.id = `residuo-row-${residuo.nombre}`;

                    row.innerHTML = `
                        <td>${residuo.nombre}</td>
                        <td>${residuo.clasificacion}</td>
                        <td class="action-buttons">
                            <button class="edit-residuo-btn" data-nombre="${residuo.nombre}"
                                    data-clasificacion="${residuo.clasificacion}">Editar</button>
                            <button class="delete-residuo-btn" data-nombre="${residuo.nombre}">Eliminar</button>
                        </td>
                    `;

                    residuosTableBody.appendChild(row);
                });
            } else {
                clearResiduosTable();
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
                text: 'Ocurrió un problema al cargar las clasificaciones de residuos.',
            });
        });
    }

    // Manejar la apertura del modal para agregar
    addResiduoBtn.addEventListener('click', function() {
        openModal(addResiduoModal);
    });

    // Manejar la apertura del modal de edición usando delegación de eventos
    document.addEventListener('click', function(event) {
        if (event.target && event.target.classList.contains('edit-residuo-btn')) {
            const nombre = event.target.getAttribute('data-nombre');
            const clasificacion = event.target.getAttribute('data-clasificacion');

            // Llenar el formulario de edición con los datos actuales
            document.getElementById('original_nombre_residuo').value = nombre;
            document.getElementById('edit_nombre').value = nombre;
            document.getElementById('edit_clasificacion').value = clasificacion;

            // Abrir el modal de edición
            openModal(editResiduoModal);
        }
    });

    // Manejar la eliminación de residuos usando delegación de eventos
    document.addEventListener('click', function(event) {
        if (event.target && event.target.classList.contains('delete-residuo-btn')) {
            const nombre = event.target.getAttribute('data-nombre');

            Swal.fire({
                title: '¿Estás seguro?',
                text: `¿Quieres eliminar la clasificación de residuo "${nombre}"? Esta acción no se puede deshacer.`,
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
                    fetch('/api/delete-clasificacion-residuo/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrftoken,
                            'X-Requested-With': 'XMLHttpRequest',
                        },
                        body: JSON.stringify({ nombre }), // Incluir el nombre en la solicitud
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            // Eliminar la fila de la tabla
                            const row = document.getElementById(`residuo-row-${nombre}`);
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
                            text: 'Ocurrió un problema al eliminar la clasificación de residuo.',
                        });
                    });
                }
            });
        }
    });

    // Manejar la eliminación de todas las clasificaciones de residuos
    deleteAllResiduosBtn.addEventListener('click', function() {
        Swal.fire({
            title: '¿Estás seguro?',
            text: '¿Quieres eliminar **todas las clasificaciones de residuos**? Esta acción no se puede deshacer.',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Sí, eliminar todas',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                // Obtener el token CSRF desde la cookie
                const csrftoken = getCookie('csrftoken');

                // Enviar la solicitud de eliminación al backend
                fetch('/api/delete-all-clasificacion-residuos/', {
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
                        clearResiduosTable();

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
                        text: 'Ocurrió un problema al eliminar todas las clasificaciones de residuos.',
                    });
                });
            }
        });
    });

    // Manejar el cierre de los modales al hacer clic en el botón de cierre
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (this.parentElement.parentElement.id === 'addResiduoModal') {
                closeModal(addResiduoModal);
            } else if (this.parentElement.parentElement.id === 'editResiduoModal') {
                closeModal(editResiduoModal);
            }
        });
    });

    // Cerrar los modales al hacer clic fuera de ellos
    window.addEventListener('click', function(event) {
        if (event.target == addResiduoModal) {
            closeModal(addResiduoModal);
        }
        if (event.target == editResiduoModal) {
            closeModal(editResiduoModal);
        }
    });

    // Manejar el envío del formulario de agregar Clasificación de Residuo
    addResiduoForm.addEventListener('submit', function(event) {
        event.preventDefault();

        // Obtener los datos del formulario
        const nombre = document.getElementById('add_nombre').value.trim();
        const clasificacion = document.getElementById('add_clasificacion').value.trim();

        // Validar los campos
        if (!nombre || !clasificacion) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Por favor, completa todos los campos.',
            });
            return;
        }

        // Obtener el token CSRF desde la cookie
        const csrftoken = getCookie('csrftoken');

        // Enviar la solicitud de agregar Clasificación de Residuo al backend
        fetch('/api/add-clasificacion-residuo/', {  // Mantener la URL correcta
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: JSON.stringify({ nombre, clasificacion }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Recargar las clasificaciones de residuos
                loadResiduos();

                // Mostrar mensaje de éxito
                Swal.fire({
                    icon: 'success',
                    title: 'Éxito',
                    text: data.message,
                    timer: 2000,
                    showConfirmButton: false,
                });

                // Cerrar el modal y limpiar el formulario
                closeModal(addResiduoModal);
                addResiduoForm.reset();
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
                text: 'Ocurrió un problema al agregar la clasificación de residuo.',
            });
        });
    });

    // Manejar el envío del formulario de editar Clasificación de Residuo
    editResiduoForm.addEventListener('submit', function(event) {
        event.preventDefault();

        // Obtener los datos del formulario
        const original_nombre = document.getElementById('original_nombre_residuo').value.trim();
        const nombre = document.getElementById('edit_nombre').value.trim();
        const clasificacion = document.getElementById('edit_clasificacion').value.trim();

        // Validar los campos
        if (!original_nombre || !nombre || !clasificacion) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Por favor, completa todos los campos obligatorios.',
            });
            return;
        }

        // Obtener el token CSRF desde la cookie
        const csrftoken = getCookie('csrftoken');

        // Enviar la solicitud de edición al backend
        fetch('/api/edit-clasificacion-residuo/', {  // Mantener la URL correcta
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: JSON.stringify({
                original_nombre, nombre, clasificacion
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Recargar las clasificaciones de residuos
                loadResiduos();

                Swal.fire({
                    icon: 'success',
                    title: 'Éxito',
                    text: data.message,
                    timer: 2000,
                    showConfirmButton: false,
                });

                // Cerrar el modal
                closeModal(editResiduoModal);
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
                text: 'Ocurrió un problema al editar la clasificación de residuo.',
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

    // Cargar las clasificaciones de residuos al cargar la página
    loadResiduos();
});
