app.controller('CollectionsController', ['$scope', '$timeout', 'ApiService', 'API_URL', function($scope, $timeout, ApiService, API_URL) {
    // Debug flag - Controls console logging for search functionality
    // Set to true to enable debug logs (useful for troubleshooting search issues)
    // Set to false in production to prevent console spam
    // NOTE: Currently set to true as requested in issue to help debug search input boxes
    var DEBUG_SEARCH = true;
    
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
    $scope.searchInCollection = '';
    $scope.searchNotInCollection = '';
    $scope.filteredRecipesInCollection = [];
    $scope.filteredRecipesNotInCollection = [];
    $scope.recipeSelection = {};
    $scope.savingCollection = false;
    $scope.saveMessage = '';
    $scope.saveError = '';
    $scope.saveTimeout = null; // For debouncing auto-save
    $scope.pendingSave = false; // Flag to track if save is needed after current save completes
    $scope.selectedCollection = {};
    $scope.collectionModal = null;

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
        if (DEBUG_SEARCH) console.log('[onCollectionSelect] Selected collection ID:', $scope.selectedCollectionId);
        $scope.saveMessage = '';
        $scope.saveError = '';
        $scope.searchInCollection = '';
        $scope.searchNotInCollection = '';
        
        if (!$scope.selectedCollectionId) {
            $scope.filteredRecipesInCollection = [];
            $scope.filteredRecipesNotInCollection = [];
            $scope.recipeSelection = {};
            return;
        }
        
        // Find selected collection
        var collection = $scope.collections.find(function(c) {
            return c.id === $scope.selectedCollectionId;
        });
        
        if (!collection) {
            if (DEBUG_SEARCH) console.log('[onCollectionSelect] Collection not found');
            return;
        }
        
        if (DEBUG_SEARCH) console.log('[onCollectionSelect] Collection found:', collection.name, 'with', collection.recipe_ids.length, 'recipes');
        
        // Initialize recipe selection based on collection's recipe_ids
        $scope.recipeSelection = {};
        var recipeIds = collection.recipe_ids || [];
        
        $scope.recipes.forEach(function(recipe) {
            $scope.recipeSelection[recipe.id] = recipeIds.indexOf(recipe.id) !== -1;
        });
        
        if (DEBUG_SEARCH) console.log('[onCollectionSelect] Recipe selection initialized, total recipes:', $scope.recipes.length);
        
        // Initialize filtered recipes
        $scope.filterRecipesInCollection();
        $scope.filterRecipesNotInCollection();
    };
    
    // Helper function to check if recipe matches search query
    $scope.recipeMatchesQuery = function(recipe, query) {
        if (!query) return true;
        
        if (DEBUG_SEARCH) console.log('[recipeMatchesQuery] Checking recipe:', recipe.id, recipe.name, 'against query:', query);
        
        // Search by ID
        if (recipe.id.toString().indexOf(query) !== -1) {
            if (DEBUG_SEARCH) console.log('[recipeMatchesQuery] Matched by ID');
            return true;
        }
        
        // Search by name
        if (recipe.name && recipe.name.toLowerCase().indexOf(query) !== -1) {
            if (DEBUG_SEARCH) console.log('[recipeMatchesQuery] Matched by name');
            return true;
        }
        
        // Search by ingredients
        var ingredientsList = $scope.getIngredientsList(recipe).toLowerCase();
        if (ingredientsList.indexOf(query) !== -1) {
            if (DEBUG_SEARCH) console.log('[recipeMatchesQuery] Matched by ingredients');
            return true;
        }
        
        if (DEBUG_SEARCH) console.log('[recipeMatchesQuery] No match found');
        return false;
    };
    
    // Filter recipes IN the collection based on search query
    // Accepts optional searchQuery parameter, otherwise uses $scope.searchInCollection
    $scope.filterRecipesInCollection = function(searchQuery) {
        // Use parameter if provided, otherwise use scope variable
        var query = (searchQuery !== undefined ? searchQuery : $scope.searchInCollection || '').toLowerCase();
        if (DEBUG_SEARCH) {
            console.log('[filterRecipesInCollection] Called with parameter:', searchQuery);
            console.log('[filterRecipesInCollection] Using search query:', query);
            console.log('[filterRecipesInCollection] $scope.searchInCollection value:', $scope.searchInCollection);
        }
        
        // Get all recipes that are in the collection
        var recipesInCollection = $scope.recipes.filter(function(recipe) {
            return $scope.recipeSelection[recipe.id] === true;
        });
        if (DEBUG_SEARCH) console.log('[filterRecipesInCollection] Recipes in collection (before filter):', recipesInCollection.length);
        
        if (!query) {
            $scope.filteredRecipesInCollection = recipesInCollection;
        } else {
            $scope.filteredRecipesInCollection = recipesInCollection.filter(function(recipe) {
                return $scope.recipeMatchesQuery(recipe, query);
            });
        }
        if (DEBUG_SEARCH) console.log('[filterRecipesInCollection] Filtered recipes count:', $scope.filteredRecipesInCollection.length);
    };
    
    // Filter recipes NOT in the collection based on search query
    // Accepts optional searchQuery parameter, otherwise uses $scope.searchNotInCollection
    $scope.filterRecipesNotInCollection = function(searchQuery) {
        // Use parameter if provided, otherwise use scope variable
        var query = (searchQuery !== undefined ? searchQuery : $scope.searchNotInCollection || '').toLowerCase();
        if (DEBUG_SEARCH) {
            console.log('[filterRecipesNotInCollection] Called with parameter:', searchQuery);
            console.log('[filterRecipesNotInCollection] Using search query:', query);
            console.log('[filterRecipesNotInCollection] $scope.searchNotInCollection value:', $scope.searchNotInCollection);
        }
        
        // Get all recipes that are NOT in the collection
        var recipesNotInCollection = $scope.recipes.filter(function(recipe) {
            return !$scope.recipeSelection[recipe.id];
        });
        if (DEBUG_SEARCH) console.log('[filterRecipesNotInCollection] Recipes not in collection (before filter):', recipesNotInCollection.length);
        
        if (!query) {
            $scope.filteredRecipesNotInCollection = recipesNotInCollection;
        } else {
            $scope.filteredRecipesNotInCollection = recipesNotInCollection.filter(function(recipe) {
                return $scope.recipeMatchesQuery(recipe, query);
            });
        }
        if (DEBUG_SEARCH) console.log('[filterRecipesNotInCollection] Filtered recipes count:', $scope.filteredRecipesNotInCollection.length);
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
    
    // Handle checkbox change - auto-save with debounce
    $scope.onRecipeCheckboxChange = function(recipeId) {
        // Refresh the filtered lists immediately for responsive UI
        // Note: Called without parameters to use current scope search values
        // This maintains any active search filter while updating recipe membership
        $scope.filterRecipesInCollection();
        $scope.filterRecipesNotInCollection();
        
        // Debounce auto-save to handle rapid changes
        // This ensures we wait until user stops clicking before saving
        if ($scope.saveTimeout) {
            $timeout.cancel($scope.saveTimeout);
        }
        
        $scope.saveTimeout = $timeout(function() {
            // If a save is in progress, schedule another save after it completes
            if ($scope.savingCollection) {
                $scope.pendingSave = true;
            } else {
                $scope.autoSaveCollectionRecipes();
            }
        }, 500); // Wait 500ms after last change before saving
    };
    
    // Auto-save collection recipes
    $scope.autoSaveCollectionRecipes = function() {
        if (!$scope.selectedCollectionId) {
            return;
        }
        
        // If already saving, mark that we need another save
        if ($scope.savingCollection) {
            $scope.pendingSave = true;
            return;
        }
        
        $scope.savingCollection = true;
        $scope.pendingSave = false;
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
            $scope.saveMessage = 'Changes saved automatically';
            
            // Update the local collection data instead of reloading all collections
            collection.recipe_ids = selectedRecipeIds;
            
            // If there's a pending save, trigger it after a short delay
            // The delay allows the UI to update and prevents rapid consecutive API calls
            if ($scope.pendingSave) {
                $scope.pendingSave = false;
                $timeout(function() {
                    $scope.autoSaveCollectionRecipes();
                }, 100); // 100ms delay to ensure UI stability
            }
            
            // Clear message after 2 seconds
            $timeout(function() {
                $scope.saveMessage = '';
            }, 2000);
        }, function(error) {
            $scope.savingCollection = false;
            $scope.saveError = 'Error saving: ' + (error.data && error.data.error || 'Unknown error');
            console.error('Error updating collection:', error);
            
            // Clear error after 3 seconds
            $timeout(function() {
                $scope.saveError = '';
            }, 3000);
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

    // Show collection details in modal
    $scope.showCollectionDetails = function(collection) {
        $scope.selectedCollection = collection;
        var modalElement = document.getElementById('collectionDetailsModal');
        if (modalElement) {
            if (!$scope.collectionModal) {
                $scope.collectionModal = new bootstrap.Modal(modalElement);
            }
            $scope.collectionModal.show();
        }
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
    
    // Handle modal close - prevent aria-hidden warning
    angular.element(document).ready(function() {
        var modalElement = document.getElementById('collectionDetailsModal');
        if (modalElement) {
            // Before modal hides, blur any focused element to prevent aria-hidden warning
            modalElement.addEventListener('hide.bs.modal', function() {
                // Remove focus from any element inside the modal
                var focusedElement = document.activeElement;
                if (focusedElement && modalElement.contains(focusedElement)) {
                    focusedElement.blur();
                }
            });
        }
    });
    
    // Watch for changes in search queries
    // These watchers handle the search input changes for both search boxes
    $scope.$watch('searchInCollection', function(newVal, oldVal) {
        if (newVal !== oldVal && $scope.selectedCollectionId) {
            if (DEBUG_SEARCH) {
                console.log('=== [Watch] searchInCollection changed ===');
                console.log('[Watch] Old value:', oldVal);
                console.log('[Watch] New value:', newVal);
                console.log('[Watch] Calling filterRecipesInCollection with newVal');
            }
            $scope.filterRecipesInCollection(newVal);
        }
    });
    
    $scope.$watch('searchNotInCollection', function(newVal, oldVal) {
        if (newVal !== oldVal && $scope.selectedCollectionId) {
            if (DEBUG_SEARCH) {
                console.log('=== [Watch] searchNotInCollection changed ===');
                console.log('[Watch] Old value:', oldVal);
                console.log('[Watch] New value:', newVal);
                console.log('[Watch] Calling filterRecipesNotInCollection with newVal');
            }
            $scope.filterRecipesNotInCollection(newVal);
        }
    });
}]);
