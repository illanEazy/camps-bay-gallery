// ==========================================================================
// MAIN JAVASCRIPT FILE - REUSABLE FUNCTIONS FOR ENTIRE SITE
// ==========================================================================

document.addEventListener('DOMContentLoaded', function() {
    // CAROUSEL FUNCTIONALITY - Reusable for any image carousel
    // --------------------------------------------------------------------------
    let currentSlide = 0;
    const slides = document.querySelectorAll('.carousel-slide');
    const dots = document.querySelectorAll('.carousel-dots .dot');
    const totalSlides = slides.length;

    function showSlide(n) {
        slides.forEach(slide => slide.classList.remove('active'));
        dots.forEach(dot => dot.classList.remove('active'));
        currentSlide = (n + totalSlides) % totalSlides;
        slides[currentSlide].classList.add('active');
        dots[currentSlide].classList.add('active');
    }

    function nextSlide() {
        showSlide(currentSlide + 1);
    }

    // Auto-advance carousel every 5 seconds
    if (totalSlides > 0) {
        setInterval(nextSlide, 5000);
    }

    // Dot click events
    dots.forEach(dot => {
        dot.addEventListener('click', () => {
            const slideIndex = parseInt(dot.getAttribute('data-slide'));
            showSlide(slideIndex);
        });
    });

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') showSlide(currentSlide - 1);
        if (e.key === 'ArrowRight') showSlide(currentSlide + 1);
    });

    // COUNTDOWN TIMER - Reusable for any event countdown
    // --------------------------------------------------------------------------
    function updateCountdown() {
        const eventDate = new Date('2026-01-20');
        const now = new Date();
        const diff = Math.floor((eventDate - now) / (1000 * 60 * 60 * 24));
        const countdownElement = document.getElementById('countdown');
        if (countdownElement) {
            countdownElement.textContent = diff > 0 ? `${diff} DAYS` : 'TODAY';
        }
    }
    
    updateCountdown();
    setInterval(updateCountdown, 3600000); // Update every hour

    // ARTISTS CAROUSEL - WORKING VERSION (NOW DYNAMIC)
    // --------------------------------------------------------------------------
    let currentIndex = 0;
    const track = document.getElementById('artistsTrack');
    const cards = document.querySelectorAll('.artist-card');
    const totalCards = cards.length;
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');

    if (track && cards.length > 0 && prevBtn && nextBtn) {
        function updateCarousel() {
            if (cards.length === 0) return;
            
            // Calculate card width including gap
            const cardWidth = cards[0].offsetWidth;
            const gap = 40;
            
            // Move track by (card width + gap) * current index
            const translateX = currentIndex * (cardWidth + gap);
            track.style.transform = `translateX(-${translateX}px)`;
        }

        // Previous button click
        prevBtn.addEventListener('click', () => {
            currentIndex = Math.max(0, currentIndex - 1);
            updateCarousel();
        });

        // Next button click
        nextBtn.addEventListener('click', () => {
            // Show 3 cards at a time
            const visibleCards = window.innerWidth < 768 ? 1 : (window.innerWidth < 1200 ? 2 : 3);
            const maxIndex = Math.max(0, totalCards - visibleCards);
            currentIndex = Math.min(maxIndex, currentIndex + 1);
            updateCarousel();
        });

        // Auto-slide every 5 seconds (only if there are more than visible cards)
        if (totalCards > 3) {
            const autoSlideInterval = setInterval(() => {
                const visibleCards = window.innerWidth < 768 ? 1 : (window.innerWidth < 1200 ? 2 : 3);
                const maxIndex = Math.max(0, totalCards - visibleCards);
                
                if (currentIndex >= maxIndex) {
                    currentIndex = 0;
                } else {
                    currentIndex++;
                }
                
                updateCarousel();
            }, 5000);

            // Stop auto-slide when user interacts
            prevBtn.addEventListener('click', () => {
                clearInterval(autoSlideInterval);
            });
            
            nextBtn.addEventListener('click', () => {
                clearInterval(autoSlideInterval);
            });
        }

        // Handle window resize
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(updateCarousel, 250);
        });
        
        // Initial position
        window.addEventListener('load', updateCarousel);
        setTimeout(updateCarousel, 500);
    }

    // ARTWORK DATA - Keep for reference but don't use modal for grid
    const artworkData = [
        {
            title: 'Coastal Abstractions',
            artist: 'Amara Thompson',
            description: 'A meditation on the meeting of land and sea. Thompson captures the essence of Camps Bay through layered textures and a palette drawn from the coastal landscape.',
            medium: 'Mixed Media on Canvas',
            dimensions: '120 × 100 cm',
            year: '2025',
            image: 'https://images.unsplash.com/photo-1549887534-1541e9326642?w=800&h=800&fit=crop'
        },
        {
            title: 'Equilibrium III',
            artist: 'Marcus Chen',
            description: "Part of Chen's ongoing exploration of balance and form. This sculptural work plays with weight, shadow, and the negative space between elements.",
            medium: 'Bronze Sculpture',
            dimensions: '85 × 45 × 30 cm',
            year: '2024',
            image: 'https://images.unsplash.com/photo-1561214115-f2f134cc4912?w=800&h=800&fit=crop'
        },
        {
            title: 'City Fragments',
            artist: 'Sofia Rodriguez',
            description: 'Rodriguez deconstructs urban landscapes into geometric fragments, revealing the hidden patterns and rhythms of contemporary life.',
            medium: 'Acrylic on Canvas',
            dimensions: '150 × 120 cm',
            year: '2025',
            image: 'https://images.unsplash.com/photo-1578301978018-3005759f48f7?w=800&h=800&fit=crop'
        },
        {
            title: 'Silent Spaces',
            artist: 'James Williams',
            description: 'A minimalist exploration of emptiness and presence. Williams invites contemplation through carefully considered negative space and subtle tonal shifts.',
            medium: 'Oil on Linen',
            dimensions: '100 × 100 cm',
            year: '2024',
            image: 'https://images.unsplash.com/photo-1547826039-bfc35e0f1ea8?w=800&h=800&fit=crop'
        },
        {
            title: 'Earth Memory',
            artist: 'Zara Okafor',
            description: "Okafor's textured surfaces evoke geological time and ancient landscapes. Each layer tells a story of transformation and permanence.",
            medium: 'Mixed Media with Natural Pigments',
            dimensions: '110 × 90 cm',
            year: '2025',
            image: 'https://images.unsplash.com/photo-1536924940846-227afb31e2a5?w=800&h=800&fit=crop'
        },
        {
            title: 'Presence',
            artist: 'Kai Nakamura',
            description: 'A contemporary take on portraiture that questions identity and perception. Nakamura\'s work exists between representation and abstraction.',
            medium: 'Digital Print on Archival Paper',
            dimensions: '130 × 95 cm',
            year: '2025',
            image: 'https://images.unsplash.com/photo-1579762715118-a6f1d4b934f1?w=800&h=800&fit=crop'
        },
        {
            title: 'Linear Tensions',
            artist: 'Amara Thompson',
            description: 'Thompson returns to geometric abstraction, creating visual tension through intersecting lines and carefully balanced composition.',
            medium: 'Acrylic and Graphite on Canvas',
            dimensions: '140 × 110 cm',
            year: '2024',
            image: 'https://images.unsplash.com/photo-1577083288073-40892c0860fd?w=800&h=800&fit=crop'
        },
        {
            title: 'Flow State',
            artist: 'Marcus Chen',
            description: 'Chen\'s organic forms seem to move and breathe. This piece captures a moment of transformation, frozen in bronze.',
            medium: 'Bronze Sculpture',
            dimensions: '95 × 60 × 40 cm',
            year: '2025',
            image: 'https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=800&h=800&fit=crop'
        },
        {
            title: 'Layered Narratives',
            artist: 'Sofia Rodriguez',
            description: 'Rodriguez weaves together fragments of text, image, and paint to create a rich tapestry of meaning and memory.',
            medium: 'Mixed Media Collage',
            dimensions: '125 × 100 cm',
            year: '2025',
            image: 'https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=800&h=800&fit=crop'
        }
    ];

    // EXPLORE BUTTON - Reusable smooth scroll functionality
    // --------------------------------------------------------------------------
    const exploreBtn = document.querySelector('.explore-btn');
    if (exploreBtn) {
        exploreBtn.addEventListener('click', () => {
            const spaceSection = document.querySelector('.space-section');
            if (spaceSection) {
                window.scrollTo({
                    top: spaceSection.offsetTop - 100,
                    behavior: 'smooth'
                });
            }
        });
    }

    // ==========================================================================
    // CONTACT FORM HANDLING - REUSABLE FOR ANY FORM
    // ==========================================================================

    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Basic form validation
            const firstName = document.getElementById('firstName').value.trim();
            const lastName = document.getElementById('lastName').value.trim();
            const email = document.getElementById('email').value.trim();
            const message = document.getElementById('message').value.trim();
            
            if (!firstName || !lastName || !email || !message) {
                alert('Please fill in all required fields.');
                return;
            }
            
            // Email validation
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                alert('Please enter a valid email address.');
                return;
            }
            
            // Here you would typically send the form data to your Django backend
            // Example using Fetch API:
            /*
            const formData = new FormData(this);
            fetch('/api/contact/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Thank you for reaching out! We will get back to you soon.');
                    this.reset();
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Something went wrong. Please try again.');
            });
            */
            
            // For now, just show a success message
            alert('Thank you for reaching out! We will get back to you soon.');
            this.reset();
        });
    }

    // Helper function for CSRF token (if using Django CSRF protection)
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

    // ==========================================================================
    // ARTWORKS PAGE FILTERING - MINIMAL ADDITION
    // ==========================================================================
    
    // This is already handled in the template's extra_js block
    // No additional JavaScript needed for modal - it already works!

    // ==========================================================================
    // PASSWORD TOGGLE FUNCTIONALITY - REUSABLE
    // ==========================================================================

    function initPasswordToggles() {
        document.querySelectorAll('.toggle-password').forEach(function(button) {
            button.addEventListener('click', function() {
                const targetId = this.getAttribute('data-target');
                const passwordInput = document.getElementById(targetId);
                const icon = this.querySelector('i');
                
                if (passwordInput && icon) {
                    if (passwordInput.type === 'password') {
                        passwordInput.type = 'text';
                        icon.classList.remove('fa-eye');
                        icon.classList.add('fa-eye-slash');
                    } else {
                        passwordInput.type = 'password';
                        icon.classList.remove('fa-eye-slash');
                        icon.classList.add('fa-eye');
                    }
                }
            });
        });
    }

    // Initialize when DOM is loaded
    initPasswordToggles();

    // ============================================================================
    // MODAL FUNCTIONALITY - REUSABLE (NEW ADDITION)
    // ============================================================================
    
    // Handle modal open/close for any modal
    function setupModal(modalId, openButtonId, closeButtonId, cancelButtonId = null) {
        const modal = document.getElementById(modalId);
        const openBtn = document.getElementById(openButtonId);
        const closeBtn = document.getElementById(closeButtonId);
        const cancelBtn = cancelButtonId ? document.getElementById(cancelButtonId) : null;
        
        if (openBtn && modal) {
            openBtn.addEventListener('click', function() {
                modal.classList.add('active');
                document.body.style.overflow = 'hidden';
            });
        }
        
        if (closeBtn && modal) {
            closeBtn.addEventListener('click', function() {
                modal.classList.remove('active');
                document.body.style.overflow = 'auto';
            });
        }
        
        if (cancelBtn && modal) {
            cancelBtn.addEventListener('click', function() {
                modal.classList.remove('active');
                document.body.style.overflow = 'auto';
            });
        }
        
        if (modal) {
            modal.addEventListener('click', function(e) {
                if (e.target === modal) {
                    modal.classList.remove('active');
                    document.body.style.overflow = 'auto';
                }
            });
        }
    }
    
    // Set up all modals
    setupModal('inquiryModal', 'openInquiryModal', 'closeInquiryModal', 'cancelInquiry');
    setupModal('scheduleModal', 'openScheduleModal', 'closeScheduleModal', 'cancelSchedule');
    setupModal('addToCartModal', 'openAddToCartModal', 'closeAddToCartModal');
    
    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal-overlay.active').forEach(modal => {
                modal.classList.remove('active');
                document.body.style.overflow = 'auto';
            });
        }
    });
    
    // ============================================================================
    // FORM VALIDATION - REUSABLE (NEW ADDITION)
    // ============================================================================
    
    function setupFormValidation(formId) {
        const form = document.getElementById(formId);
        if (!form) return;
        
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.style.borderColor = '#e74c3c';
                    
                    // Add error message if not exists
                    if (!field.nextElementSibling || !field.nextElementSibling.classList.contains('error-message')) {
                        const errorMsg = document.createElement('div');
                        errorMsg.className = 'error-message';
                        errorMsg.textContent = 'This field is required';
                        errorMsg.style.color = '#e74c3c';
                        errorMsg.style.fontSize = '0.875rem';
                        errorMsg.style.marginTop = '0.25rem';
                        field.parentNode.insertBefore(errorMsg, field.nextSibling);
                    }
                } else {
                    field.style.borderColor = '';
                    
                    // Remove error message if exists
                    const errorMsg = field.nextElementSibling;
                    if (errorMsg && errorMsg.classList.contains('error-message')) {
                        errorMsg.remove();
                    }
                }
            });
            
            // Email validation
            const emailField = form.querySelector('input[type="email"][required]');
            if (emailField && emailField.value.trim()) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(emailField.value.trim())) {
                    isValid = false;
                    emailField.style.borderColor = '#e74c3c';
                    
                    if (!emailField.nextElementSibling || !emailField.nextElementSibling.classList.contains('error-message')) {
                        const errorMsg = document.createElement('div');
                        errorMsg.className = 'error-message';
                        errorMsg.textContent = 'Please enter a valid email address';
                        errorMsg.style.color = '#e74c3c';
                        errorMsg.style.fontSize = '0.875rem';
                        errorMsg.style.marginTop = '0.25rem';
                        emailField.parentNode.insertBefore(errorMsg, emailField.nextSibling);
                    }
                }
            }
            
            if (!isValid) {
                e.preventDefault();
                return false;
            }
            
            // Show loading state
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            }
            
            return true;
        });
    }
    
    // Set up form validation
    setupFormValidation('inquiryForm');
    setupFormValidation('scheduleForm');
    
    // ============================================================================
    // AUTO-SHOW INQUIRY MODAL FOR "ON REQUEST" ARTWORKS (NEW ADDITION)
    // ============================================================================
    
    // Check if we're on an artwork detail page
    const artworkAvailability = document.querySelector('.artwork-availability .availability-tag');
    if (artworkAvailability && artworkAvailability.textContent.includes('Request')) {
        // Auto-show inquiry modal after 1 second
        setTimeout(() => {
            const inquiryModal = document.getElementById('inquiryModal');
            if (inquiryModal) {
                inquiryModal.classList.add('active');
                document.body.style.overflow = 'hidden';
            }
        }, 1000);
    }
});