// app_principal/static/app_principal/js/login.js

function showForm(formId) {
    // Oculta todos los formularios
    document.querySelectorAll(".form-section").forEach(section => {
        section.classList.add("hidden");
        section.style.display = "none";
    });
    // Muestra el formulario correspondiente
    const formToShow = document.getElementById(formId);
    if (formToShow) {
        formToShow.classList.remove("hidden");
        formToShow.style.display = "block";
    }
}

function submitSignup() {
    const persona_responsable = document.getElementById('persona_responsable').value;
    const institucion = document.getElementById('institucion').value;
    const area = document.getElementById('area').value;
    const usuario = document.getElementById('usuario').value;
    const password = document.getElementById('password').value;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/signup/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
        },
        body: JSON.stringify({ persona_responsable, institucion, area, usuario, password }),
    })
    .then(response => response.json())
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
                window.location.href = '/login/';
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

function submitLogin() {
    const usuario = document.getElementById('login-usuario').value;
    const password = document.getElementById('login-password').value;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
        },
        body: JSON.stringify({ usuario, password }),
    })
    .then(response => response.json())
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
                timer: 1000,
                showConfirmButton: false,
            }).then(() => {
                window.location.href = '/generate-report/';
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
