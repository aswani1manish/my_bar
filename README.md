# Neighborhood Sips

A web application for managing your cocktail bar - ingredients, recipes, and collections.

**Neighborhood Sips** is your personal cocktail mixologist brand management system, built with AngularJS frontend, Python Flask backend, and MySQL for persistent storage.

## Deployment Options

### ☁️ Cloud Deployment (Recommended)
Deploy to the cloud for production use:
- **Backend**: PythonAnywhere
- **Database**: MySQL (e.g., PythonAnywhere MySQL, AWS RDS, etc.)
- **Frontend**: PythonAnywhere or static hosting

📖 **[Complete Cloud Deployment Guide](DEPLOYMENT.md)**

### 💻 Local Development
Run on your local machine for development and testing.

See [Local Installation](#installation--setup-local) below.

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
- **Database**: MySQL 8.0+ (RDBMS)
- **Image Processing**: Pillow

## Prerequisites

### For Local Development
- Python 3.8 or higher
- MySQL 8.0 or higher
- Modern web browser (Chrome, Firefox, Safari, Edge)

### For Cloud Deployment
- MySQL database (e.g., PythonAnywhere MySQL, AWS RDS, etc.)
- PythonAnywhere account (free tier available)
- See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions

## Installation & Setup (Local)

### 1. Clone the Repository

```bash
git clone https://github.com/aswani1manish/my_bar.git
cd my_bar
```

### 2. Setup MySQL

Install and start MySQL:

```bash
# On macOS with Homebrew
brew install mysql
brew services start mysql

# On Ubuntu/Debian
sudo apt-get install mysql-server
sudo systemctl start mysql

# On Windows
# Download from https://dev.mysql.com/downloads/mysql/
# Install and start MySQL service
```

Create the database:

```bash
# Log into MySQL
mysql -u root -p

# Create database and user (optional)
CREATE DATABASE neighborhood_sips;
CREATE USER 'neighborhood_sips_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON neighborhood_sips.* TO 'neighborhood_sips_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3. Setup Backend

```bash
cd backend

# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize the database schema
python init_db.py

# Start the Flask server
python app.py
```

The backend will run on `http://localhost:5000`

### 4. Setup Frontend

```bash
cd backend/static

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

### Load Cocktail Recipes

To load cocktail recipes from the bar-data-copy repository:

1. First, clone the bar-data-copy repository:
   ```bash
   git clone https://github.com/aswani1manish/bar-data-copy.git
   ```

2. Load the recipes into your database:
   ```bash
   cd backend
   python3 load_recipes.py --data-dir /path/to/bar-data-copy
   ```

Options:
- `--dry-run`: Preview what will be loaded without making changes
- `--copy-images`: Copy recipe images to the uploads folder (may take longer)

Example:
```bash
# Preview recipes without loading
python3 load_recipes.py --data-dir ../bar-data-copy --dry-run

# Load recipes without images (faster)
python3 load_recipes.py --data-dir ../bar-data-copy

# Load recipes with images
python3 load_recipes.py --data-dir ../bar-data-copy --copy-images
```

The script will:
- Load all recipes from the bar-data-copy repository
- Automatically create any missing ingredients
- Link recipes to existing ingredients in the database
- Optionally copy recipe images to the uploads folder

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

📘 **[See Collections MySQL Examples](COLLECTIONS_MYSQL_EXAMPLES.md)** for sample data formats and query examples.

### Images
- `GET /api/uploads/<filename>` - Retrieve uploaded image

## Configuration

### MySQL Connection

By default, the app connects to MySQL at `localhost:3306` with root user and no password. To use a different MySQL configuration, set these environment variables:

```bash
export MYSQL_HOST="your-mysql-host"
export MYSQL_PORT="3306"
export MYSQL_USER="your-username"
export MYSQL_PASSWORD="your-password"
export MYSQL_DATABASE="neighborhood_sips"
```

Or create a `.env` file in the `backend` directory:

```
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DATABASE=neighborhood_sips
```

### CORS Configuration

The backend allows CORS from all origins by default. For production, update the CORS configuration in `backend/app.py`.

## Project Structure

```
my_bar/
├── backend/
│   ├── app.py              # Flask application with API endpoints
│   ├── requirements.txt    # Python dependencies
│   ├── uploads/           # Image uploads (auto-created)
│   └── static/            # Frontend files
│       ├── index.html     # Main HTML page
│       ├── css/
│       │   └── style.css  # Custom styles
│       ├── js/
│       │   ├── app.js         # AngularJS app configuration
│       │   ├── controllers/   # AngularJS controllers
│       │   ├── services/      # API service
│       │   └── directives/    # Image upload directive
│       └── views/             # HTML templates
├── .gitignore
└── README.md
```

## Contributing

This is a personal project for managing the Neighborhood Sips cocktail brand. Feel free to fork and adapt for your own use!

## License

MIT License - feel free to use this project for your own cocktail bar management needs.

## Author

Neighborhood Sips - Your Personal Cocktail Mixologist Brand

