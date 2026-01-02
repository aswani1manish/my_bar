app.factory('ApiService', ['$http', 'API_URL', function($http, API_URL) {
    return {
        // Ingredients
        getIngredients: function(search, tags) {
            var params = {};
            if (search) params.search = search;
            if (tags) params.tags = tags;
            return $http.get(API_URL + '/ingredients', { params: params });
        },
        getIngredient: function(id) {
            return $http.get(API_URL + '/ingredients/' + id);
        },
        updateIngredientBarShelf: function(id, barShelfAvailability) {
            return $http.patch(API_URL + '/ingredients/' + id + '/bar-shelf', {
                bar_shelf_availability: barShelfAvailability
            });
        },
        // createIngredient: function(ingredient) {
        //     return $http.post(API_URL + '/ingredients', ingredient);
        // },
        // updateIngredient: function(id, ingredient) {
        //     return $http.put(API_URL + '/ingredients/' + id, ingredient);
        // },
        // deleteIngredient: function(id) {
        //     return $http.delete(API_URL + '/ingredients/' + id);
        // },
        
        // Recipes
        getRecipes: function(search, tags, barShelfMode) {
            var params = {};
            if (search) params.search = search;
            if (tags) params.tags = tags;
            if (barShelfMode) params.bar_shelf_mode = barShelfMode;
            return $http.get(API_URL + '/recipes', { params: params });
        },
        getRecipe: function(id) {
            return $http.get(API_URL + '/recipes/' + id);
        },
        createRecipe: function(recipe) {
            return $http.post(API_URL + '/recipes', recipe);
        },
        updateRecipe: function(id, recipe) {
            return $http.put(API_URL + '/recipes/' + id, recipe);
        },
        deleteRecipe: function(id) {
            return $http.delete(API_URL + '/recipes/' + id);
        },
        
        // Collections
        getCollections: function(search, tags) {
            var params = {};
            if (search) params.search = search;
            if (tags) params.tags = tags;
            return $http.get(API_URL + '/collections', { params: params });
        },
        getCollection: function(id) {
            return $http.get(API_URL + '/collections/' + id);
        },
        // createCollection: function(collection) {
        //     return $http.post(API_URL + '/collections', collection);
        // },
        updateCollection: function(id, collection) {
            return $http.put(API_URL + '/collections/' + id, collection);
        }
        // deleteCollection: function(id) {
        //     return $http.delete(API_URL + '/collections/' + id);
        // }
    };
}]);
