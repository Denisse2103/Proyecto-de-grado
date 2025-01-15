// app_principal/static/app_principal/js/manage_pconsumo.js

function updatePConsumo() {
    const baja = document.getElementById("baja").value.trim();
    const alta = document.getElementById("alta").value.trim();
    const csrftoken = getCookie("csrftoken");

    fetch("/api/update-pconsumo/", {  // Asegúrate de que esta URL coincide con la definida en urls.py
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,
            "X-Requested-With": "XMLHttpRequest"
        },
        body: JSON.stringify({ baja: baja, alta: alta })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            Swal.fire({
                icon: "success",
                title: "Éxito",
                text: data.message
            });
        } else {
            Swal.fire({
                icon: "error",
                title: "Error",
                text: data.message
            });
        }
    })
    .catch(error => {
        console.error("Error:", error);
        Swal.fire({
            icon: "error",
            title: "Error",
            text: "Ocurrió un error al actualizar los datos."
        });
    });
}

// Helper function to obtener el token CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}