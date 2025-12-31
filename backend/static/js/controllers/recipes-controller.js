app.controller('RecipesController', ['$scope', 'ApiService', 'API_URL', function($scope, ApiService, API_URL) {
    $scope.recipes = [];
    $scope.allRecipes = [];
    $scope.ingredients = [];
    $scope.collections = [];
    $scope.currentRecipe = {};
    $scope.isEditing = false;
    $scope.searchQuery = '';
    $scope.tagSearch = '';
    $scope.selectedCollection = '';
    $scope.newTag = '';
    $scope.newIngredient = {};
    $scope.apiUrl = API_URL;
    $scope.selectedRecipe = {};

    // Load all recipes
    $scope.loadRecipes = function() {
        
        // Load collections first, then recipes.
        $scope.loadCollections();
        ApiService.getRecipes($scope.searchQuery, $scope.tagSearch).then(function(response) {
            $scope.allRecipes = response.data;
            $scope.filterRecipesByCollection();
        }, function(error) {
            console.error('Error loading recipes:', error);
            alert('Error loading recipes. Make sure the backend is running.');
        });
    };

    // Load all ingredients for dropdown
    $scope.loadIngredients = function() {
        ApiService.getIngredients('', '').then(function(response) {
            $scope.ingredients = response.data;
        }, function(error) {
            console.error('Error loading ingredients:', error);
        });
    };

    // Load all collections for dropdown
    $scope.loadCollections = function() {
        ApiService.getCollections('', '').then(function(response) {
            $scope.collections = response.data;
        }, function(error) {
            console.error('Error loading collections:', error);
        });
    };

    // Filter recipes by selected collection
    $scope.filterRecipesByCollection = function() {
        if (!$scope.selectedCollection) {
            // Show all recipes when no collection is selected
            $scope.recipes = $scope.allRecipes;
        } else {
            // Find the selected collection
            var collection = $scope.collections.find(function(c) {
                return c.id === parseInt($scope.selectedCollection);
            });
            
            if (collection && collection.recipe_ids) {
                // Filter recipes to only those in the collection
                $scope.recipes = $scope.allRecipes.filter(function(recipe) {
                    return collection.recipe_ids.indexOf(recipe.id) !== -1;
                });
            } else {
                $scope.recipes = [];
            }
        }
    };

    // Search recipes
    $scope.search = function() {
        $scope.loadRecipes();
    };

    // // Create or update recipe
    // $scope.saveRecipe = function() {
    //     if (!$scope.currentRecipe.name) {
    //         alert('Please enter a recipe name');
    //         return;
    //     }

    //     if ($scope.isEditing) {
    //         ApiService.updateRecipe($scope.currentRecipe._id, $scope.currentRecipe).then(function(response) {
    //             $scope.loadRecipes();
    //             $scope.resetForm();
    //         }, function(error) {
    //             console.error('Error updating recipe:', error);
    //             alert('Error updating recipe');
    //         });
    //     } else {
    //         ApiService.createRecipe($scope.currentRecipe).then(function(response) {
    //             $scope.loadRecipes();
    //             $scope.resetForm();
    //         }, function(error) {
    //             console.error('Error creating recipe:', error);
    //             alert('Error creating recipe');
    //         });
    //     }
    // };

    // // Edit recipe
    // $scope.editRecipe = function(recipe) {
    //     $scope.currentRecipe = angular.copy(recipe);
    //     $scope.isEditing = true;
    //     window.scrollTo(0, 0);
    // };

    // // Delete recipe
    // $scope.deleteRecipe = function(id) {
    //     if (confirm('Are you sure you want to delete this recipe?')) {
    //         ApiService.deleteRecipe(id).then(function(response) {
    //             $scope.loadRecipes();
    //         }, function(error) {
    //             console.error('Error deleting recipe:', error);
    //             alert('Error deleting recipe');
    //         });
    //     }
    // };

    // // Add ingredient to recipe
    // $scope.addIngredientToRecipe = function() {
    //     if ($scope.newIngredient.ingredient_id && $scope.newIngredient.quantity && $scope.newIngredient.unit) {
    //         if (!$scope.currentRecipe.ingredients) {
    //             $scope.currentRecipe.ingredients = [];
    //         }
            
    //         // Find ingredient name
    //         var ingredient = $scope.ingredients.find(function(ing) {
    //             return ing._id === $scope.newIngredient.ingredient_id;
    //         });
            
    //         $scope.currentRecipe.ingredients.push({
    //             ingredient_id: $scope.newIngredient.ingredient_id,
    //             ingredient_name: ingredient ? ingredient.name : '',
    //             quantity: $scope.newIngredient.quantity,
    //             unit: $scope.newIngredient.unit
    //         });
            
    //         $scope.newIngredient = {};
    //     }
    // };

    // // Remove ingredient from recipe
    // $scope.removeIngredientFromRecipe = function(index) {
    //     $scope.currentRecipe.ingredients.splice(index, 1);
    // };

    // // Add tag
    // $scope.addTag = function() {
    //     if ($scope.newTag && $scope.newTag.trim()) {
    //         if (!$scope.currentRecipe.tags) {
    //             $scope.currentRecipe.tags = [];
    //         }
    //         if ($scope.currentRecipe.tags.indexOf($scope.newTag.trim()) === -1) {
    //             $scope.currentRecipe.tags.push($scope.newTag.trim());
    //         }
    //         $scope.newTag = '';
    //     }
    // };

    // // Remove tag
    // $scope.removeTag = function(tag) {
    //     var index = $scope.currentRecipe.tags.indexOf(tag);
    //     if (index > -1) {
    //         $scope.currentRecipe.tags.splice(index, 1);
    //     }
    // };

    // Get ingredient name by ID
    $scope.getIngredientName = function(ingredientId) {
        var ingredient = $scope.ingredients.find(function(ing) {
            return ing.id === ingredientId;
        });
        return ingredient ? ingredient.name : 'Unknown';
    };

    // Get image URL
    $scope.getImageUrl = function(filename) {
        return API_URL + '/uploads/' + filename;
    };

    // Show recipe details in modal
    $scope.showRecipeDetails = function(recipe) {
        $scope.selectedRecipe = recipe;
        var modalElement = document.getElementById('recipeDetailsModal');
        if (modalElement) {
            var modal = new bootstrap.Modal(modalElement);
            modal.show();
        }
    };

    // // Reset form
    // $scope.resetForm = function() {
    //     $scope.currentRecipe = {
    //         ingredients: [],
    //         tags: [],
    //         images: [],
    //         removed_images: []
    //     };
    //     $scope.isEditing = false;
    //     $scope.newTag = '';
    //     $scope.newIngredient = {};
    // };

    // Initialize
    // $scope.resetForm();
    $scope.loadRecipes();
    $scope.loadIngredients();
}]);
