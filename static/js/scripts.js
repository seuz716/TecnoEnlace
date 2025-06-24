// ===========================
// 1. UTILIDADES GENERALES
// ===========================

// Mostrar toasts (requiere .toast-container en el DOM)
function showToast(message, type = 'success') {
    const container = document.querySelector('.toast-container');
    if (!container) {
        console.warn('Falta el contenedor de toasts.');
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
    container.appendChild(toast);
    new bootstrap.Toast(toast).show();
}

document.addEventListener('DOMContentLoaded', function() {
    const csrfToken = '{{ csrf_token }}';

    document.querySelectorAll('tbody tr').forEach(row => {
        row.addEventListener('mouseenter', () => row.classList.add('table-active'));
        row.addEventListener('mouseleave', () => row.classList.remove('table-active'));
    });

   

    document.querySelectorAll('.remove-item').forEach(button => {
        button.addEventListener('click', async (e) => {
            const productId = e.currentTarget.dataset.productId;
            const row = e.currentTarget.closest('tr');
            row.classList.add('animate__animated', 'animate__fadeOut');
            await new Promise(resolve => setTimeout(resolve, 500));
            await fetch(`/cart/remove/${productId}/`, {
                method: 'POST',
                headers: {'X-CSRFToken': csrfToken}
            });
            row.remove();
            updateTotal();
        });
    });

    document.getElementById('confirmCheckout').addEventListener('click', (e) => {
        e.currentTarget.querySelector('.spinner-border').classList.remove('d-none');
        e.currentTarget.disabled = true;
    });

    async function updateCart(productId, quantity) {
        try {
            const response = await fetch(`/cart/update/${productId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({quantity})
            });

            if (response.ok) {
                const data = await response.json();
                document.querySelector(`.subtotal[data-product-id="${productId}"]`).textContent = `$ ${data.subtotal.toLocaleString()}`;
                updateTotal();
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }

    function updateTotal() {
        let total = 0;
        document.querySelectorAll('.subtotal').forEach(element => {
            const price = parseFloat(element.dataset.price);
            const quantity = parseInt(element.closest('tr').querySelector('.quantity-input').value);
            total += price * quantity;
        });
        document.getElementById('cart-total').textContent = total.toLocaleString();
    }
});


    document.addEventListener("DOMContentLoaded", function () {
        initDarkMode();
    });

// Obtener CSRF desde cookies
function getCookie(name) {
    return document.cookie.split(';')
        .map(c => c.trim())
        .find(c => c.startsWith(name + '='))
        ?.split('=')[1] || null;
}

// Debounce para búsquedas o eventos frecuentes
function debounce(func, delay) {
    let timer;
    return function (...args) {
        clearTimeout(timer);
        timer = setTimeout(() => func.apply(this, args), delay);
    };
}

// ===========================
// 2. UX Y FUNCIONALIDADES
// ===========================

// Animaciones en scroll (fade-in)
function initUXFeatures() {
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) entry.target.classList.add('fade-in');
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.card, footer, .navbar').forEach(el => observer.observe(el));
}

// Dark mode con localStorage
function initDarkMode() {
    const toggle = document.getElementById('darkModeToggle');
    if (localStorage.getItem('darkMode') === 'true') document.body.classList.add('dark-mode');
    toggle?.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
    });
}

// Botón scroll to top
function initScrollTop() {
    const btn = document.querySelector('.scroll-top');
    if (!btn) return;

    window.addEventListener('scroll', () => {
        btn.classList.toggle('visible', window.scrollY > 300);
    });

    btn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

// Filtrar por categoría
function initCategoryFilter() {
    document.querySelectorAll('.category-filter').forEach(filter => {
        filter.addEventListener('click', () => {
            const category = filter.dataset.category;
            window.location.href = `/productos/?category=${category}`;
        });
    });
}

// Lazy load para imágenes sin atributo loading
function initLazyLoadImages() {
    document.querySelectorAll('img:not([loading])')
        .forEach(img => img.setAttribute('loading', 'lazy'));
}

// Tooltips Bootstrap
function initTooltips() {
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
        new bootstrap.Tooltip(el);
    });
}

// LightGallery
function initLightGallery() {
    const gallery = document.getElementById('product-gallery');
    if (!gallery) return;

    import('https://cdnjs.cloudflare.com/ajax/libs/lightgallery-js/1.4.0/lightgallery.min.js')
        .then(module => module.default(gallery, {
            thumbnail: true,
            animateThumb: false,
            showThumbByDefault: false,
        }))
        .catch(error => console.error("Error al cargar LightGallery:", error));
}

// Manejo de errores globales
function initGlobalErrorHandler() {
    window.addEventListener('error', e => {
        console.error('Error global:', e.error);
        showToast('Ha ocurrido un error inesperado', 'danger');
    });
}

// ===========================
// 3. BÚSQUEDA EN TIEMPO REAL
// ===========================

function initGlobalSearch() {
    const searchInput = document.getElementById('globalSearch');
    const productGrid = document.getElementById('productGrid');
    if (!searchInput || !productGrid) return;

    const search = debounce(async (query) => {
        const params = new URLSearchParams(window.location.search);
        params.set('search', query);

        try {
            const res = await fetch(`${searchInput.dataset.url}?${params}`);
            if (!res.ok) throw new Error(res.status);
            const data = await res.json();
            productGrid.innerHTML = data.html;

            productGrid.querySelectorAll('.card').forEach(card => {
                card.style.opacity = "0";
                card.style.transform = "translateY(20px)";
            });
        } catch (err) {
            console.error('❌ Error en búsqueda:', err);
            productGrid.innerHTML = `<div class="text-center text-danger py-3">Error al cargar los productos.</div>`;
        }
    }, 300);

    searchInput.addEventListener('input', e => search(e.target.value));
}

// ===========================
// 4. FUNCIONES DEL CARRITO
// ===========================

// Inicializar contador del carrito
function initCart() {
    const url = typeof CART_COUNT_URL !== 'undefined' ? CART_COUNT_URL : '/cart/cart/count/';
    fetch(url)
        .then(res => res.json())
        .then(data => updateCartCount(data.cart_count))
        .catch(err => console.error('Error al obtener conteo del carrito:', err));
}

// Actualizar contador visualmente y sincronizar
function updateCartCount(count) {
    const countElem = document.getElementById('cartCount');
    if (countElem) countElem.textContent = count;

    localStorage.setItem('cartCount', count);
    document.querySelectorAll('.cart-count-indicator').forEach(el => el.textContent = count);
}

// Sincronizar entre pestañas y al volver al foco
function setupCartSync() {
    window.addEventListener('focus', initCart);
    window.addEventListener('storage', e => {
        if (e.key === 'cartCount') initCart();
    });
}

  document.addEventListener('DOMContentLoaded', () => {
    // GLOW al pasar el cursor
    document.querySelectorAll('.neon-brand, .nav-link, .dropdown-item').forEach(el => {
      el.addEventListener('mouseenter', () => {
        el.style.filter = 'drop-shadow(0 0 5px #00f0ff)';
      });
      el.addEventListener('mouseleave', () => {
        el.style.filter = '';
      });
    });

    // MODO OSCURO
    const toggle = document.getElementById('darkModeToggle');
    const body = document.body;

    // Restaurar modo oscuro desde localStorage
    if (localStorage.getItem('dark-mode') === 'enabled') {
      body.classList.add('dark-mode');
    }

    toggle?.addEventListener('click', () => {
      body.classList.toggle('dark-mode');
      const isDark = body.classList.contains('dark-mode');
      localStorage.setItem('dark-mode', isDark ? 'enabled' : 'disabled');
    });

    // FUNCIONES DEL CARRITO (si están disponibles)
    if (typeof initCart === 'function') initCart();
    if (typeof setupCartSync === 'function') setupCartSync();
  });


   function incrementQuantity(productId) {
      const input = document.getElementById('cantidad_' + productId);
      input.value = parseInt(input.value) + 1;
    }

    function decrementQuantity(productId) {
      const input = document.getElementById('cantidad_' + productId);
      if (parseInt(input.value) > 1) {
        input.value = parseInt(input.value) - 1;
      }
    }

    function showMessage(message) {
      alert(message); // Puedes reemplazar por un toast
    }

    function initCartForms() {
      document.querySelectorAll('.add-to-cart-form').forEach(form => {
        form.addEventListener('submit', function (event) {
          event.preventDefault();
          const productoId = form.dataset.productoId;
          const cantidad = form.querySelector('input[name="cantidad"]').value;
          const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;
          const url = "{% url 'cart:add' 0 %}".replace('0', productoId);

          fetch(url, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded',
              'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin',
            body: new URLSearchParams({
              cantidad,
              csrfmiddlewaretoken: csrfToken
            })
          })
          .then(response => response.json())
          .then(data => {
            if (data.success) {
              const cartCountElem = document.getElementById('cartCount');
              if (cartCountElem) {
                cartCountElem.innerText = data.cart_count;
              }
              showMessage("Producto agregado al carrito");
            } else {
              showMessage("Error al agregar producto");
            }
          })
          .catch(error => {
            console.error('Error:', error);
            showMessage("Error al procesar la solicitud.");
          });
        });
      });
    }

    function initScrollAnimations() {
      const cards = document.querySelectorAll(".animate-on-scroll");
      const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add("show");
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.1 });

      cards.forEach(card => {
        card.classList.add("fade-in-up");
        observer.observe(card);
      });
    }

    function initRealTimeSearch() {
      const searchInput = document.getElementById('globalSearch');
      if (!searchInput) return;

      const debounce = (func, delay) => {
        let timeout;
        return (...args) => {
          clearTimeout(timeout);
          timeout = setTimeout(() => func(...args), delay);
        };
      };

      // Búsqueda en tiempo real opcional
    }

    document.addEventListener("DOMContentLoaded", () => {
      initCartForms();
      initScrollAnimations();
      initRealTimeSearch();
    });
// ===========================
// 5. INICIALIZACIÓN GLOBAL
// ===========================

document.addEventListener('DOMContentLoaded', () => {
    initUXFeatures();
    initDarkMode();
    initScrollTop();
    initCategoryFilter();
    initLazyLoadImages();
    initTooltips();
    initLightGallery();
    initGlobalErrorHandler();
    initGlobalSearch();

    initCart();
    setupCartSync();
});

