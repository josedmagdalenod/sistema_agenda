(function(){
  function updateVerificadoState(){
    var ids = ['id_nombre_empresa_verificado','id_rif_verificado','id_telefono_verificado','id_email_verificado','id_direccion_verificada','id_documento_rif_verificado','id_acta_constitutiva_verificada'];
    var all = ids.every(function(i){ var el=document.getElementById(i); return el && el.checked; });
    var ver=document.getElementById('id_verificado');
    if (ver){
      ver.disabled = !all;
      if(!all) ver.checked = false;
    }
  }
  document.addEventListener('DOMContentLoaded', function(){
    var ids = ['id_nombre_empresa_verificado','id_rif_verificado','id_telefono_verificado','id_email_verificado','id_direccion_verificada','id_documento_rif_verificado','id_acta_constitutiva_verificada'];
    ids.forEach(function(i){ var el=document.getElementById(i); if(el) el.addEventListener('change', updateVerificadoState); });
    updateVerificadoState();
  });
})();
