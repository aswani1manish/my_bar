var app = angular.module('neighborhoodSipsApp', ['ngRoute']);

// API Configuration
app.constant('API_URL', 'http://localhost:5000/api');

// Route Configuration
app.config(['$routeProvider', function($routeProvider) {
    $routeProvider
        .when('/', {
            templateUrl: 'views/home.html',
            controller: 'MainController'
        })
        .when('/ingredients', {
            templateUrl: 'views/ingredients.html',
            controller: 'IngredientsController'
        })
        .when('/recipes', {
            templateUrl: 'views/recipes.html',
            controller: 'RecipesController'
        })
        .when('/collections', {
            templateUrl: 'views/collections.html',
            controller: 'CollectionsController'
        })
        .otherwise({
            redirectTo: '/'
        });
}]);
