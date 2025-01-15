// app_principal/static/app_principal/js/manage_users.js

document.addEventListener('DOMContentLoaded', function() {
    // Obtener elementos del DOM
    const editButtons = document.querySelectorAll('.edit-btn');
    const deleteButtons = document.querySelectorAll('.delete-btn');
    const deleteAllBtn = document.getElementById('deleteAllBtn'); // Nuevo botón
    const modal = document.getElementById('editModal');
    const closeButton = document.querySelector('.close-button');
    const editUserForm = document.getElementById('editUserForm');

    // Función para abrir el modal con los datos del usuario
    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            const usuario = this.getAttribute('data-usuario');
            const persona_responsable = this.getAttribute('data-persona_responsable');
            const institucion = this.getAttribute('data-institucion');
            const area = this.getAttribute('data-area');

            // Llenar el formulario con los datos actuales
            document.getElementById('original_usuario').value = usuario;
            document.getElementById('persona_responsable').value = persona_responsable;
            document.getElementById('institucion').value = institucion;
            document.getElementById('area').value = area;
            document.getElementById('usuario').value = usuario;
            document.getElementById('contraseña').value = ''; // Vaciar contraseña

            // Mostrar el modal
            modal.style.display = 'block';
        });
    });

    // Función para cerrar el modal
    closeButton.addEventListener('click', function() {
        modal.style.display = 'none';
    });

    // Cerrar el modal al hacer clic fuera de él
    window.addEventListener('click', function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    });

    // Manejar el envío del formulario de edición
    editUserForm.addEventListener('submit', function(event) {
        event.preventDefault();

        // Obtener los datos del formulario
        const original_usuario = document.getElementById('original_usuario').value;
        const persona_responsable = document.getElementById('persona_responsable').value;
        const institucion = document.getElementById('institucion').value;
        const area = document.getElementById('area').value;
        const usuario = document.getElementById('usuario').value;
        let contraseña = document.getElementById('contraseña').value;

        // Validar los campos (excepto contraseña si es '******')
        if (!persona_responsable || !institucion || !area || !usuario) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Por favor, completa todos los campos obligatorios.',
            });
            return;
        }

        // Si la contraseña es '******' o está vacía, no la enviamos para mantener la existente
        if (contraseña === '******' || contraseña.trim() === '') {
            contraseña = null;
        }

        // Obtener el token CSRF desde la cookie
        const csrftoken = getCookie('csrftoken');

        // Enviar la solicitud de edición al backend
        fetch('/api/edit-user/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: JSON.stringify({
                original_usuario,
                persona_responsable,
                institucion,
                area,
                usuario,
                contraseña,
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Actualizar la fila en la tabla
                const row = document.getElementById(`user-row-${original_usuario}`);
                row.id = `user-row-${usuario}`; // Actualizar el ID si el nombre de usuario cambió
                row.querySelector('td:nth-child(1)').innerText = persona_responsable;
                row.querySelector('td:nth-child(2)').innerText = institucion;
                row.querySelector('td:nth-child(3)').innerText = area;
                row.querySelector('td:nth-child(4)').innerText = usuario;
                // Contraseña permanece oculta

                // Actualizar los atributos de los botones
                row.querySelector('.edit-btn').setAttribute('data-usuario', usuario);
                row.querySelector('.edit-btn').setAttribute('data-persona_responsable', persona_responsable);
                row.querySelector('.edit-btn').setAttribute('data-institucion', institucion);
                row.querySelector('.edit-btn').setAttribute('data-area', area);
                row.querySelector('.delete-btn').setAttribute('data-usuario', usuario);

                Swal.fire({
                    icon: 'success',
                    title: 'Éxito',
                    text: data.message,
                    timer: 2000,
                    showConfirmButton: false,
                });

                // Cerrar el modal
                modal.style.display = 'none';
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
                text: 'Ocurrió un problema al editar el usuario.',
            });
        });
    });

    // Manejar la eliminación de usuarios individuales
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const usuario = this.getAttribute('data-usuario');

            Swal.fire({
                title: '¿Estás seguro?',
                text: `¿Quieres eliminar al usuario "${usuario}"? Esta acción no se puede deshacer.`,
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
                    fetch('/api/delete-user/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrftoken,
                            'X-Requested-With': 'XMLHttpRequest',
                        },
                        body: JSON.stringify({ usuario }),
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            // Eliminar la fila de la tabla
                            const row = document.getElementById(`user-row-${usuario}`);
                            row.parentNode.removeChild(row);

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
                            text: 'Ocurrió un problema al eliminar el usuario.',
                        });
                    });
                }
            });
        });
    });

    // Manejar la eliminación de todos los usuarios
    deleteAllBtn.addEventListener('click', function() {
        Swal.fire({
            title: '¿Estás seguro?',
            text: '¿Quieres eliminar **todos los usuarios**? Esta acción no se puede deshacer.',
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
                fetch('/api/delete-all-users/', {
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
                        text: 'Ocurrió un problema al eliminar todos los usuarios.',
                    });
                });
            }
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
