app.controller('RecipesController', ['$scope', 'ApiService', 'API_URL', function($scope, ApiService, API_URL) {
    $scope.recipes = [];
    $scope.allRecipes = [];
    $scope.ingredients = [];
    $scope.collections = [];
    $scope.currentRecipe = {};
    $scope.isEditing = false;
    $scope.searchQuery = '';
    $scope.tagSearchQuery = '';
    $scope.selectedCollection = '';
    $scope.barShelfMode = false;
    $scope.selectedSpirit = '';
    $scope.selectedTag = '';
    $scope.newTag = '';
    $scope.newIngredient = {};
    $scope.apiUrl = API_URL;
    $scope.selectedRecipe = {};
    $scope.recipeModal = null;

    // Load all recipes
    $scope.loadRecipes = function() {
        
        // Load collections first, then recipes.
        $scope.loadCollections();
        var barShelfModeParam = $scope.barShelfMode ? 'Y' : '';
        $scope.recipesLoading = true;
        ApiService.getRecipes($scope.searchQuery, $scope.tagSearchQuery, barShelfModeParam).then(function(response) {
            $scope.allRecipes = response.data;
            $scope.filterRecipesByCollection();
            $scope.recipesLoading = false;
            // Check for deep link after recipes are loaded
            $scope.checkUrlForRecipeId();
        }, function(error) {
            console.error('Error loading recipes:', error);
            $scope.recipesLoading = false;
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
        var filteredRecipes = $scope.allRecipes;
        
        // Apply collection filter if selected
        if ($scope.selectedCollection) {
            // Find the selected collection
            var collection = $scope.collections.find(function(c) {
                return c.id === parseInt($scope.selectedCollection);
            });
            
            if (collection && collection.recipe_ids) {
                // Filter recipes to only those in the collection
                filteredRecipes = filteredRecipes.filter(function(recipe) {
                    return collection.recipe_ids.indexOf(recipe.id) !== -1;
                });
            } else {
                filteredRecipes = [];
            }
        }
        
        // Apply spirit filter if selected
        if ($scope.selectedSpirit) {
            filteredRecipes = filteredRecipes.filter(function(recipe) {
                if (recipe.ingredients && recipe.ingredients.length > 0) {
                    return recipe.ingredients.some(function(ingredient) {
                        if (!ingredient.name) return false;
                        var ingredientNameLower = ingredient.name.toLowerCase();
                        var spiritLower = $scope.selectedSpirit.toLowerCase();
                        // Check for word boundary match to avoid false positives like 'Gin' matching 'Ginger'
                        var regex = new RegExp('\\b' + spiritLower + '\\b', 'i');
                        return regex.test(ingredient.name);
                    });
                }
                return false;
            });
        }

        // Apply tag filter if selected
        if ($scope.selectedTag) {
            filteredRecipes = filteredRecipes.filter(function(recipe) {
                if (recipe.tags && recipe.tags.length > 0) {
                    return recipe.tags.some(function(tag) {
                        return tag.toLowerCase() === $scope.selectedTag.toLowerCase();
                    });
                }
                return false;
            });
        }
        
        $scope.recipes = filteredRecipes;
    };

    // Filter recipes by spirit
    $scope.filterBySpirit = function(spirit) {
        // Toggle spirit selection
        if ($scope.selectedSpirit === spirit) {
            $scope.selectedSpirit = '';
        } else {
            $scope.selectedSpirit = spirit;
        }
        $scope.filterRecipesByCollection();
    };

    // Filter recipes by tag
    $scope.filterByTag = function(tag) {
        // Toggle tag selection
        if ($scope.selectedTag === tag) {
            $scope.selectedTag = '';
        } else {
            $scope.selectedTag = tag;
        }
        $scope.filterRecipesByCollection();
    };

    // Search recipes
    $scope.search = function() {
        $scope.loadRecipes();
    };

    // Toggle bar shelf mode
    $scope.toggleBarShelfMode = function() {
        $scope.loadRecipes();
    };

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
            // Update URL with recipe ID without reloading the page
            if (recipe && recipe.id) {
                window.history.pushState({recipeId: recipe.id}, '', '?recipe=' + recipe.id);
            }
        }
    };

    // Check for recipe ID in URL on page load and auto-open modal
    $scope.checkUrlForRecipeId = function() {
        var urlParams = new URLSearchParams(window.location.search);
        var recipeId = urlParams.get('recipe');
        
        if (recipeId && $scope.allRecipes && $scope.allRecipes.length > 0) {
            // Find the recipe by ID
            var recipe = $scope.allRecipes.find(function(r) {
                return r.id === parseInt(recipeId);
            });
            if (recipe) {
                // Open the modal after a short delay to ensure DOM is ready
                setTimeout(function() {
                    $scope.$apply(function() {
                        $scope.showRecipeDetails(recipe);
                    });
                }, 500);
            } else {
                console.warn('Recipe with ID', recipeId, 'not found');
            }
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


    $scope.loadRecipes();
    $scope.loadIngredients();

    // Handle modal close - clean up URL
    angular.element(document).ready(function() {
        var modalElement = document.getElementById('recipeDetailsModal');
        if (modalElement) {
            // Before modal hides, blur any focused element to prevent aria-hidden warning
            modalElement.addEventListener('hide.bs.modal', function() {
                // Remove focus from any element inside the modal
                var focusedElement = document.activeElement;
                if (focusedElement && modalElement.contains(focusedElement)) {
                    focusedElement.blur();
                }
            });
            
            modalElement.addEventListener('hidden.bs.modal', function() {
                // Remove recipe parameter from URL when modal is closed
                var url = window.location.origin + window.location.pathname;
                window.history.pushState({}, '', url);
            });
        }
    });

    // Handle browser back/forward button
    window.addEventListener('popstate', function(event) {
        if (event.state && event.state.recipeId) {
            // Find and show the recipe
            var recipe = $scope.allRecipes.find(function(r) {
                return r.id === event.state.recipeId;
            });
            if (recipe) {
                $scope.$apply(function() {
                    $scope.showRecipeDetails(recipe);
                });
            }
        } else {
            // Close modal if going back to page without recipe ID
            if ($scope.recipeModal) {
                $scope.recipeModal.hide();
            }
        }
    });
}]);
