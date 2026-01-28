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

    // ARTISTS CAROUSEL - WORKING VERSION
    // --------------------------------------------------------------------------
    let currentIndex = 0;
    const track = document.getElementById('artistsTrack');
    const cards = document.querySelectorAll('.artist-card');
    const totalCards = cards.length;
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');

    if (track && cards.length > 0 && prevBtn && nextBtn) {
        function updateCarousel() {
            // Calculate card width including gap
            if (cards.length === 0) return;
            
            // Get the actual width of a card
            const cardWidth = cards[0].offsetWidth;
            const gap = 40; // From CSS gap: 40px
            
            // Move track by (card width + gap) * current index
            const translateX = currentIndex * (cardWidth + gap);
            track.style.transform = `translateX(-${translateX}px)`;
            
            console.log('Carousel updated - Index:', currentIndex, 'Translate:', translateX);
        }

        // Previous button click
        prevBtn.addEventListener('click', () => {
            currentIndex = Math.max(0, currentIndex - 1);
            updateCarousel();
        });

        // Next button click
        nextBtn.addEventListener('click', () => {
            // Max index is total cards - 3 (since we show 3 at a time)
            const maxIndex = Math.max(0, totalCards - 3);
            currentIndex = Math.min(maxIndex, currentIndex + 1);
            updateCarousel();
        });

        // Auto-slide every 3 seconds
        const autoSlideInterval = setInterval(() => {
            const maxIndex = Math.max(0, totalCards - 3);
            
            if (currentIndex >= maxIndex) {
                currentIndex = 0; // Loop back to start
            } else {
                currentIndex++;
            }
            
            updateCarousel();
        }, 3000);

        // Stop auto-slide when user interacts
        let userInteracted = false;
        
        prevBtn.addEventListener('click', () => {
            userInteracted = true;
            clearInterval(autoSlideInterval);
        });
        
        nextBtn.addEventListener('click', () => {
            userInteracted = true;
            clearInterval(autoSlideInterval);
        });

        // Handle window resize
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(updateCarousel, 250);
        });
        
        // Initial position - wait for images to load
        window.addEventListener('load', () => {
            setTimeout(updateCarousel, 100);
        });
        
        // Also update after a short delay
        setTimeout(updateCarousel, 500);
    }

    // MODAL FUNCTIONALITY - Reusable for any detail modal
    // --------------------------------------------------------------------------
    // Remove or comment out the modal functionality for grid cards
    // Keep it only for detail page later
    
    // Instead, update the button click handlers to use the new URLs
    // We'll handle modals only on detail pages

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

    // Keep countdown and other existing functionality
    // Remove modal triggers for artwork cards in grid

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
});