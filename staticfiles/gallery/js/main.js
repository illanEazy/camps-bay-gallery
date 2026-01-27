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

    // ARTISTS CAROUSEL - Reusable for any horizontal scrolling gallery
    // --------------------------------------------------------------------------
    let currentArtistIndex = 0;
    const artistsTrack = document.getElementById('artistsTrack');
    const artistCards = document.querySelectorAll('.artist-card');
    const totalArtistCards = artistCards.length;
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');

    function updateArtistCarousel() {
        if (artistsTrack && artistCards.length > 0) {
            const cardWidth = artistCards[0].offsetWidth + 40; // 40px gap
            artistsTrack.style.transform = `translateX(-${currentArtistIndex * cardWidth}px)`;
        }
    }

    if (prevBtn && nextBtn) {
        prevBtn.addEventListener('click', () => {
            currentArtistIndex = (currentArtistIndex - 1 + totalArtistCards) % totalArtistCards;
            updateArtistCarousel();
        });

        nextBtn.addEventListener('click', () => {
            currentArtistIndex = (currentArtistIndex + 1) % totalArtistCards;
            updateArtistCarousel();
        });
    }

    // Auto-slide artists carousel
    if (artistCards.length > 0) {
        setInterval(() => {
            currentArtistIndex = (currentArtistIndex + 1) % (totalArtistCards - 2);
            updateArtistCarousel();
        }, 3000);
    }

    window.addEventListener('resize', updateArtistCarousel);

    // MODAL FUNCTIONALITY - Reusable for any detail modal
    // --------------------------------------------------------------------------
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
        }
    ];

    const modal = document.getElementById('artworkModal');
    const modalClose = document.getElementById('modalClose');
    const viewButtons = document.querySelectorAll('.view-btn');

    if (viewButtons) {
        viewButtons.forEach((button, index) => {
            button.addEventListener('click', () => {
                if (artworkData[index]) {
                    const artwork = artworkData[index];
                    
                    document.getElementById('modalImg').src = artwork.image;
                    document.getElementById('modalTitle').textContent = artwork.title;
                    document.getElementById('modalArtist').textContent = artwork.artist;
                    document.getElementById('modalDescription').textContent = artwork.description;
                    document.getElementById('modalMedium').textContent = artwork.medium;
                    document.getElementById('modalDimensions').textContent = artwork.dimensions;
                    document.getElementById('modalYear').textContent = artwork.year;
                    
                    modal.classList.add('active');
                    document.body.style.overflow = 'hidden';
                }
            });
        });
    }

    if (modalClose) {
        modalClose.addEventListener('click', () => {
            modal.classList.remove('active');
            document.body.style.overflow = 'auto';
        });
    }

    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
                document.body.style.overflow = 'auto';
            }
        });
    }

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
});