app.controller('IngredientsController', ['$scope', 'ApiService', 'API_URL', function($scope, ApiService, API_URL) {
    $scope.ingredients = [];
    $scope.currentIngredient = {};
    $scope.isEditing = false;
    $scope.searchQuery = '';
    $scope.tagSearch = '';
    $scope.newTag = '';
    $scope.apiUrl = API_URL;

    // Load all ingredients
    $scope.loadIngredients = function() {
        ApiService.getIngredients($scope.searchQuery, $scope.tagSearch).then(function(response) {
            $scope.ingredients = response.data;
        }, function(error) {
            console.error('Error loading ingredients:', error);
            alert('Error loading ingredients. Make sure the backend is running.');
        });
    };

    // Search ingredients
    $scope.search = function() {
        $scope.loadIngredients();
    };

    // // Create or update ingredient
    // $scope.saveIngredient = function() {
    //     if (!$scope.currentIngredient.name) {
    //         alert('Please enter an ingredient name');
    //         return;
    //     }

    //     if ($scope.isEditing) {
    //         ApiService.updateIngredient($scope.currentIngredient._id, $scope.currentIngredient).then(function(response) {
    //             $scope.loadIngredients();
    //             $scope.resetForm();
    //         }, function(error) {
    //             console.error('Error updating ingredient:', error);
    //             alert('Error updating ingredient');
    //         });
    //     } else {
    //         ApiService.createIngredient($scope.currentIngredient).then(function(response) {
    //             $scope.loadIngredients();
    //             $scope.resetForm();
    //         }, function(error) {
    //             console.error('Error creating ingredient:', error);
    //             alert('Error creating ingredient');
    //         });
    //     }
    // };

    // // Edit ingredient
    // $scope.editIngredient = function(ingredient) {
    //     $scope.currentIngredient = angular.copy(ingredient);
    //     $scope.isEditing = true;
    //     window.scrollTo(0, 0);
    // };

    // // Delete ingredient
    // $scope.deleteIngredient = function(id) {
    //     if (confirm('Are you sure you want to delete this ingredient?')) {
    //         ApiService.deleteIngredient(id).then(function(response) {
    //             $scope.loadIngredients();
    //         }, function(error) {
    //             console.error('Error deleting ingredient:', error);
    //             alert('Error deleting ingredient');
    //         });
    //     }
    // };

    // // Add tag
    // $scope.addTag = function() {
    //     if ($scope.newTag && $scope.newTag.trim()) {
    //         if (!$scope.currentIngredient.tags) {
    //             $scope.currentIngredient.tags = [];
    //         }
    //         if ($scope.currentIngredient.tags.indexOf($scope.newTag.trim()) === -1) {
    //             $scope.currentIngredient.tags.push($scope.newTag.trim());
    //         }
    //         $scope.newTag = '';
    //     }
    // };

    // // Remove tag
    // $scope.removeTag = function(tag) {
    //     var index = $scope.currentIngredient.tags.indexOf(tag);
    //     if (index > -1) {
    //         $scope.currentIngredient.tags.splice(index, 1);
    //     }
    // };

    // Get image URL
    $scope.getImageUrl = function(filename) {
        return API_URL + '/uploads/' + filename;
    };

    // // Reset form
    // $scope.resetForm = function() {
    //     $scope.currentIngredient = {
    //         tags: [],
    //         images: [],
    //         removed_images: []
    //     };
    //     $scope.isEditing = false;
    //     $scope.newTag = '';
    // };

    // Initialize
    // $scope.resetForm();
    $scope.loadIngredients();
}]);
