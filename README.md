# Neighborhood Sips

A web application for managing your cocktail bar - ingredients, recipes, and collections.

**Neighborhood Sips** is your personal cocktail mixologist brand management system, built with AngularJS frontend, Python Flask backend, and MongoDB for persistent storage.

## Features

### 1. Ingredients Management
- Add, edit, and delete cocktail ingredients (e.g., gin, vodka, elderflower liqueur)
- Upload multiple images for each ingredient
- Categorize ingredients (spirits, liqueurs, mixers, etc.)
- Tag ingredients for easy filtering
- Search ingredients by name or description
- Filter ingredients by tags

### 2. Recipes Management
- Create cocktail recipes with multiple ingredients
- Specify quantities and units (oz, dashes, ml, etc.)
- Example: "Grapefruit Drop" with 1.5 oz Gin, 0.75 oz Elderflower Liqueur, 0.5 oz Lemon Juice
- Upload multiple images for each recipe
- Add preparation instructions
- Tag recipes for organization
- Search and filter recipes

### 3. Collections Management
- Group recipes into themed collections
- Upload collection images
- Tag and organize collections
- Search and filter collections

### 4. Additional Features
- **Mobile-friendly responsive design** - works on all devices
- **Image upload** - upload one or more images for any data element
- **Search & Filter** - powerful search across all data types
- **Tagging system** - organize with custom tags

## Technology Stack

- **Frontend**: AngularJS 1.8.2, Bootstrap 5, Font Awesome
- **Backend**: Python 3.x, Flask 3.0.0, Flask-CORS
- **Database**: MongoDB (NoSQL)
- **Image Processing**: Pillow

## Prerequisites

- Python 3.8 or higher
- MongoDB 4.0 or higher
- Modern web browser (Chrome, Firefox, Safari, Edge)

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/aswani1manish/my_bar.git
cd my_bar
```

### 2. Setup MongoDB

Install and start MongoDB:

```bash
# On macOS with Homebrew
brew install mongodb-community
brew services start mongodb-community

# On Ubuntu/Debian
sudo apt-get install mongodb
sudo systemctl start mongodb

# On Windows
# Download from https://www.mongodb.com/try/download/community
# Install and start MongoDB service
```

### 3. Setup Backend

```bash
cd backend

# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the Flask server
python app.py
```

The backend will run on `http://localhost:5000`

### 4. Setup Frontend

```bash
cd frontend

# Simply open index.html in a web browser or use a local server
# Using Python's built-in server:
python3 -m http.server 8000

# Or using Node.js http-server:
# npm install -g http-server
# http-server -p 8000
```

The frontend will be available at `http://localhost:8000`

## Usage

1. **Access the Application**: Open your browser and navigate to `http://localhost:8000`

2. **Load Sample Ingredients** (Optional but recommended):
   ```bash
   cd backend
   python3 load_sample_ingredients.py
   ```
   This will load 34 common cocktail ingredients including spirits, liqueurs, juices, syrups, and mixers.

3. **Add Ingredients**:
   - Click on "Ingredients" in the navigation
   - Fill in the ingredient details (name, category, description)
   - Upload one or more images
   - Add tags for organization
   - Click "Create"

4. **Create Recipes**:
   - Navigate to "Recipes"
   - Enter recipe name and description
   - Add ingredients with quantities and units
   - Upload recipe images
   - Add preparation instructions
   - Tag your recipe
   - Click "Create"

5. **Organize Collections**:
   - Go to "Collections"
   - Create a new collection
   - Select recipes to include
   - Upload collection images
   - Add tags
   - Click "Create"

6. **Search & Filter**:
   - Use the search bar to find items by name or description
   - Use the tag filter to find items with specific tags
   - Both filters work across ingredients, recipes, and collections

## Data Loading

### Load Sample Ingredients

The application includes a script to load 34 common cocktail ingredients:

```bash
cd backend
python3 load_sample_ingredients.py
```

Use `--dry-run` to preview what will be loaded without making changes:

```bash
python3 load_sample_ingredients.py --dry-run
```

The sample ingredients include:
- **Spirits**: Gin, Vodka, Rum, Tequila, Bourbon, Scotch, Cognac
- **Liqueurs**: Triple Sec, Cointreau, Elderflower Liqueur, Amaretto, Kahlúa, Baileys
- **Vermouth & Aperitifs**: Dry Vermouth, Sweet Vermouth, Campari, Aperol
- **Bitters**: Angostura Bitters, Orange Bitters
- **Juices**: Lemon, Lime, Orange, Grapefruit, Cranberry, Pineapple
- **Syrups**: Simple Syrup, Grenadine, Honey Syrup
- **Mixers**: Tonic Water, Club Soda, Ginger Beer, Cola, Ginger Ale

### Load from Bar Assistant Repository (Optional)

For a more comprehensive ingredient list, you can load ingredients from the Bar Assistant data repository:

```bash
cd backend
python3 load_ingredients.py
```

Note: This requires internet access and may take a few minutes.

## API Endpoints

### Ingredients
- `GET /api/ingredients` - List all ingredients (supports search and tag filters)
- `GET /api/ingredients/<id>` - Get a specific ingredient
- `POST /api/ingredients` - Create new ingredient
- `PUT /api/ingredients/<id>` - Update ingredient
- `DELETE /api/ingredients/<id>` - Delete ingredient

### Recipes
- `GET /api/recipes` - List all recipes (supports search and tag filters)
- `GET /api/recipes/<id>` - Get a specific recipe
- `POST /api/recipes` - Create new recipe
- `PUT /api/recipes/<id>` - Update recipe
- `DELETE /api/recipes/<id>` - Delete recipe

### Collections
- `GET /api/collections` - List all collections (supports search and tag filters)
- `GET /api/collections/<id>` - Get a specific collection
- `POST /api/collections` - Create new collection
- `PUT /api/collections/<id>` - Update collection
- `DELETE /api/collections/<id>` - Delete collection

### Images
- `GET /api/uploads/<filename>` - Retrieve uploaded image

## Configuration

### MongoDB Connection

By default, the app connects to MongoDB at `mongodb://localhost:27017/`. To use a different MongoDB instance, set the `MONGO_URI` environment variable:

```bash
export MONGO_URI="mongodb://username:password@host:port/database"
```

### CORS Configuration

The backend allows CORS from all origins by default. For production, update the CORS configuration in `backend/app.py`.

## Project Structure

```
my_bar/
├── backend/
│   ├── app.py              # Flask application with API endpoints
│   ├── requirements.txt    # Python dependencies
│   └── uploads/           # Image uploads (auto-created)
├── frontend/
│   ├── index.html         # Main HTML page
│   ├── css/
│   │   └── style.css      # Custom styles
│   ├── js/
│   │   ├── app.js         # AngularJS app configuration
│   │   ├── controllers/   # AngularJS controllers
│   │   ├── services/      # API service
│   │   └── directives/    # Image upload directive
│   └── views/             # HTML templates
├── .gitignore
└── README.md
```

## Contributing

This is a personal project for managing the Neighborhood Sips cocktail brand. Feel free to fork and adapt for your own use!

## License

MIT License - feel free to use this project for your own cocktail bar management needs.

## Author

Neighborhood Sips - Your Personal Cocktail Mixologist Brand

