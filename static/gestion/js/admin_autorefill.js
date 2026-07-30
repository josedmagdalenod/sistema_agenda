
document.addEventListener("DOMContentLoaded", function() {
    var reqSelect = document.querySelector("#id_requerimiento_en_curso") || document.querySelector("select[name='requerimiento_en_curso']");

    if (reqSelect) {
        reqSelect.addEventListener("change", function() {
            var reqId = this.value;
            if (!reqId) return;

            fetch("/api/requerimiento/" + reqId + "/")
                .then(response => response.json())
                .then(data => {
                    if (data.error) return;

                    // Campos a autocompletar en el formulario
                    var elPersona = document.querySelector("#id_persona_solicito") || document.querySelector("input[name='persona_solicito']");
                    var elTicket = document.querySelector("#id_numero_ticket") || document.querySelector("input[name='numero_ticket']");
                    var elTitulo = document.querySelector("#id_titulo") || document.querySelector("input[name='titulo']");
                    var elEmpresa = document.querySelector("#id_empresa") || document.querySelector("select[name='empresa']");
                    var elFecha = document.querySelector("#id_fecha_solicitud") || document.querySelector("input[name='fecha_solicitud']");
                    var elDesglose = document.querySelector("#id_desglose") || document.querySelector("textarea[name='desglose']");

                    if (elPersona && data.solicitante) elPersona.value = data.solicitante;
                    if (elTicket && data.numero_ticket) elTicket.value = data.numero_ticket;
                    if (elTitulo && data.titulo) elTitulo.value = data.titulo;
                    if (elFecha && data.fecha) elFecha.value = data.fecha;
                    if (elDesglose && data.desglose) elDesglose.value = data.desglose;

                    if (elEmpresa && data.empresa_id) {
                        elEmpresa.value = data.empresa_id;
                    }
                })
                .catch(err => console.error("Error obteniendo datos del requerimiento:", err));
        });
    }
});
