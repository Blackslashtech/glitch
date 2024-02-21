const emojis = ['👽', '👾', '🛸', '🌌', '🌠', '⭐'];
const numberOfAliens = 25;
const aliensLayer = document.getElementById('aliens-layer');

for (let i = 0; i < numberOfAliens; i++) {
    createAlien();
}

function createAlien() {
    const alien = document.createElement('div');
    alien.className = 'alien';
    alien.innerText = emojis[Math.floor(Math.random() * emojis.length)];

    const startX = Math.random() * window.innerWidth;
    const startY = Math.random() * window.innerHeight;

    alien.style.left = `${startX}px`;
    alien.style.top = `${startY}px`;

    const randomSize = Math.random() * 2.0 + 1.0;
    alien.style.fontSize = `${randomSize}em`;

    animateAlien(alien);
    aliensLayer.appendChild(alien);
}

function animateAlien(alien) {
    const animationDuration = Math.random() * 10 + 5;
    const rotationSpeed = Math.random() * 90 - 45;

    alien.style.animation = `moveAlien ${animationDuration}s linear infinite, rotateAlien ${rotationSpeed}s linear infinite`;

    setInterval(() => {
        const deltaX = (Math.random() - 0.5) * 1000;
        const deltaY = (Math.random() - 0.5) * 200;
        
        const currentLeft = parseFloat(alien.style.left);
        const currentTop = parseFloat(alien.style.top);
        
        const newX = currentLeft + deltaX;
        const newY = currentTop + deltaY;

        alien.style.left = `${newX}px`;
        alien.style.top = `${newY}px`;
    }, 2000);
}