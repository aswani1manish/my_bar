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
            scope.displayImages = [];
            scope.newImages = [];
            
            // Initialize with existing images
            scope.$watch('images', function(newVal) {
                if (newVal && Array.isArray(newVal)) {
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
                var fileInput = element.find('input[type="file"]')[0];
                if (fileInput) {
                    fileInput.click();
                }
            };
            
            // Bind the change event to the file input
            var fileInput = element.find('input[type="file"]');
            fileInput.on('change', function(event) {
                scope.handleFileSelect(event);
            });
            
            scope.handleFileSelect = function(event) {
                var files = event.target.files;
                
                for (var i = 0; i < files.length; i++) {
                    (function(file) {
                        var reader = new FileReader();
                        reader.onload = function(e) {
                            scope.$apply(function() {
                                var imageData = e.target.result;
                                scope.displayImages.push({
                                    url: imageData,
                                    data: imageData,
                                    isExisting: false
                                });
                                scope.newImages.push(imageData);
                                scope.updateImagesModel();
                            });
                        };
                        reader.readAsDataURL(file);
                    })(files[i]);
                }
                
                // Reset input
                event.target.value = '';
            };
            
            scope.removeImage = function(index) {
                var img = scope.displayImages[index];
                
                if (img.isExisting) {
                    // Mark for removal
                    if (!scope.removedImages) {
                        scope.removedImages = [];
                    }
                    scope.removedImages.push(img.filename);
                }
                
                scope.displayImages.splice(index, 1);
                scope.updateImagesModel();
            };
            
            scope.updateImagesModel = function() {
                // Update the images model with all images (existing filenames + new base64)
                scope.images = scope.displayImages.map(function(img) {
                    return img.isExisting ? img.filename : img.data;
                });
            };
        }
    };
});
