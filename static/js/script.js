// LinkarCasa JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }
    
    // FAQ accordion functionality
    const faqItems = document.querySelectorAll('.faq-item');
    
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        const answer = item.querySelector('.faq-answer');
        const icon = question.querySelector('i');
        
        question.addEventListener('click', function() {
            const isActive = item.classList.contains('active');
            
            // Close all other FAQ items
            faqItems.forEach(otherItem => {
                if (otherItem !== item) {
                    otherItem.classList.remove('active');
                    otherItem.querySelector('.faq-answer').classList.add('hidden');
                    otherItem.querySelector('.faq-question i').style.transform = 'rotate(0deg)';
                }
            });
            
            // Toggle current item
            if (isActive) {
                item.classList.remove('active');
                answer.classList.add('hidden');
                icon.style.transform = 'rotate(0deg)';
            } else {
                item.classList.add('active');
                answer.classList.remove('hidden');
                icon.style.transform = 'rotate(180deg)';
            }
        });
    });
    
    // Smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('a[href^="#"]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                const offsetTop = targetElement.offsetTop - 80; // Account for fixed header
                
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
                
                // Close mobile menu if open
                if (mobileMenu && !mobileMenu.classList.contains('hidden')) {
                    mobileMenu.classList.add('hidden');
                }
            }
        });
    });
      // Form submission handling
    const contactForm = document.getElementById('contact-form');
    const formMessage = document.getElementById('form-message');
    
    if (contactForm) {
        contactForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const submitButton = contactForm.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.innerHTML;
              // Show loading state
            document.getElementById('submit-default').style.display = 'none';
            document.getElementById('submit-loading').style.display = 'inline-flex';
            submitButton.disabled = true;
            
            try {
                const formData = new FormData(contactForm);
                
                // Validate form fields
                const nome = formData.get('nome');
                const email = formData.get('email');
                const telefone = formData.get('telefone');
                
                if (!nome || !email || !telefone) {
                    showMessage('Por favor, preencha todos os campos obrigatórios.', 'error');
                    return;
                }
                
                // Simple email validation
                const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailPattern.test(email)) {
                    showMessage('Por favor, forneça um endereço de e-mail válido.', 'error');
                    return;
                }
                  // Submit the form
                const response = await fetch('/contato', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    console.log('Formulário enviado com sucesso!', result);
                    showMessage(result.message, 'success');
                    contactForm.reset();
                    
                    // Track conversion if available
                    if (typeof gtag === 'function') {
                        gtag('event', 'conversion', {
                            'send_to': 'AW-CONVERSION_ID/CONVERSION_LABEL',
                            'transaction_id': result.contato_id
                        });
                    }
                } else {
                    console.error('Erro no envio do formulário:', result);
                    showMessage(result.message || 'Ocorreu um erro ao enviar o formulário. Por favor, tente novamente.', 'error');
                }
                
            } catch (error) {
                console.error('Erro ao enviar formulário:', error);
                showMessage('Erro ao enviar mensagem. Tente novamente.', 'error');
            } finally {                // Restore button state
                document.getElementById('submit-loading').style.display = 'none';
                document.getElementById('submit-default').style.display = 'inline-flex';
                submitButton.disabled = false;
            }
        });
    }
    
    function showMessage(message, type) {
        if (!formMessage) return;
        
        formMessage.className = `mt-6 p-4 rounded-lg ${type === 'success' ? 'bg-green-600 text-white' : 'bg-red-600 text-white'}`;
        formMessage.textContent = message;
        formMessage.classList.remove('hidden');
        
        // Hide message after 5 seconds
        setTimeout(() => {
            formMessage.classList.add('hidden');
        }, 5000);
    }
    
    // Intersection Observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate');
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    const animatedElements = document.querySelectorAll('.fade-in-up');
    animatedElements.forEach(el => observer.observe(el));
    
    // Add scroll effect to header
    const header = document.querySelector('nav');
    let lastScrollY = window.scrollY;
    
    window.addEventListener('scroll', function() {
        const currentScrollY = window.scrollY;
        
        if (header) {
            if (currentScrollY > 100) {
                header.classList.add('bg-gray-900');
                header.classList.remove('bg-gray-900/95');
            } else {
                header.classList.remove('bg-gray-900');
                header.classList.add('bg-gray-900/95');
            }
        }
        
        lastScrollY = currentScrollY;
    });
    
    // Phone number formatting
    const phoneInput = document.getElementById('telefone');
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            
            if (value.length <= 11) {
                if (value.length <= 2) {
                    value = value.replace(/(\d{0,2})/, '($1');
                } else if (value.length <= 6) {
                    value = value.replace(/(\d{2})(\d{0,4})/, '($1) $2');
                } else if (value.length <= 10) {
                    value = value.replace(/(\d{2})(\d{4})(\d{0,4})/, '($1) $2-$3');
                } else {
                    value = value.replace(/(\d{2})(\d{5})(\d{0,4})/, '($1) $2-$3');
                }
            }
            
            e.target.value = value;
        });
    }
    
    // Parallax effect for hero section
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const heroElements = document.querySelectorAll('.animate-float');
        
        heroElements.forEach((element, index) => {
            const speed = 0.5 + (index * 0.1);
            element.style.transform = `translateY(${scrolled * speed}px)`;
        });
    });
    
    // Add typing effect to hero title (optional enhancement)
    function typeWriter(element, text, speed = 100) {
        let i = 0;
        element.innerHTML = '';
        
        function type() {
            if (i < text.length) {
                element.innerHTML += text.charAt(i);
                i++;
                setTimeout(type, speed);
            }
        }
        
        type();
    }
    
    // WhatsApp contact integration
    function openWhatsApp(phoneNumber, message) {
        const cleanPhone = phoneNumber.replace(/\D/g, '');
        const encodedMessage = encodeURIComponent(message);
        const whatsappURL = `https://wa.me/55${cleanPhone}?text=${encodedMessage}`;
        window.open(whatsappURL, '_blank');
    }
    
    // Add click-to-call functionality (if needed)
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('whatsapp-link')) {
            e.preventDefault();
            const phone = e.target.dataset.phone;
            const message = e.target.dataset.message || 'Olá! Gostaria de saber mais sobre a LinkarCasa.';
            openWhatsApp(phone, message);
        }
    });    // Tooltip functionality optimized for icon clicks
    function initializeTooltips() {
        const tooltipContainers = document.querySelectorAll('.tooltip-container');
        
        console.log('=== TOOLTIP DEBUG ===');
        console.log('Found tooltip containers:', tooltipContainers.length);
        
        if (tooltipContainers.length === 0) {
            console.log('No tooltip containers found.');
            return;
        }
        
        tooltipContainers.forEach((container, index) => {
            const tooltip = container.querySelector('.tooltip-content');
            const icon = container.querySelector('i');
            
            console.log(`Container ${index}:`, container);
            console.log(`Tooltip ${index}:`, tooltip);
            console.log(`Icon ${index}:`, icon);
            
            if (!tooltip) {
                console.log(`No tooltip content found for container ${index}`);
                return;
            }
            
            // Set initial styles
            tooltip.style.opacity = '0';
            tooltip.style.visibility = 'hidden';
            tooltip.style.pointerEvents = 'none';
            
            // Click to toggle tooltip
            container.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                console.log(`Click tooltip ${index}`);
                
                // Hide all other tooltips first
                document.querySelectorAll('.tooltip-content').forEach(otherTooltip => {
                    if (otherTooltip !== tooltip) {
                        otherTooltip.style.opacity = '0';
                        otherTooltip.style.visibility = 'hidden';
                        otherTooltip.style.pointerEvents = 'none';
                    }
                });
                
                // Toggle current tooltip
                const isVisible = tooltip.style.visibility === 'visible' && tooltip.style.opacity === '1';
                
                if (isVisible) {
                    tooltip.style.opacity = '0';
                    tooltip.style.visibility = 'hidden';
                    tooltip.style.pointerEvents = 'none';
                    console.log(`Tooltip ${index} hidden`);
                } else {
                    tooltip.style.opacity = '1';
                    tooltip.style.visibility = 'visible';
                    tooltip.style.pointerEvents = 'auto';
                    console.log(`Tooltip ${index} shown`);
                }
            });
            
            // Optional: Show on hover for desktop users
            container.addEventListener('mouseenter', function(e) {
                console.log(`Mouse enter tooltip ${index}`);
                // Only show if not on mobile
                if (window.innerWidth > 768) {
                    // Hide all other tooltips first
                    document.querySelectorAll('.tooltip-content').forEach(otherTooltip => {
                        if (otherTooltip !== tooltip) {
                            otherTooltip.style.opacity = '0';
                            otherTooltip.style.visibility = 'hidden';
                            otherTooltip.style.pointerEvents = 'none';
                        }
                    });
                    
                    tooltip.style.opacity = '1';
                    tooltip.style.visibility = 'visible';
                    tooltip.style.pointerEvents = 'auto';
                }
            });
            
            // Hide on mouse leave (desktop only)
            container.addEventListener('mouseleave', function(e) {
                console.log(`Mouse leave tooltip ${index}`);
                if (window.innerWidth > 768) {
                    tooltip.style.opacity = '0';
                    tooltip.style.visibility = 'hidden';
                    tooltip.style.pointerEvents = 'none';
                }
            });
            
            console.log(`Tooltip ${index} initialized successfully`);
        });
        
        // Hide tooltips when clicking outside
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.tooltip-container')) {
                document.querySelectorAll('.tooltip-content').forEach(tooltip => {
                    tooltip.style.opacity = '0';
                    tooltip.style.visibility = 'hidden';
                    tooltip.style.pointerEvents = 'none';
                });
            }
        });
        
        console.log('=== TOOLTIP INIT COMPLETE ===');
    }
      // Initialize tooltips with retry mechanism
    function initializeTooltipsWithRetry() {
        setTimeout(() => {
            initializeTooltips();
            
            // Double-check after page fully loaded
            setTimeout(() => {
                const tooltipCount = document.querySelectorAll('.tooltip-container').length;
                console.log('Final tooltip count:', tooltipCount);
                if (tooltipCount > 0) {
                    console.log('Tooltips found and should be working');
                } else {
                    console.log('No tooltips found on page');
                }
            }, 1000);
        }, 100);
    }
    
    initializeTooltipsWithRetry();
});

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Performance optimization
if ('IntersectionObserver' in window) {
    // Use Intersection Observer for better performance
    const lazyImages = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    lazyImages.forEach(img => imageObserver.observe(img));
}

// Error handling for external resources
window.addEventListener('error', function(e) {
    console.error('Resource loading error:', e.target.src || e.target.href);
    // Optionally show user-friendly error message
});

// Add service worker for PWA capabilities (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('SW registered: ', registration);
            })
            .catch(function(registrationError) {
                console.log('SW registration failed: ', registrationError);
            });
    });
}
