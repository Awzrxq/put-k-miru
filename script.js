// ===== Модальное окно =====
const modal = document.getElementById('modal');
const form = document.getElementById('appointmentForm');
const successBlock = document.getElementById('modalSuccess');

// Открытие модалки
document.querySelectorAll('[data-modal-open]').forEach(btn => {
    btn.addEventListener('click', () => {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        // Если карточка услуги - подставляем услугу в select
        const card = btn.closest('.service-card');
        if (card && card.dataset.service) {
            const select = form.querySelector('select[name="service_type"]');
            select.value = card.dataset.service;
        }
    });
});

// Закрытие модалки
document.querySelectorAll('[data-modal-close]').forEach(el => {
    el.addEventListener('click', () => {
        modal.classList.remove('active');
        document.body.style.overflow = '';
        // Сброс через 300мс после закрытия
        setTimeout(() => {
            form.style.display = 'flex';
            successBlock.style.display = 'none';
            form.reset();
        }, 300);
    });
});

// Закрытие по Esc
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.classList.contains('active')) {
        modal.querySelector('[data-modal-close]').click();
    }
});

// ===== Отправка формы =====
form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Отправляем...';
    submitBtn.disabled = true;

    const formData = {
        name: form.name.value.trim(),
        phone: form.phone.value.trim(),
        service_type: form.service_type.value,
        message: form.message.value.trim()
    };

    try {
        const response = await fetch('/api/appointments', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            throw new Error('Ошибка сервера');
        }

        // Успех
        form.style.display = 'none';
        successBlock.style.display = 'block';

    } catch (err) {
        console.error(err);
        alert('Не удалось отправить заявку. Попробуйте ещё раз или позвоните нам.');
    } finally {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
});

// ===== Клик по карточке услуги =====
document.querySelectorAll('.service-card').forEach(card => {
    card.addEventListener('click', (e) => {
        // Не открывать, если кликнули по ссылке
        if (e.target.tagName === 'A') return;
        const btn = card.querySelector('.arrow-btn');
        if (btn) btn.click();
    });
});

// ===== Плавное появление секций при скролле =====
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

document.querySelectorAll('.feature-card, .service-card, .about__text, .about__visual').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity 0.7s ease, transform 0.7s ease';
    observer.observe(el);
});

console.log('🌿 Сайт «Путь к миру» загружен');
