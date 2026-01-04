// Gallery JavaScript

let currentView = 'mosaic';
let galleryImages = [];

// Load gallery images on page load
document.addEventListener('DOMContentLoaded', function() {
    loadGalleryImages();
});

// Load images from the API
async function loadGalleryImages() {
    try {
        const response = await fetch('/api/gallery/images');
        const data = await response.json();
        
        if (data.images && data.images.length > 0) {
            galleryImages = data.images;
            renderGallery();
        } else {
            showEmptyState();
        }
    } catch (error) {
        console.error('Error loading gallery images:', error);
        showErrorState();
    }
}

// Render the gallery based on current view
function renderGallery() {
    const container = document.getElementById('galleryContainer');
    
    if (currentView === 'mosaic') {
        renderMosaicView(container);
    } else {
        renderRibbonView(container);
    }
}

// Render mosaic (grid) view
function renderMosaicView(container) {
    const html = `
        <div class="gallery-mosaic">
            ${galleryImages.map((img, index) => `
                <div class="gallery-mosaic-item" onclick="openImageModal('${img.url}', '${img.filename}')">
                    <img src="${img.url}" alt="${img.filename}" loading="lazy">
                </div>
            `).join('')}
        </div>
    `;
    container.innerHTML = html;
}

// Render ribbon (horizontal strip) view
function renderRibbonView(container) {
    const html = `
        <div class="gallery-ribbon">
            ${galleryImages.map((img, index) => `
                <div class="gallery-ribbon-item" onclick="openImageModal('${img.url}', '${img.filename}')">
                    <img src="${img.url}" alt="${img.filename}" loading="lazy">
                </div>
            `).join('')}
        </div>
    `;
    container.innerHTML = html;
}

// Switch between mosaic and ribbon views
function switchView(view) {
    currentView = view;
    
    // Update button states
    const mosaicBtn = document.getElementById('mosaicViewBtn');
    const ribbonBtn = document.getElementById('ribbonViewBtn');
    
    if (view === 'mosaic') {
        mosaicBtn.classList.add('active');
        ribbonBtn.classList.remove('active');
    } else {
        ribbonBtn.classList.add('active');
        mosaicBtn.classList.remove('active');
    }
    
    // Re-render gallery
    renderGallery();
}

// Open image in modal
function openImageModal(imageUrl, filename) {
    const modal = new bootstrap.Modal(document.getElementById('imageModal'));
    const modalImage = document.getElementById('modalImage');
    const modalLabel = document.getElementById('imageModalLabel');
    
    modalImage.src = imageUrl;
    modalLabel.textContent = filename;
    
    modal.show();
}

// Show empty state when no images are found
function showEmptyState() {
    const container = document.getElementById('galleryContainer');
    container.innerHTML = `
        <div class="gallery-empty">
            <i class="fas fa-images"></i>
            <h4>No Images Found</h4>
            <p>The gallery is currently empty. Please add some images to the gallery folder.</p>
        </div>
    `;
}

// Show error state when loading fails
function showErrorState() {
    const container = document.getElementById('galleryContainer');
    container.innerHTML = `
        <div class="gallery-empty">
            <i class="fas fa-exclamation-triangle"></i>
            <h4>Error Loading Gallery</h4>
            <p>There was an error loading the gallery images. Please try again later.</p>
        </div>
    `;
}
