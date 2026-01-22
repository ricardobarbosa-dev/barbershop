const sr = ScrollReveal({
    distance: '60px',
    duration: 900,
    easing: 'cubic-bezier(0.25, 0.1, 0.25, 1)',
    reset: false
});

sr.reveal('.hero h1', {
    origin: 'top',
    delay: 100
});

sr.reveal('.hero p', {
    origin: 'top',
    delay: 200
});

sr.reveal('.hero .btn-contact', {
    origin: 'bottom',
    delay: 300
});

sr.reveal('.bounce', {
    origin: 'bottom',
    delay: 500
});

sr.reveal('.title-popular h2', {
    origin: 'left',
    delay: 100
});

sr.reveal('.title-popular p', {
    origin: 'right',
    delay: 200
});


sr.reveal('.service-card', {
    origin: 'bottom',
    interval: 150
});

sr.reveal('.about-us .description', {
    origin: 'left',
    interval: 150
});

sr.reveal('.about-img', {
    origin: 'right',
    delay: 200
});


sr.reveal('.stat-item', {
    scale: 0.85,
    interval: 120
});


sr.reveal('.team-member', {
    origin: 'bottom',
    interval: 200
});


sr.reveal('.location', {
    origin: 'left'
});

sr.reveal('.location-info', {
    origin: 'bottom',
    interval: 120
});

sr.reveal('footer', {
    origin: 'bottom',
    delay: 100
});
