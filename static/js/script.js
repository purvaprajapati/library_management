// Global JavaScript & jQuery helper functions for Library Management System

$(document).ready(function () {
    // CSRF helper for jQuery AJAX requests
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken') || $('input[name="csrfmiddlewaretoken"]').val();

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    // Auto-dismiss alerts after 5 seconds
    setTimeout(function () {
        $(".alert-dismissible").fadeOut("slow");
    }, 5000);
});

// Utility function to display dynamic toast/alert messages
function showToastMessage(message, type) {
    const alertType = type === 'success' ? 'alert-success' : 'alert-danger';
    const alertHtml = `
        <div class="alert ${alertType} alert-dismissible fade show shadow-sm" role="alert">
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    $("#message-container").html(alertHtml);
    setTimeout(function () {
        $("#message-container .alert").fadeOut("slow");
    }, 5000);
}
