document.addEventListener("DOMContentLoaded", function () {
    const selectReq = document.getElementById("id_requerimiento_origen");

    if (selectReq) {
        selectReq.addEventListener("change", function () {
            const ticketId = this.value;
            if (!ticketId) return;

            fetch("/api/requerimiento/" + ticketId + "/")
                .then(response => response.json())
                .then(data => {
                    const inputGlpi = document.getElementById("id_ticket_glpi");
                    const inputTitulo = document.getElementById("id_titulo_requerimiento");
                    const selectEmpresa = document.getElementById("id_empresa_destino");
                    const textareaItems = document.getElementById("id_desglose_items");
                    const inputSolicitante = document.getElementById("id_solicitante_info");

                    if (inputGlpi && !inputGlpi.value) inputGlpi.value = data.ticket_glpi;
                    if (inputTitulo) inputTitulo.value = data.titulo;
                    if (selectEmpresa) selectEmpresa.value = data.empresa_destino_id;
                    if (textareaItems) textareaItems.value = data.desglose_items;
                    
                    if (inputSolicitante) {
                        const emailInfo = data.solicitante_email ? " (" + data.solicitante_email + ")" : "";
                        inputSolicitante.value = data.solicitante_nombre + emailInfo;
                    }

                    generarTablaDinamica(data.desglose_items);
                })
                .catch(error => console.error("Error al autocompletar requerimiento:", error));
        });
    }

    function transformarCasillasVisuales() {
        document.querySelectorAll("[id$='-descripcion_adjudicacion']").forEach(campoOriginal => {
            if (campoOriginal.dataset.transformed) return;
            campoOriginal.dataset.transformed = "true";

            campoOriginal.style.display = "none";

            let containerDiv = document.createElement("div");
            containerDiv.className = "tabla-seriales-container";
            containerDiv.style.width = "100%";
            containerDiv.style.marginTop = "8px";

            let btnHelper = document.createElement("button");
            btnHelper.type = "button";
            btnHelper.className = "button";
            btnHelper.style.display = "inline-block";
            btnHelper.style.marginBottom = "10px";
            btnHelper.style.backgroundColor = "#0d6efd";
            btnHelper.style.color = "#ffffff";
            btnHelper.style.border = "none";
            btnHelper.style.padding = "8px 16px";
            btnHelper.style.borderRadius = "4px";
            btnHelper.style.cursor = "pointer";
            btnHelper.style.fontWeight = "bold";
            btnHelper.innerHTML = "<i class='fa-solid fa-rotate'></i> Regenerar Formulario de Marcas y Seriales";

            let tableWrapper = document.createElement("div");
            tableWrapper.className = "table-responsive";

            btnHelper.addEventListener("click", function () {
                const textareaItems = document.getElementById("id_desglose_items");
                if (textareaItems && textareaItems.value) {
                    generarTablaDinamica(textareaItems.value);
                } else {
                    alert("Por favor seleccione primero un requerimiento en curso arriba.");
                }
            });

            containerDiv.appendChild(btnHelper);
            containerDiv.appendChild(tableWrapper);

            campoOriginal.parentNode.insertBefore(containerDiv, campoOriginal);

            // Si ya hay ítems en la caja de desglose superior, generar la tabla de una vez
            const textareaItems = document.getElementById("id_desglose_items");
            if (textareaItems && textareaItems.value) {
                generarTablaDinamica(textareaItems.value);
            }
        });
    }

    function generarTablaDinamica(desgloseTexto) {
        document.querySelectorAll(".tabla-seriales-container").forEach(container => {
            let wrapper = container.querySelector(".table-responsive");
            let campoOriginal = container.parentNode.querySelector("[id$='-descripcion_adjudicacion']");

            let lineas = desgloseTexto.split("\n");
            let htmlTable = `
                <table class="table table-bordered table-sm align-middle" style="width:100%; border-collapse:collapse; margin-top:5px; background:#fff; font-size:13px;">
                    <thead>
                        <tr style="background:#e9ecef; text-align:left; font-weight:bold;">
                            <th style="padding:6px; border:1px solid #dee2e6; width:35%;">Ítem / Producto</th>
                            <th style="padding:6px; border:1px solid #dee2e6; width:25%;">Marca y Modelo</th>
                            <th style="padding:6px; border:1px solid #dee2e6; width:25%;">Serial / Código Único</th>
                            <th style="padding:6px; border:1px solid #dee2e6; width:15%;">Costo Unit. ($)</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            lineas.forEach(l => {
                let itemLimpio = l.trim();
                if (itemLimpio) {
                    // Separación limpia de cantidad e ítem
                    let match = itemLimpio.match(/^(\d+)\s*(.*)/);
                    let cant = 1;
                    let nombreItem = itemLimpio;

                    if (match) {
                        cant = parseInt(match[1]);
                        nombreItem = match[2].trim();
                    }

                    for (let i = 1; i <= cant; i++) {
                        let sufijo = cant > 1 ? " (" + i + " de " + cant + ")" : "";
                        let itemNombreFull = nombreItem + sufijo;

                        htmlTable += `
                            <tr>
                                <td style="padding:4px; border:1px solid #dee2e6;">
                                    <input type="text" class="form-control form-control-sm row-item" value="${itemNombreFull}" style="width:100%; border:1px solid #ccc; padding:4px; font-weight:600;" />
                                </td>
                                <td style="padding:4px; border:1px solid #dee2e6;">
                                    <input type="text" class="form-control form-control-sm row-marca" placeholder="Ej: HP / Dell / Cantera" style="width:100%; border:1px solid #ccc; padding:4px;" />
                                </td>
                                <td style="padding:4px; border:1px solid #dee2e6;">
                                    <input type="text" class="form-control form-control-sm row-serial" placeholder="Ej: SN-998811 / N/A" style="width:100%; border:1px solid #ccc; padding:4px;" />
                                </td>
                                <td style="padding:4px; border:1px solid #dee2e6;">
                                    <input type="number" step="0.01" class="form-control form-control-sm row-costo" value="0.00" style="width:100%; border:1px solid #ccc; padding:4px;" />
                                </td>
                            </tr>
                        `;
                    }
                }
            });

            htmlTable += `</tbody></table>`;
            wrapper.innerHTML = htmlTable;

            function sincronizarOriginal() {
                let lineasFormateadas = [];
                wrapper.querySelectorAll("tbody tr").forEach(tr => {
                    let item = tr.querySelector(".row-item").value.trim();
                    let marca = tr.querySelector(".row-marca").value.trim() || "N/A";
                    let serial = tr.querySelector(".row-serial").value.trim() || "S/N";
                    let costo = tr.querySelector(".row-costo").value.trim() || "0.00";

                    lineasFormateadas.push(item + " | " + marca + " | " + serial + " | " + costo);
                });
                if (campoOriginal) {
                    campoOriginal.value = lineasFormateadas.join("\n");
                }
            }

            wrapper.querySelectorAll("input").forEach(inp => {
                inp.addEventListener("input", sincronizarOriginal);
            });

            sincronizarOriginal();
        });
    }

    transformarCasillasVisuales();

    const container = document.getElementById("pagos_proveedores-group");
    if (container) {
        const observer = new MutationObserver(function () {
            transformarCasillasVisuales();
        });
        observer.observe(container, { childList: true, subtree: true });
    }
});