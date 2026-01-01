app.directive('imageUpload', function() {
    return {
        restrict: 'E',
        scope: {
            images: '=',
            removedImages: '=',
            apiUrl: '@'
        },
        template: `
            <div class="mb-3">
                <label class="form-label">Images</label>
                
                <!-- Upload Area -->
                <div class="image-upload-container" ng-click="triggerFileInput()">
                    <input type="file" id="file-input-{{$id}}" multiple accept="image/*" 
                           style="display: none;">
                    <i class="fas fa-cloud-upload-alt fa-3x mb-2"></i>
                    <p class="mb-0">Click to upload images</p>
                    <small class="text-muted">PNG, JPG, GIF up to 16MB</small>
                </div>
                
                <!-- Image Previews -->
                <div class="image-preview-container" ng-if="displayImages.length > 0">
                    <div class="image-preview" ng-repeat="img in displayImages track by $index">
                        <img ng-src="{{img.url}}" alt="Preview">
                        <button type="button" class="remove-image" ng-click="removeImage($index)">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
            </div>
        `,
        link: function(scope, element, attrs) {
            console.log('[ImageUpload] Directive initialized');
            scope.displayImages = [];
            scope.newImages = [];
            
            // Get file input reference - use querySelector since jqLite doesn't support attribute selectors
            var fileInput = null;
            
            // Use $timeout to ensure DOM is ready
            setTimeout(function() {
                var inputElement = element[0].querySelector('input[type="file"]');
                if (inputElement) {
                    fileInput = angular.element(inputElement);
                    console.log('[ImageUpload] File input element found:', fileInput);
                    
                    // Bind the change event to the file input
                    fileInput.on('change', function(event) {
                        console.log('[ImageUpload] File input change event triggered');
                        scope.handleFileSelect(event);
                    });
                } else {
                    console.error('[ImageUpload] File input element not found!');
                }
            }, 0);
            
            // Initialize with existing images
            scope.$watch('images', function(newVal) {
                if (newVal && Array.isArray(newVal)) {
                    console.log('[ImageUpload] Initializing with existing images:', newVal);
                    scope.displayImages = newVal.map(function(img) {
                        return {
                            url: scope.apiUrl + '/uploads/' + img,
                            filename: img,
                            isExisting: true
                        };
                    });
                }
            }, true);
            
            scope.triggerFileInput = function() {
                console.log('[ImageUpload] triggerFileInput called, fileInput:', fileInput);
                if (fileInput && fileInput[0]) {
                    console.log('[ImageUpload] Clicking file input');
                    fileInput[0].click();
                } else {
                    console.error('[ImageUpload] File input not available for click');
                }
            };
            
            scope.handleFileSelect = function(event) {
                console.log('[ImageUpload] handleFileSelect called');
                var files = event.target.files;
                console.log('[ImageUpload] Number of files selected:', files.length);
                
                for (var i = 0; i < files.length; i++) {
                    (function(file) {
                        console.log('[ImageUpload] Processing file:', file.name, 'type:', file.type, 'size:', file.size);
                        var reader = new FileReader();
                        reader.onload = function(e) {
                            console.log('[ImageUpload] File read complete for:', file.name);
                            scope.$apply(function() {
                                var imageData = e.target.result;
                                scope.displayImages.push({
                                    url: imageData,
                                    data: imageData,
                                    isExisting: false
                                });
                                scope.newImages.push(imageData);
                                scope.updateImagesModel();
                                console.log('[ImageUpload] Image added to displayImages, total count:', scope.displayImages.length);
                            });
                        };
                        reader.onerror = function(error) {
                            console.error('[ImageUpload] Error reading file:', file.name, error);
                        };
                        reader.readAsDataURL(file);
                    })(files[i]);
                }
                
                // Reset input
                event.target.value = '';
            };
            
            scope.removeImage = function(index) {
                console.log('[ImageUpload] Removing image at index:', index);
                var img = scope.displayImages[index];
                
                if (img.isExisting) {
                    // Mark for removal
                    if (!scope.removedImages) {
                        scope.removedImages = [];
                    }
                    scope.removedImages.push(img.filename);
                    console.log('[ImageUpload] Marked existing image for removal:', img.filename);
                }
                
                scope.displayImages.splice(index, 1);
                scope.updateImagesModel();
                console.log('[ImageUpload] Image removed, remaining count:', scope.displayImages.length);
            };
            
            scope.updateImagesModel = function() {
                // Update the images model with all images (existing filenames + new base64)
                scope.images = scope.displayImages.map(function(img) {
                    return img.isExisting ? img.filename : img.data;
                });
                console.log('[ImageUpload] Images model updated, count:', scope.images.length);
            };
        }
    };
});
