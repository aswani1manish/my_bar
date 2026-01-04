app.controller('RecipesController', ['$scope', 'ApiService', 'API_URL', function($scope, ApiService, API_URL) {
    $scope.recipes = [];
    $scope.allRecipes = [];
    $scope.ingredients = [];
    $scope.collections = [];
    $scope.currentRecipe = {};
    $scope.isEditing = false;
    $scope.searchQuery = '';
    $scope.tagSearch = '';
    $scope.selectedCollection = '4';
    $scope.barShelfMode = false;
    $scope.newTag = '';
    $scope.newIngredient = {};
    $scope.apiUrl = API_URL;
    $scope.selectedRecipe = {};
    $scope.recipeModal = null;
    $scope.uniqueTags = [];
    $scope.selectedTags = [];
    $scope.tagSelection = {};
    $scope.showTagDropdown = false;

    // Load all recipes
    $scope.loadRecipes = function() {
        
        // Load collections first, then recipes.
        $scope.loadCollections();
        var barShelfModeParam = $scope.barShelfMode ? 'Y' : '';
        // Note: tagSearch is kept empty since we now use client-side tag filtering
        ApiService.getRecipes($scope.searchQuery, '', barShelfModeParam).then(function(response) {
            $scope.allRecipes = response.data;
            $scope.extractUniqueTags();
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
        var filteredByCollection = [];
        
        if (!$scope.selectedCollection) {
            // Show all recipes when no collection is selected
            filteredByCollection = $scope.allRecipes;
        } else {
            // Find the selected collection
            var collection = $scope.collections.find(function(c) {
                return c.id === parseInt($scope.selectedCollection);
            });
            
            if (collection && collection.recipe_ids) {
                // Filter recipes to only those in the collection
                filteredByCollection = $scope.allRecipes.filter(function(recipe) {
                    return collection.recipe_ids.indexOf(recipe.id) !== -1;
                });
            } else {
                filteredByCollection = [];
            }
        }
        
        // Apply tag filter
        if ($scope.selectedTags.length > 0) {
            $scope.recipes = filteredByCollection.filter(function(recipe) {
                if (!recipe.tags || recipe.tags.length === 0) {
                    return false;
                }
                // Check if recipe has at least one of the selected tags
                return $scope.selectedTags.some(function(selectedTag) {
                    return recipe.tags.indexOf(selectedTag) !== -1;
                });
            });
        } else {
            $scope.recipes = filteredByCollection;
        }
    };

    // Search recipes
    $scope.search = function() {
        $scope.loadRecipes();
    };

    // Toggle bar shelf mode
    $scope.toggleBarShelfMode = function() {
        $scope.loadRecipes();
    };

    // Extract unique tags from all recipes
    $scope.extractUniqueTags = function() {
        var tagsSet = new Set();
        $scope.allRecipes.forEach(function(recipe) {
            if (recipe.tags && recipe.tags.length > 0) {
                recipe.tags.forEach(function(tag) {
                    tagsSet.add(tag);
                });
            }
        });
        $scope.uniqueTags = Array.from(tagsSet).sort();
    };

    // Toggle tag dropdown visibility
    $scope.toggleTagDropdown = function(event) {
        event.stopPropagation();
        $scope.showTagDropdown = !$scope.showTagDropdown;
    };

    // Update selected tags when checkboxes change
    $scope.updateSelectedTags = function() {
        $scope.selectedTags = Object.keys($scope.tagSelection).filter(function(tag) {
            return $scope.tagSelection[tag];
        });
        $scope.filterRecipesByCollection();
    };

    // Close dropdown when clicking outside
    var closeDropdownHandler = function(event) {
        if ($scope.showTagDropdown) {
            $scope.$apply(function() {
                $scope.showTagDropdown = false;
            });
        }
    };
    
    angular.element(document).on('click', closeDropdownHandler);
    
    // Clean up event listener when scope is destroyed
    $scope.$on('$destroy', function() {
        angular.element(document).off('click', closeDropdownHandler);
    });

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

    // Get ingredient names in recipe
    $scope.getIngredientNamesForRecipe = function(recipe) {
        var names = recipe.ingredients.map(ingr => ingr.name);
        return names.join(', ');
    };
    
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
            if (!$scope.recipeModal) {
                $scope.recipeModal = new bootstrap.Modal(modalElement);
            }
            $scope.recipeModal.show();
        }
    };

    // Truncate text to specified word limit
    $scope.truncateText = function(text, wordLimit) {
        if (!text) return '';
        var words = text.split(' ');
        if (words.length <= wordLimit) {
            return text;
        }
        return words.slice(0, wordLimit).join(' ');
    };

    // Check if text needs truncation
    $scope.needsTruncation = function(text, wordLimit) {
        if (!text) return false;
        var words = text.split(' ');
        return words.length > wordLimit;
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
