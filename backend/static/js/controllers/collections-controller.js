app.controller('CollectionsController', ['$scope', '$timeout', 'ApiService', 'API_URL', function($scope, $timeout, ApiService, API_URL) {
    $scope.collections = [];
    $scope.recipes = [];
    $scope.currentCollection = {};
    $scope.isEditing = false;
    $scope.searchQuery = '';
    $scope.tagSearch = '';
    $scope.newTag = '';
    $scope.selectedRecipes = {};
    $scope.apiUrl = API_URL;
    
    // Recipe management variables
    $scope.selectedCollectionId = '';
    $scope.recipeSearchQuery = '';
    $scope.filteredRecipes = [];
    $scope.recipeSelection = {};
    $scope.selectAll = false;
    $scope.savingCollection = false;
    $scope.saveMessage = '';
    $scope.saveError = '';

    // Load all collections
    $scope.loadCollections = function() {
        ApiService.getCollections($scope.searchQuery, $scope.tagSearch).then(function(response) {
            $scope.collections = response.data;
        }, function(error) {
            console.error('Error loading collections:', error);
            alert('Error loading collections. Make sure the backend is running.');
        });
    };

    // Load all recipes for selection
    $scope.loadRecipes = function() {
        ApiService.getRecipes('', '').then(function(response) {
            $scope.recipes = response.data;
            $scope.loadCollections();
        }, function(error) {
            console.error('Error loading recipes:', error);
        });
    };

    // Search collections
    $scope.search = function() {
        $scope.loadCollections();
    };
    
    // Handle collection selection
    $scope.onCollectionSelect = function() {
        $scope.saveMessage = '';
        $scope.saveError = '';
        $scope.recipeSearchQuery = '';
        $scope.selectAll = false;
        
        if (!$scope.selectedCollectionId) {
            $scope.filteredRecipes = [];
            $scope.recipeSelection = {};
            return;
        }
        
        // Find selected collection
        var collection = $scope.collections.find(function(c) {
            return c.id === $scope.selectedCollectionId;
        });
        
        if (!collection) {
            return;
        }
        
        // Initialize recipe selection based on collection's recipe_ids
        $scope.recipeSelection = {};
        var recipeIds = collection.recipe_ids || [];
        
        $scope.recipes.forEach(function(recipe) {
            $scope.recipeSelection[recipe.id] = recipeIds.indexOf(recipe.id) !== -1;
        });
        
        // Initialize filtered recipes
        $scope.filterRecipesInCollection();
    };
    
    // Filter recipes based on search query
    $scope.filterRecipesInCollection = function() {
        var query = ($scope.recipeCollectionSearchQuery || '').toLowerCase();
        console.log($scope.recipeCollectionSearchQuery);
        if (!query) {
            $scope.filteredRecipesInCollection = angular.copy($scope.recipes);
        } else {
            $scope.filteredRecipesInCollection = $scope.recipes.filter(function(recipe) {
                // Search by ID
                if (recipe.id.toString().indexOf(query) !== -1) {
                    return true;
                }
                
                // Search by name
                if (recipe.name && recipe.name.toLowerCase().indexOf(query) !== -1) {
                    return true;
                }
                
                // Search by ingredients
                var ingredientsList = $scope.getIngredientsList(recipe).toLowerCase();
                if (ingredientsList.indexOf(query) !== -1) {
                    return true;
                }
                
                return false;
            });
        }
        
        // Sort filtered recipes: recipes in collection first, then others
        $scope.filteredRecipesInCollection.sort(function(a, b) {
            var aInCollection = ($scope.recipeSelection && $scope.recipeSelection[a.id]) ? 1 : 0;
            var bInCollection = ($scope.recipeSelection && $scope.recipeSelection[b.id]) ? 1 : 0;
            
            // Sort descending by collection membership (in collection = 1, not in = 0)
            // This puts recipes with 1 (in collection) before those with 0 (not in)
            return bInCollection - aInCollection;
        });
    };
    
    // Get ingredients list as comma-separated string
    $scope.getIngredientsList = function(recipe) {
        if (!recipe || !recipe.ingredients || recipe.ingredients.length === 0) {
            return 'No ingredients';
        }
        
        return recipe.ingredients.map(function(ing) {
            return ing.name;
        }).join(', ');
    };
    
    // Toggle all recipes selection
    $scope.toggleAllRecipes = function() {
        $scope.filteredRecipes.forEach(function(recipe) {
            $scope.recipeSelection[recipe.id] = $scope.selectAll;
        });
    };
    
    // Save collection recipes
    $scope.saveCollectionRecipes = function() {
        if (!$scope.selectedCollectionId) {
            return;
        }
        
        $scope.savingCollection = true;
        $scope.saveMessage = '';
        $scope.saveError = '';
        
        // Get selected recipe IDs
        var selectedRecipeIds = [];
        Object.keys($scope.recipeSelection).forEach(function(recipeId) {
            if ($scope.recipeSelection[recipeId]) {
                selectedRecipeIds.push(parseInt(recipeId));
            }
        });
        
        // Find the collection
        var collection = $scope.collections.find(function(c) {
            return c.id === $scope.selectedCollectionId;
        });
        
        if (!collection) {
            $scope.saveError = 'Collection not found';
            $scope.savingCollection = false;
            return;
        }
        
        // Prepare update data
        var updateData = {
            name: collection.name,
            description: collection.description,
            recipe_ids: selectedRecipeIds,
            tags: collection.tags || [],
            images: collection.images || []
        };
        
        // Update collection
        ApiService.updateCollection($scope.selectedCollectionId, updateData).then(function(response) {
            $scope.savingCollection = false;
            $scope.saveMessage = 'Collection updated successfully!';
            
            // Reload collections to reflect changes
            $scope.loadCollections();
            
            // Clear message after 3 seconds
            $timeout(function() {
                $scope.saveMessage = '';
            }, 3000);
        }, function(error) {
            $scope.savingCollection = false;
            $scope.saveError = 'Error updating collection: ' + (error.data?.error || 'Unknown error');
            console.error('Error updating collection:', error);
        });
    };

    // // Create or update collection
    // $scope.saveCollection = function() {
    //     if (!$scope.currentCollection.name) {
    //         alert('Please enter a collection name');
    //         return;
    //     }

    //     // Get selected recipe IDs
    //     $scope.currentCollection.recipe_ids = Object.keys($scope.selectedRecipes)
    //         .filter(function(key) { return $scope.selectedRecipes[key]; });

    //     if ($scope.isEditing) {
    //         ApiService.updateCollection($scope.currentCollection._id, $scope.currentCollection).then(function(response) {
    //             $scope.loadCollections();
    //             $scope.resetForm();
    //         }, function(error) {
    //             console.error('Error updating collection:', error);
    //             alert('Error updating collection');
    //         });
    //     } else {
    //         ApiService.createCollection($scope.currentCollection).then(function(response) {
    //             $scope.loadCollections();
    //             $scope.resetForm();
    //         }, function(error) {
    //             console.error('Error creating collection:', error);
    //             alert('Error creating collection');
    //         });
    //     }
    // };

    // // Edit collection
    // $scope.editCollection = function(collection) {
    //     $scope.currentCollection = angular.copy(collection);
    //     $scope.isEditing = true;
        
    //     // Set selected recipes
    //     $scope.selectedRecipes = {};
    //     if ($scope.currentCollection.recipe_ids) {
    //         $scope.currentCollection.recipe_ids.forEach(function(id) {
    //             $scope.selectedRecipes[id] = true;
    //         });
    //     }
        
    //     window.scrollTo(0, 0);
    // };

    // // Delete collection
    // $scope.deleteCollection = function(id) {
    //     if (confirm('Are you sure you want to delete this collection?')) {
    //         ApiService.deleteCollection(id).then(function(response) {
    //             $scope.loadCollections();
    //         }, function(error) {
    //             console.error('Error deleting collection:', error);
    //             alert('Error deleting collection');
    //         });
    //     }
    // };

    // // Add tag
    // $scope.addTag = function() {
    //     if ($scope.newTag && $scope.newTag.trim()) {
    //         if (!$scope.currentCollection.tags) {
    //             $scope.currentCollection.tags = [];
    //         }
    //         if ($scope.currentCollection.tags.indexOf($scope.newTag.trim()) === -1) {
    //             $scope.currentCollection.tags.push($scope.newTag.trim());
    //         }
    //         $scope.newTag = '';
    //     }
    // };

    // // Remove tag
    // $scope.removeTag = function(tag) {
    //     var index = $scope.currentCollection.tags.indexOf(tag);
    //     if (index > -1) {
    //         $scope.currentCollection.tags.splice(index, 1);
    //     }
    // };

    // Get recipe names in collection
    $scope.getRecipeNames = function(recipeIds) {
        if (!recipeIds || recipeIds.length === 0) return 'No recipes';
        
        var names = recipeIds.map(function(id) {
            var recipe = $scope.recipes.find(function(r) { return r.id === id; });
            return recipe ? recipe.name : 'Unknown';
        });
        
        return names.join(', ');
    };

    // Get recipe name based on ID
    $scope.getRecipeName = function(recipeId) {
        
        var recipe = $scope.recipes.find(function(r) { return r.id === recipeId; });
        return recipe ? recipe.name : 'Unknown';
    };

    $scope.getIngredientNamesForRecipeId = function(recipeId) {
        
        var recipe = $scope.recipes.find(function(r) { return r.id === recipeId; });
        var ingr_names = recipe.ingredients.map(ingr => ingr.name).join(', ');
        return ingr_names;
    };


    // Get image URL
    $scope.getImageUrl = function(filename) {
        return API_URL + '/uploads/' + filename;
    };

    // // Reset form
    // $scope.resetForm = function() {
    //     $scope.currentCollection = {
    //         recipe_ids: [],
    //         tags: [],
    //         images: [],
    //         removed_images: []
    //     };
    //     $scope.isEditing = false;
    //     $scope.newTag = '';
    //     $scope.selectedRecipes = {};
    // };

    // Initialize
    // $scope.resetForm();
    $scope.loadRecipes();
    //Need to call this inside load recipes to ensure that recipes are loaded first, before collections. Hence commented out.
    //$scope.loadCollections(); 
}]);
