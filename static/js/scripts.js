// =====================================================
// 1. FUNCIONES DE UX & UTILIDADES
// =====================================================

// Función para mostrar Toasts (requiere un contenedor con clase "toast-container")
function showToast(message, type = 'success') {
    const toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        console.warn('No se encontró el contenedor de toasts. Agrega un <div class="toast-container position-fixed bottom-0 end-0 p-3"></div> en tu HTML.');
        return;
    }
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-bg-${type} border-0`;
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    toastContainer.appendChild(toast);
    new bootstrap.Toast(toast).show();
}

// Helper: Obtener el CSRF token desde las cookies
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



// Animaciones al hacer scroll
function initUXFeatures() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, { threshold: 0.1 });
    document.querySelectorAll('.card, footer, .navbar').forEach(el => observer.observe(el));
}

// Modo Oscuro
function initDarkMode() {
    const toggle = document.getElementById('darkModeToggle');
    const isDark = localStorage.getItem('darkMode') === 'true';
    if (isDark) document.body.classList.add('dark-mode');
    if (toggle) {
        toggle.addEventListener('click', () => {
            document.body.classList.toggle('dark-mode');
            localStorage.setItem('darkMode', document.body.classList.contains('dark-mode') ? 'true' : 'false');

        });
    }
}



// Scroll to Top
function initScrollTop() {
    const scrollButton = document.querySelector('.scroll-top');
    if (!scrollButton) return;
    window.addEventListener('scroll', () => {
        scrollButton.classList.toggle('visible', window.scrollY > 300);
    });
    scrollButton.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

// Filtro por Categoría
function initCategoryFilter() {
    const filters = document.querySelectorAll('.category-filter');
    filters.forEach(filter => {
        filter.addEventListener('click', () => {
            const category = filter.getAttribute('data-category');
            window.location.href = `/productos/?category=${category}`;
        });
    });
}

// LightGallery para productos
function initLightGallery() {
    const gallery = document.getElementById('product-gallery');
    if (gallery) {
        import('https://cdnjs.cloudflare.com/ajax/libs/lightgallery-js/1.4.0/lightgallery.min.js')
            .then(module => module.default(gallery, {
                thumbnail: true,
                animateThumb: false,
                showThumbByDefault: false,
            }))
            .catch(error => console.error("Error al cargar LightGallery:", error));
    }
}

// Tooltips de Bootstrap
function initTooltips() {
    const tooltipTriggerList = Array.from(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(tooltipTriggerEl => {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Lazy Load en imágenes sin atributo "loading"
function initLazyLoadImages() {
    const images = document.querySelectorAll('img:not([loading])');
    images.forEach(img => {
        img.setAttribute('loading', 'lazy');
    });
}

// Función debounce (debe estar definida antes de usarla)
function debounce(func, delay) {
    let timer;
    return function (...args) {
        clearTimeout(timer);
        timer = setTimeout(() => {
            func.apply(this, args);
        }, delay);
    };
}

function initGlobalSearch() {
    const searchInput = document.getElementById('globalSearch');
    const productGrid = document.getElementById('productGrid');

    // Asegúrate de que el input tenga el atributo data-url con la URL correcta:
    // data-url="{% url 'productos:filtrar_productos' %}"

    const debounceSearch = debounce(async (query) => {
        const params = new URLSearchParams(window.location.search);
        params.set('search', query);

        try {
            // Usamos template string para construir la URL
            const response = await fetch(`${searchInput.dataset.url}?${params.toString()}`);
            if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
            
            // Se espera que la respuesta sea JSON con la clave 'html'
            const data = await response.json();
            productGrid.innerHTML = data.html;

            // Opcional: reiniciar animaciones (si tienes definido un observer)
            productGrid.querySelectorAll('.card').forEach(card => {
                card.style.opacity = "0";
                card.style.transform = "translateY(20px)";
                if (typeof observer !== 'undefined') {
                    observer.observe(card);
                }
            });
        } catch (error) {
            console.error('❌ Error en búsqueda:', error);
            productGrid.innerHTML = `<div class="text-center text-danger py-3">Ocurrió un error al cargar los productos.</div>`;
        }
    }, 300);

    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            debounceSearch(e.target.value);
        });
    }
}

// Inicializa la búsqueda global cuando el DOM esté cargado
document.addEventListener('DOMContentLoaded', function () {
    initGlobalSearch();
});




    function addActive(items) {
        removeActive(items);
        if (currentFocus >= items.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = items.length - 1;
        items[currentFocus].classList.add('autocomplete-active');
    }
    function removeActive(items) {
        items.forEach(item => item.classList.remove('autocomplete-active'));
    }


// Manejo global de errores
    function initGlobalErrorHandler() {
        window.addEventListener('error', (e) => {
            console.error('Error global capturado:', e.error);
            showToast('Ha ocurrido un error inesperado', 'danger');
        });
    }

// =====================================================
// 2. FUNCIONES DEL CARRITO (AJAX)
// =====================================================

// Inicializa el contador del carrito consultándolo al servidor
function initCart() {
    const url = (typeof CART_COUNT_URL !== 'undefined') ? CART_COUNT_URL : '/cart/cart/count/';
    fetch(url)
        .then(response => response.json().catch(err => {
            console.error('La respuesta no es JSON. Respuesta:', response);
            throw err;
        }))
        .then(data => {
            if (data.cart_count !== undefined) {
                updateCartCount(data.cart_count);
            }
        })
        .catch(error => console.error('Error al obtener el conteo del carrito:', error));
}

// Actualiza el contador en el DOM y en localStorage
function updateCartCount(newCount) {
    const cartCount = document.getElementById('cartCount');
    if (cartCount) {
        cartCount.textContent = newCount;
    }
    localStorage.setItem('cartCount', newCount);
    document.querySelectorAll('.cart-count-indicator').forEach(element => {
        element.textContent = newCount;
    });
}

// Configura la sincronización del carrito entre pestañas y al recuperar el foco
function setupCartSync() {
    window.addEventListener('focus', initCart);
    window.addEventListener('storage', (e) => {
        if (e.key === 'cartCount') {
            initCart();
        }
    });
}


// =====================================================
// 3. INICIALIZACIÓN DE SINCRONIZACIÓN DEL CARRITO
// =====================================================
function setupCartSynchronization() {
    setupCartSync();
    
}

// =====================================================
// FIN DEL SCRIPT: Inicialización general
// =====================================================
document.addEventListener('DOMContentLoaded', function () {
    // Funciones de UX & Utilidades
    initUXFeatures();
    initScrollTop();
    initDarkMode();
    initCategoryFilter();
    initLightGallery();
    initTooltips();
    initLazyLoadImages();
    initGlobalErrorHandler();
    initGlobalSearch();
   
    
    // Funciones del Carrito
    initCart();
    setupCartSynchronization();
});
