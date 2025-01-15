// app_principal/static/app_principal/js/manage_salas.js

document.addEventListener('DOMContentLoaded', function() {
    // Obtener elementos del DOM
    const addSalaBtn = document.getElementById('addSalaBtn');
    const deleteAllBtn = document.getElementById('deleteAllBtn');
    const addModal = document.getElementById('addModal');
    const editModal = document.getElementById('editModal');
    const closeButtons = document.querySelectorAll('.close-button');
    const addSalaForm = document.getElementById('addSalaForm');
    const editSalaForm = document.getElementById('editSalaForm');

    // Función para abrir el modal
    function openModal(modal) {
        modal.style.display = 'flex'; // Usar Flex para centrar
    }

    // Función para cerrar el modal
    function closeModal(modal) {
        modal.style.display = 'none';
    }

    // Manejar la apertura de los modales
    addSalaBtn.addEventListener('click', function() {
        openModal(addModal);
    });

    // Manejar la apertura del modal de edición usando delegación de eventos
    document.addEventListener('click', function(event) {
        if (event.target && event.target.classList.contains('edit-btn')) {
            const nombre = event.target.getAttribute('data-nombre');
            const cbaja = event.target.getAttribute('data-cbaja');
            const calta = event.target.getAttribute('data-calta');

            // Llenar el formulario de edición con los datos actuales
            document.getElementById('original_nombre').value = nombre;
            document.getElementById('edit_nombre').value = nombre;
            document.getElementById('edit_cbaja').value = cbaja;
            document.getElementById('edit_calta').value = calta;

            // Abrir el modal de edición
            openModal(editModal);
        }
    });

    // Manejar la eliminación de Salas individuales usando delegación de eventos
    document.addEventListener('click', function(event) {
        if (event.target && event.target.classList.contains('delete-btn')) {
            const nombre = event.target.getAttribute('data-nombre');

            Swal.fire({
                title: '¿Estás seguro?',
                text: `¿Quieres eliminar la sala "${nombre}"? Esta acción no se puede deshacer.`,
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
                    fetch('/api/delete-sala/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrftoken,
                            'X-Requested-With': 'XMLHttpRequest',
                        },
                        body: JSON.stringify({ nombre }),
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            // Eliminar la fila de la tabla
                            const row = document.getElementById(`sala-row-${nombre}`);
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
                            text: 'Ocurrió un problema al eliminar la sala.',
                        });
                    });
                }
            });
        }
    });

    // Manejar la eliminación de todas las Salas
    deleteAllBtn.addEventListener('click', function() {
        Swal.fire({
            title: '¿Estás seguro?',
            text: '¿Quieres eliminar **todas las salas**? Esta acción no se puede deshacer.',
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
                fetch('/api/delete-all-salas/', {
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
                        const tbody = document.querySelector('table tbody');
                        tbody.innerHTML = ''; // Limpiar el contenido del tbody

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
                        text: 'Ocurrió un problema al eliminar todas las salas.',
                    });
                });
            }
        });
    });

    // Manejar el cierre de los modales al hacer clic en el botón de cierre
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (this.parentElement.parentElement.id === 'addModal') {
                closeModal(addModal);
            } else if (this.parentElement.parentElement.id === 'editModal') {
                closeModal(editModal);
            }
        });
    });

    // Cerrar los modales al hacer clic fuera de ellos
    window.addEventListener('click', function(event) {
        if (event.target == addModal) {
            closeModal(addModal);
        }
        if (event.target == editModal) {
            closeModal(editModal);
        }
    });

    // Manejar el envío del formulario de agregar Sala
    addSalaForm.addEventListener('submit', function(event) {
        event.preventDefault();

        // Obtener los datos del formulario
        const nombre = document.getElementById('add_nombre').value.trim();
        const cbaja = document.getElementById('add_cbaja').value.trim();
        const calta = document.getElementById('add_calta').value.trim();

        // Validar los campos
        if (!nombre || !cbaja || !calta) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Por favor, completa todos los campos.',
            });
            return;
        }

        // Obtener el token CSRF desde la cookie
        const csrftoken = getCookie('csrftoken');

        // Enviar la solicitud de agregar Sala al backend
        fetch('/api/add-sala/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: JSON.stringify({ nombre, cbaja, calta }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Agregar la nueva Sala a la tabla
                const tbody = document.querySelector('table tbody');
                const newRow = document.createElement('tr');
                newRow.id = `sala-row-${nombre}`;

                newRow.innerHTML = `
                    <td>${nombre}</td>
                    <td>${cbaja}</td>
                    <td>${calta}</td>
                    <td class="action-buttons">
                        <button class="edit-btn" data-nombre="${nombre}" data-cbaja="${cbaja}" data-calta="${calta}">
                            Editar
                        </button>
                        <button class="delete-btn" data-nombre="${nombre}">Eliminar</button>
                    </td>
                `;

                tbody.appendChild(newRow);

                // Mostrar mensaje de éxito
                Swal.fire({
                    icon: 'success',
                    title: 'Éxito',
                    text: data.message,
                    timer: 2000,
                    showConfirmButton: false,
                });

                // Cerrar el modal y limpiar el formulario
                closeModal(addModal);
                addSalaForm.reset();
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
                text: 'Ocurrió un problema al agregar la sala.',
            });
        });
    });

    // Manejar el envío del formulario de editar Sala
    editSalaForm.addEventListener('submit', function(event) {
        event.preventDefault();

        // Obtener los datos del formulario
        const original_nombre = document.getElementById('original_nombre').value.trim();
        const nombre = document.getElementById('edit_nombre').value.trim();
        const cbaja = document.getElementById('edit_cbaja').value.trim();
        const calta = document.getElementById('edit_calta').value.trim();

        // Validar los campos
        if (!original_nombre || !nombre || !cbaja || !calta) {
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
        fetch('/api/edit-sala/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: JSON.stringify({ original_nombre, nombre, cbaja, calta }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Actualizar la fila en la tabla
                const row = document.getElementById(`sala-row-${original_nombre}`);
                if (row) {
                    row.id = `sala-row-${nombre}`; // Actualizar el ID si el nombre cambió
                    row.querySelector('td:nth-child(1)').innerText = nombre;
                    row.querySelector('td:nth-child(2)').innerText = cbaja;
                    row.querySelector('td:nth-child(3)').innerText = calta;

                    // Actualizar los atributos de los botones
                    const editBtn = row.querySelector('.edit-btn');
                    const deleteBtn = row.querySelector('.delete-btn');

                    editBtn.setAttribute('data-nombre', nombre);
                    editBtn.setAttribute('data-cbaja', cbaja);
                    editBtn.setAttribute('data-calta', calta);
                    deleteBtn.setAttribute('data-nombre', nombre);
                }

                Swal.fire({
                    icon: 'success',
                    title: 'Éxito',
                    text: data.message,
                    timer: 2000,
                    showConfirmButton: false,
                });

                // Cerrar el modal
                closeModal(editModal);
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
                text: 'Ocurrió un problema al editar la sala.',
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
});
