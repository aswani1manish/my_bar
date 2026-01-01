app.controller('RecipesAdminController', ['$scope', 'ApiService', 'API_URL', function($scope, ApiService, API_URL) {
    $scope.currentRecipe = {};
    $scope.isEditing = false;
    $scope.lookupId = '';
    $scope.newTag = '';
    $scope.apiUrl = API_URL;
    $scope.ingredients = [];
    $scope.collections = [];
    $scope.recipeCollections = [];
    $scope.selectedIngredients = [];

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
                $scope.loadRecipeCollections();
            }
        }, function(error) {
            console.error('Error loading collections:', error);
        });
    };

    // Load collections that contain this recipe
    $scope.loadRecipeCollections = function() {
        if (!$scope.currentRecipe.id) {
            $scope.recipeCollections = [];
            return;
        }
        
        $scope.recipeCollections = $scope.collections.filter(function(collection) {
            return collection.recipe_ids && collection.recipe_ids.indexOf($scope.currentRecipe.id) !== -1;
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
            
            $scope.loadRecipeCollections();
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

        if ($scope.isEditing && $scope.currentRecipe.id) {
            ApiService.updateRecipe($scope.currentRecipe.id, $scope.currentRecipe).then(function(response) {
                alert('Recipe updated successfully!');
                $scope.currentRecipe = response.data;
                $scope.isEditing = true;
                $scope.loadRecipeCollections();
            }, function(error) {
                console.error('Error updating recipe:', error);
                alert('Error updating recipe');
            });
        } else {
            ApiService.createRecipe($scope.currentRecipe).then(function(response) {
                alert('Recipe created successfully with ID: ' + response.data.id);
                $scope.currentRecipe = response.data;
                $scope.isEditing = true;
                $scope.lookupId = response.data.id;
                $scope.loadRecipeCollections();
            }, function(error) {
                console.error('Error creating recipe:', error);
                alert('Error creating recipe');
            });
        }
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
        $scope.recipeCollections = [];
    };

    // Initialize
    $scope.resetForm();
    $scope.loadIngredients();
    $scope.loadCollections();
}]);
