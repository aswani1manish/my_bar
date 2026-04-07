app.controller('ViewCollectionController', ['$scope', 'ApiService', 'API_URL', function($scope, ApiService, API_URL) {
    var BASE_SPIRITS = ['Gin', 'Vodka', 'Tequila', 'Rum', 'Bourbon', 'Whiskey', 'Mezcal'];

    $scope.collections = [];
    $scope.allRecipes = [];
    $scope.recipes = [];
    $scope.selectedCollectionId = 'all';
    $scope.selectedCollection = {};
    $scope.selectedRecipe = {};
    $scope.recipeModal = null;
    $scope.savedScrollPosition = undefined;

    // Load all recipes and collections, then apply any deep-link selection
    $scope.load = function() {
        ApiService.getRecipes('', '').then(function(response) {
            $scope.allRecipes = response.data;
            ApiService.getCollections('', '').then(function(colResp) {
                $scope.collections = colResp.data;
                $scope.checkUrlForCollectionId();
                $scope.applyCollectionFilter();
            }, function(error) {
                console.error('Error loading collections:', error);
            });
        }, function(error) {
            console.error('Error loading recipes:', error);
        });
    };

    // Filter the displayed recipes based on the selected collection
    $scope.applyCollectionFilter = function() {
        if ($scope.selectedCollectionId === 'all') {
            $scope.selectedCollection = {};
            $scope.recipes = $scope.allRecipes.slice();
            return;
        }

        var collection = $scope.collections.find(function(c) {
            return c.id === $scope.selectedCollectionId;
        });
        $scope.selectedCollection = collection || {};

        if (!collection || !collection.recipe_ids || collection.recipe_ids.length === 0) {
            $scope.recipes = [];
            return;
        }

        $scope.recipes = $scope.allRecipes.filter(function(recipe) {
            return collection.recipe_ids.indexOf(recipe.id) !== -1;
        });
    };

    // Called when user changes the collection dropdown
    $scope.onCollectionChange = function() {
        // Update the URL so the current selection is shareable
        var params = new URLSearchParams(window.location.search);
        if ($scope.selectedCollectionId && $scope.selectedCollectionId !== 'all') {
            params.set('id', $scope.selectedCollectionId);
        } else {
            params.delete('id');
        }
        var newSearch = params.toString() ? '?' + params.toString() : window.location.pathname;
        window.history.replaceState(null, '', newSearch || window.location.pathname);
        $scope.applyCollectionFilter();
    };

    // Check URL for ?id= deep-link parameter and pre-select that collection
    $scope.checkUrlForCollectionId = function() {
        var urlParams = new URLSearchParams(window.location.search);
        var collectionId = urlParams.get('id');
        if (collectionId) {
            $scope.selectedCollectionId = parseInt(collectionId);
        } else {
            $scope.selectedCollectionId = 'all';
        }
    };

    // Get ingredient names for a recipe, base spirits listed first
    $scope.getIngredientNamesForRecipe = function(recipe) {
        if (!recipe || !recipe.ingredients || recipe.ingredients.length === 0) return '';
        var sorted = recipe.ingredients.slice().sort(function(a, b) {
            var aIsSpirit = BASE_SPIRITS.indexOf(a.name) !== -1;
            var bIsSpirit = BASE_SPIRITS.indexOf(b.name) !== -1;
            if (aIsSpirit && !bIsSpirit) { return -1; }
            if (!aIsSpirit && bIsSpirit) { return 1; }
            return 0;
        });
        return sorted.map(function(ingr) { return ingr.name; }).join(', ');
    };

    // Get image URL
    $scope.getImageUrl = function(filename) {
        return API_URL + '/uploads/' + filename;
    };

    // Show recipe details in modal
    $scope.showRecipeDetails = function(recipe) {
        $scope.selectedRecipe = recipe;
        var modalElement = document.getElementById('vcRecipeDetailsModal');
        if (modalElement) {
            if (!$scope.recipeModal) {
                $scope.recipeModal = new bootstrap.Modal(modalElement);
            }
            $scope.savedScrollPosition = window.pageYOffset || document.documentElement.scrollTop;
            $scope.recipeModal.show();
        }
    };

    // Initialize
    $scope.load();

    angular.element(document).ready(function() {
        var modalElement = document.getElementById('vcRecipeDetailsModal');
        if (modalElement) {
            modalElement.addEventListener('hide.bs.modal', function() {
                var focusedElement = document.activeElement;
                if (focusedElement && modalElement.contains(focusedElement)) {
                    focusedElement.blur();
                }
            });

            modalElement.addEventListener('hidden.bs.modal', function() {
                if ($scope.savedScrollPosition !== undefined) {
                    window.scrollTo(0, $scope.savedScrollPosition);
                    delete $scope.savedScrollPosition;
                }
            });
        }
    });
}]);
