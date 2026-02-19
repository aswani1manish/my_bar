// Gallery JavaScript

let galleryImages = [];
let currentModalIndex = 0;
let bsModal = null;

// Load gallery images on page load
document.addEventListener('DOMContentLoaded', function() {
    loadGalleryImages();
    
    // Handle modal close - prevent aria-hidden warning
    const modalElement = document.getElementById('imageModal');
    if (modalElement) {
        // Before modal hides, blur any focused element to prevent aria-hidden warning
        modalElement.addEventListener('hide.bs.modal', function() {
            // Remove focus from any element inside the modal
            const focusedElement = document.activeElement;
            if (focusedElement && modalElement.contains(focusedElement)) {
                focusedElement.blur();
            }
        });
    }

    // Keyboard navigation for modal
    document.addEventListener('keydown', function(e) {
        const modalElement = document.getElementById('imageModal');
        if (modalElement && modalElement.classList.contains('show')) {
            if (e.key === 'ArrowLeft') navigateModal(-1);
            else if (e.key === 'ArrowRight') navigateModal(1);
        }
    });
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

// Render the gallery (always mosaic view)
function renderGallery() {
    const container = document.getElementById('galleryContainer');
    renderMosaicView(container);
}

// Render mosaic (grid) view
function renderMosaicView(container) {
    const html = `
        <div class="gallery-mosaic">
            ${galleryImages.map((img, index) => `
                <div class="gallery-mosaic-item" onclick="openImageModal(${index})">
                    <img src="${img.url}" alt="${img.filename}" loading="lazy">
                </div>
            `).join('')}
        </div>
    `;
    container.innerHTML = html;
}

// Open image in modal by index
function openImageModal(index) {
    currentModalIndex = index;
    const img = galleryImages[index];
    const modalElement = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    const modalLabel = document.getElementById('imageModalLabel');
    
    modalImage.src = img.url;
    modalLabel.textContent = img.filename;
    updateModalNavButtons();
    
    // Use Bootstrap if available, otherwise show manually
    if (typeof bootstrap !== 'undefined') {
        if (!bsModal) {
            bsModal = new bootstrap.Modal(modalElement);
        }
        bsModal.show();
    } else {
        // Fallback: show modal manually
        modalElement.classList.add('show');
        modalElement.style.display = 'block';
        document.body.classList.add('modal-open');
        
        // Create backdrop (only once)
        if (!document.getElementById('modalBackdrop')) {
            const backdrop = document.createElement('div');
            backdrop.classList.add('modal-backdrop', 'fade', 'show');
            backdrop.id = 'modalBackdrop';
            document.body.appendChild(backdrop);

            const closeModal = () => {
                modalElement.classList.remove('show');
                modalElement.style.display = 'none';
                document.body.classList.remove('modal-open');
                const existingBackdrop = document.getElementById('modalBackdrop');
                if (existingBackdrop) {
                    existingBackdrop.remove();
                }
            };
            backdrop.addEventListener('click', closeModal);
            const closeBtn = modalElement.querySelector('.btn-close');
            if (closeBtn) {
                closeBtn.onclick = closeModal;
            }
        } else {
            // Backdrop already exists; just show the modal
            modalElement.classList.add('show');
            modalElement.style.display = 'block';
        }
    }
}

// Navigate to previous (-1) or next (+1) image in the modal
function navigateModal(direction) {
    const newIndex = currentModalIndex + direction;
    if (newIndex < 0 || newIndex >= galleryImages.length) return;
    currentModalIndex = newIndex;
    const img = galleryImages[currentModalIndex];
    document.getElementById('modalImage').src = img.url;
    document.getElementById('imageModalLabel').textContent = img.filename;
    updateModalNavButtons();
}

// Show/hide navigation buttons based on current index
function updateModalNavButtons() {
    const prevBtn = document.getElementById('modalPrevBtn');
    const nextBtn = document.getElementById('modalNextBtn');
    if (prevBtn) prevBtn.style.visibility = currentModalIndex > 0 ? 'visible' : 'hidden';
    if (nextBtn) nextBtn.style.visibility = currentModalIndex < galleryImages.length - 1 ? 'visible' : 'hidden';
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
