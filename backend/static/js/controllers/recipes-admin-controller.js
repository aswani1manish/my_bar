app.controller('RecipesAdminController', ['$scope', 'ApiService', 'API_URL', function($scope, ApiService, API_URL) {
    $scope.currentRecipe = {};
    $scope.isEditing = false;
    $scope.lookupId = '';
    $scope.newTag = '';
    $scope.apiUrl = API_URL;
    $scope.ingredients = [];
    $scope.collections = [];
    $scope.selectedIngredients = [];
    $scope.selectAllCollections = false;

    // Load all ingredients for selection
    $scope.loadIngredients = function() {
        ApiService.getIngredients('', '').then(function(response) {
            $scope.ingredients = response.data;
        }, function(error) {
            console.error('Error loading ingredients:', error);
            alert('Error loading ingredients. Make sure the backend is running.');
        });
    };

    // Load all collections
    $scope.loadCollections = function() {
        ApiService.getCollections('', '').then(function(response) {
            $scope.collections = response.data;
            if ($scope.currentRecipe.id) {
                $scope.updateCollectionSelections();
            }
        }, function(error) {
            console.error('Error loading collections:', error);
        });
    };

    // Update collection selections based on current recipe
    $scope.updateCollectionSelections = function() {
        if (!$scope.currentRecipe.id) {
            // Clear all selections for new recipe
            $scope.collections.forEach(function(collection) {
                collection.selected = false;
            });
            $scope.selectAllCollections = false;
            return;
        }
        
        // Mark collections that contain this recipe as selected
        $scope.collections.forEach(function(collection) {
            collection.selected = collection.recipe_ids && 
                                  collection.recipe_ids.indexOf($scope.currentRecipe.id) !== -1;
        });
        $scope.updateSelectAllState();
    };

    // Toggle all collections
    $scope.toggleAllCollections = function() {
        $scope.collections.forEach(function(collection) {
            collection.selected = $scope.selectAllCollections;
        });
    };

    // Update "select all" state based on individual selections
    $scope.updateSelectAllState = function() {
        if ($scope.collections.length === 0) {
            $scope.selectAllCollections = false;
            return;
        }
        $scope.selectAllCollections = $scope.collections.every(function(collection) {
            return collection.selected;
        });
    };

    // Lookup recipe by ID
    $scope.lookupRecipe = function() {
        if (!$scope.lookupId || isNaN($scope.lookupId)) {
            alert('Please enter a valid recipe ID');
            return;
        }

        ApiService.getRecipe(parseInt($scope.lookupId)).then(function(response) {
            $scope.currentRecipe = angular.copy(response.data);
            $scope.isEditing = true;
            
            // Ensure arrays are initialized
            if (!$scope.currentRecipe.tags) $scope.currentRecipe.tags = [];
            if (!$scope.currentRecipe.images) $scope.currentRecipe.images = [];
            if (!$scope.currentRecipe.ingredients) $scope.currentRecipe.ingredients = [];
            if (!$scope.currentRecipe.removed_images) $scope.currentRecipe.removed_images = [];
            
            // Convert ingredients to selected format
            $scope.selectedIngredients = angular.copy($scope.currentRecipe.ingredients);
            
            $scope.updateCollectionSelections();
        }, function(error) {
            console.error('Error fetching recipe:', error);
            alert('Recipe not found or error loading recipe');
        });
    };

    // Create or update recipe
    $scope.saveRecipe = function() {
        if (!$scope.currentRecipe.name) {
            alert('Please enter a recipe name');
            return;
        }

        // Update ingredients from selected
        $scope.currentRecipe.ingredients = angular.copy($scope.selectedIngredients);

        // Save recipe first, then update collections
        var savePromise;
        if ($scope.isEditing && $scope.currentRecipe.id) {
            savePromise = ApiService.updateRecipe($scope.currentRecipe.id, $scope.currentRecipe);
        } else {
            savePromise = ApiService.createRecipe($scope.currentRecipe);
        }

        savePromise.then(function(response) {
            $scope.currentRecipe = response.data;
            $scope.isEditing = true;
            $scope.lookupId = response.data.id;
            
            // Update collections based on selections
            $scope.updateCollectionsForRecipe().then(function() {
                alert('Recipe saved successfully!');
                // Reload collections to get updated data
                $scope.loadCollections();
            }, function(error) {
                console.error('Error updating collections:', error);
                alert('Recipe saved but there was an error updating collections');
            });
        }, function(error) {
            console.error('Error saving recipe:', error);
            alert('Error saving recipe');
        });
    };

    // Update collections based on checkbox selections
    $scope.updateCollectionsForRecipe = function() {
        var recipeId = $scope.currentRecipe.id;
        var updatePromises = [];

        $scope.collections.forEach(function(collection) {
            var recipeIds = collection.recipe_ids || [];
            var recipeIndex = recipeIds.indexOf(recipeId);
            var isInCollection = recipeIndex !== -1;
            var shouldBeInCollection = collection.selected;

            // Only update if there's a change
            if (isInCollection !== shouldBeInCollection) {
                var updatedRecipeIds = angular.copy(recipeIds);
                
                if (shouldBeInCollection && !isInCollection) {
                    // Add recipe to collection
                    updatedRecipeIds.push(recipeId);
                } else if (!shouldBeInCollection && isInCollection) {
                    // Remove recipe from collection
                    updatedRecipeIds.splice(recipeIndex, 1);
                }

                // Update the collection
                var updatedCollection = angular.copy(collection);
                updatedCollection.recipe_ids = updatedRecipeIds;
                updatePromises.push(ApiService.updateCollection(collection.id, updatedCollection));
            }
        });

        // Return a promise that resolves when all updates complete
        return Promise.all(updatePromises);
    };

    // Delete recipe
    $scope.deleteRecipe = function() {
        if (!$scope.currentRecipe.id) {
            alert('No recipe loaded to delete');
            return;
        }

        if (confirm('Are you sure you want to delete this recipe? This action cannot be undone.')) {
            ApiService.deleteRecipe($scope.currentRecipe.id).then(function(response) {
                alert('Recipe deleted successfully!');
                $scope.resetForm();
            }, function(error) {
                console.error('Error deleting recipe:', error);
                alert('Error deleting recipe');
            });
        }
    };

    // Add ingredient to recipe
    $scope.addIngredient = function() {
        $scope.selectedIngredients.push({
            name: '',
            amount: '',
            units: ''
        });
    };

    // Remove ingredient from recipe
    $scope.removeIngredient = function(index) {
        $scope.selectedIngredients.splice(index, 1);
    };

    // Select ingredient from dropdown
    $scope.selectIngredient = function(index, ingredientName) {
        $scope.selectedIngredients[index].name = ingredientName;
    };

    // Add tag
    $scope.addTag = function() {
        if ($scope.newTag && $scope.newTag.trim()) {
            if (!$scope.currentRecipe.tags) {
                $scope.currentRecipe.tags = [];
            }
            if ($scope.currentRecipe.tags.indexOf($scope.newTag.trim()) === -1) {
                $scope.currentRecipe.tags.push($scope.newTag.trim());
            }
            $scope.newTag = '';
        }
    };

    // Remove tag
    $scope.removeTag = function(tag) {
        var index = $scope.currentRecipe.tags.indexOf(tag);
        if (index > -1) {
            $scope.currentRecipe.tags.splice(index, 1);
        }
    };

    // Get image URL
    $scope.getImageUrl = function(filename) {
        return API_URL + '/uploads/' + filename;
    };

    // Reset form
    $scope.resetForm = function() {
        $scope.currentRecipe = {
            tags: [],
            images: [],
            ingredients: [],
            removed_images: []
        };
        $scope.isEditing = false;
        $scope.lookupId = '';
        $scope.newTag = '';
        $scope.selectedIngredients = [];
        $scope.selectAllCollections = false;
        $scope.updateCollectionSelections();
    };

    // Initialize
    $scope.resetForm();
    $scope.loadIngredients();
    $scope.loadCollections();
}]);
