app.controller('CollectionsController', ['$scope', 'ApiService', 'API_URL', function($scope, ApiService, API_URL) {
    $scope.collections = [];
    $scope.recipes = [];
    $scope.currentCollection = {};
    $scope.isEditing = false;
    $scope.searchQuery = '';
    $scope.tagSearch = '';
    $scope.newTag = '';
    $scope.selectedRecipes = {};
    $scope.apiUrl = API_URL;

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
        console.log(recipeId);
        var ingr_names = recipe.ingredients.map(ingr => ingr.name).join(',');
        console.log(ingr_names);
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
