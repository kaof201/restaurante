// ============================================
// CONFIGURACIÓN INICIAL
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('Sistema de Restaurante Cargado');
    
    // Inicializar tooltips de Bootstrap
    initTooltips();
    
    // Auto-cerrar alertas después de 5 segundos
    autoCloseAlerts();
    
    // Agregar animaciones a las cards
    animateCards();
});

// ============================================
// TOOLTIPS
// ============================================
function initTooltips() {
    const tooltipTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="tooltip"]')
    );
    
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// ============================================
// AUTO CERRAR ALERTAS
// ============================================
function autoCloseAlerts() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

// ============================================
// ANIMACIONES
// ============================================
function animateCards() {
    const cards = document.querySelectorAll('.card');
    
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });
}

// ============================================
// CONFIRMAR ACCIONES
// ============================================
function confirmarAccion(mensaje) {
    return confirm(mensaje || '¿Estás seguro de realizar esta acción?');
}

// ============================================
// FORMATEAR MONEDA
// ============================================
function formatearMoneda(numero) {
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP'
    }).format(numero);
}

// ============================================
// VALIDAR FORMULARIO
// ============================================
function validarFormulario(formId) {
    const form = document.getElementById(formId);
    
    if (!form) return false;
    
    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        return false;
    }
    
    return true;
}

// ============================================
// BUSQUEDA EN TABLA
// ============================================
function buscarEnTabla(inputId, tableId) {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    
    if (!input || !table) return;
    
    input.addEventListener('keyup', function() {
        const filter = this.value.toLowerCase();
        const rows = table.getElementsByTagName('tr');
        
        for (let i = 1; i < rows.length; i++) {
            const row = rows[i];
            const text = row.textContent || row.innerText;
            
            if (text.toLowerCase().indexOf(filter) > -1) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        }
    });
}

// ============================================
// ACTUALIZAR RELOJ
// ============================================
function actualizarReloj(elementId) {
    const elemento = document.getElementById(elementId);
    
    if (!elemento) return;
    
    setInterval(function() {
        const ahora = new Date();
        const tiempo = ahora.toLocaleTimeString('es-CO');
        elemento.textContent = tiempo;
    }, 1000);
}

// ============================================
// NOTIFICACIONES
// ============================================
function mostrarNotificacion(mensaje, tipo = 'info') {
    const container = document.querySelector('.container');
    
    if (!container) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${tipo} alert-dismissible fade show`;
    alert.innerHTML = `
        ${mensaje}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    container.insertBefore(alert, container.firstChild);
    
    // Auto cerrar después de 5 segundos
    setTimeout(function() {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    }, 5000);
}

// ============================================
// CARGAR DATOS DINÁMICAMENTE
// ============================================
async function cargarDatos(url) {
    try {
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error('Error al cargar datos');
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error:', error);
        mostrarNotificacion('Error al cargar los datos', 'danger');
        return null;
    }
}

// ============================================
// SCROLL SUAVE
// ============================================
function scrollSuave(elementoId) {
    const elemento = document.getElementById(elementoId);
    
    if (elemento) {
        elemento.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// ============================================
// COPIAR AL PORTAPAPELES
// ============================================
function copiarAlPortapapeles(texto) {
    navigator.clipboard.writeText(texto).then(function() {
        mostrarNotificacion('Texto copiado al portapapeles', 'success');
    }).catch(function(err) {
        console.error('Error al copiar:', err);
        mostrarNotificacion('Error al copiar el texto', 'danger');
    });
}

// ============================================
// EXPORTAR TABLA A CSV
// ============================================
function exportarTablaCSV(tableId, filename = 'datos.csv') {
    const table = document.getElementById(tableId);
    
    if (!table) return;
    
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    rows.forEach(function(row) {
        const cols = row.querySelectorAll('td, th');
        const csvRow = [];
        
        cols.forEach(function(col) {
            csvRow.push(col.innerText);
        });
        
        csv.push(csvRow.join(','));
    });
    
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    
    a.setAttribute('href', url);
    a.setAttribute('download', filename);
    a.click();
}

// ============================================
// UTILIDADES DE FECHA
// ============================================
function formatearFecha(fecha) {
    const opciones = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    
    return new Date(fecha).toLocaleDateString('es-CO', opciones);
}

// ============================================
// CONTADOR AUTOMÁTICO
// ============================================
function animarContador(elementId, valorFinal, duracion = 2000) {
    const elemento = document.getElementById(elementId);
    
    if (!elemento) return;
    
    let valorActual = 0;
    const incremento = valorFinal / (duracion / 16);
    
    const timer = setInterval(function() {
        valorActual += incremento;
        
        if (valorActual >= valorFinal) {
            valorActual = valorFinal;
            clearInterval(timer);
        }
        
        elemento.textContent = Math.floor(valorActual);
    }, 16);
}

// ============================================
// EVENTOS GLOBALES
// ============================================

// Prevenir envío doble de formularios
document.querySelectorAll('form').forEach(function(form) {
    form.addEventListener('submit', function() {
        const submitBtn = form.querySelector('button[type="submit"]');
        
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
        }
    });
});

// Confirmar eliminaciones
document.querySelectorAll('[data-confirm]').forEach(function(element) {
    element.addEventListener('click', function(e) {
        const mensaje = this.getAttribute('data-confirm');
        
        if (!confirm(mensaje)) {
            e.preventDefault();
        }
    });
});

console.log('✓ JavaScript del Sistema de Restaurante cargado correctamente');