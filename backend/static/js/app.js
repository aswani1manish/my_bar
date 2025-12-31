var app = angular.module('neighborhoodSipsApp', ['ngRoute']);

// API Configuration
// Use APP_CONFIG from config.js if available, otherwise default to localhost
app.constant('API_URL', (typeof APP_CONFIG !== 'undefined' && APP_CONFIG.apiUrl) 
    ? APP_CONFIG.apiUrl 
    : 'http://localhost:5000/api');

// Route Configuration
app.config(['$routeProvider', function($routeProvider) {
    $routeProvider
        .when('/', {
            templateUrl: 'views/home.html',
            controller: 'MainController'
        })
        .when('/recipes', {
            templateUrl: 'views/recipes.html',
            controller: 'RecipesController'
        })
        .otherwise({
            redirectTo: '/'
        });
}]);
