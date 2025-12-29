# Neighborhood Sips - Project Summary

## Overview
Neighborhood Sips is a complete web application for managing a cocktail bar. It's designed as a personal cocktail mixologist brand management system with mobile-friendly, responsive design.

## Three Core Data Elements

### 1. Ingredients
Individual components used in cocktails:
- **Examples**: Gin, Vodka, Elderflower Liqueur, Lemon Juice
- **Properties**: Name, description, category, tags, multiple images, strength (ABV), origin
- **Features**: Search by name/description, filter by tags, upload multiple images

### 2. Recipes
Cocktail recipes made from ingredients with specific quantities:
- **Example**: "Grapefruit Drop" with:
  - 1.5 oz Gin
  - 0.75 oz Elderflower Liqueur
  - 0.5 oz Lemon Juice
- **Properties**: Name, description, ingredient list (with quantities & units), instructions, tags, multiple images
- **Features**: Search, filter, link to ingredients, image gallery

### 3. Collections
Groups of related recipes:
- **Examples**: "Summer Cocktails", "Classic Martinis", "Tiki Drinks"
- **Properties**: Name, description, recipe IDs, tags, multiple images
- **Features**: Search, filter, organize multiple recipes together

## Technology Stack

### Backend (Python/Flask)
- **Framework**: Flask 3.0.0
- **Database**: MongoDB (NoSQL) via PyMongo 4.6.1
- **Image Processing**: Pillow 10.1.0
- **CORS**: Flask-CORS 4.0.0
- **Features**:
  - RESTful API with full CRUD operations
  - Base64 image upload and processing
  - Image resizing and optimization
  - Search and filtering
  - Tag-based organization

### Frontend (AngularJS)
- **Framework**: AngularJS 1.8.2
- **UI**: Bootstrap 5.3.0 (mobile-friendly, responsive)
- **Icons**: Font Awesome 6.4.0
- **Features**:
  - Single Page Application (SPA) with routing
  - Responsive design for mobile/tablet/desktop
  - Image upload with preview
  - Real-time search and filtering
  - Tag management

## Key Features

### ✓ Mobile-Friendly Responsive Design
- Works on phones, tablets, and desktops
- Bootstrap 5 grid system
- Touch-friendly interface
- Responsive navigation

### ✓ Image Upload Support
- Upload multiple images per item (ingredients, recipes, collections)
- Base64 encoding for easy transmission
- Automatic image resizing (max 1024x1024)
- Preview before upload
- Delete individual images

### ✓ Search & Filter
- Full-text search across all data types
- Search by name or description
- Filter by tags (comma-separated)
- Works for ingredients, recipes, and collections

### ✓ Tag Management
- Add custom tags to any item
- Remove tags easily
- Filter by tags
- Visual tag display with badges

## File Structure

```
my_bar/
├── backend/
│   ├── app.py                          # Main Flask application
│   ├── requirements.txt                # Python dependencies
│   ├── load_sample_ingredients.py      # Load 34 sample ingredients
│   ├── load_ingredients.py             # Load from Bar Assistant repo
│   ├── test_api.py                     # API structure tests
│   ├── test_functional.py              # Functional tests
│   ├── .env.example                    # Environment variables template
│   └── uploads/                        # Image storage (auto-created)
│
├── frontend/
│   ├── index.html                      # Main HTML page
│   ├── css/
│   │   └── style.css                   # Custom styles
│   ├── js/
│   │   ├── app.js                      # AngularJS app config
│   │   ├── controllers/
│   │   │   ├── main-controller.js
│   │   │   ├── ingredients-controller.js
│   │   │   ├── recipes-controller.js
│   │   │   └── collections-controller.js
│   │   ├── services/
│   │   │   └── api-service.js          # HTTP service
│   │   └── directives/
│   │       └── image-upload.js         # Image upload component
│   └── views/
│       ├── home.html
│       ├── ingredients.html
│       ├── recipes.html
│       └── collections.html
│
├── start_backend.sh                    # Backend startup script
├── start_frontend.sh                   # Frontend startup script
├── README.md                           # Complete documentation
└── .gitignore                          # Git ignore rules
```

## API Endpoints

### Ingredients
- `GET /api/ingredients` - List all (supports ?search= and ?tags=)
- `GET /api/ingredients/<id>` - Get one
- `POST /api/ingredients` - Create
- `PUT /api/ingredients/<id>` - Update
- `DELETE /api/ingredients/<id>` - Delete

### Recipes
- `GET /api/recipes` - List all (supports ?search= and ?tags=)
- `GET /api/recipes/<id>` - Get one
- `POST /api/recipes` - Create
- `PUT /api/recipes/<id>` - Update
- `DELETE /api/recipes/<id>` - Delete

### Collections
- `GET /api/collections` - List all (supports ?search= and ?tags=)
- `GET /api/collections/<id>` - Get one
- `POST /api/collections` - Create
- `PUT /api/collections/<id>` - Update
- `DELETE /api/collections/<id>` - Delete

### Utility
- `GET /api/health` - Health check
- `GET /api/uploads/<filename>` - Serve uploaded images

## Sample Data

The application includes 34 pre-defined cocktail ingredients:
- 8 Spirits (Gin, Vodka, Rum, Tequila, Bourbon, Scotch, Cognac, etc.)
- 6 Liqueurs (Triple Sec, Cointreau, Elderflower Liqueur, etc.)
- 4 Vermouth & Aperitifs (Dry Vermouth, Sweet Vermouth, Campari, Aperol)
- 2 Bitters (Angostura, Orange)
- 6 Juices (Lemon, Lime, Orange, Grapefruit, Cranberry, Pineapple)
- 3 Syrups (Simple, Grenadine, Honey)
- 5 Mixers (Tonic Water, Club Soda, Ginger Beer, Cola, Ginger Ale)

## Quick Start

### Prerequisites
- Python 3.8+
- MongoDB 4.0+
- Modern web browser

### Setup
```bash
# 1. Install MongoDB and start it
sudo service mongodb start

# 2. Install backend dependencies
cd backend
pip install -r requirements.txt

# 3. Load sample ingredients
python3 load_sample_ingredients.py

# 4. Start backend (Terminal 1)
python3 app.py
# Backend runs on http://localhost:5000

# 5. Start frontend (Terminal 2)
cd frontend
python3 -m http.server 8000
# Frontend available at http://localhost:8000
```

### Or use the convenience scripts:
```bash
# Terminal 1
./start_backend.sh

# Terminal 2
./start_frontend.sh
```

## Example Usage

### Creating the "Grapefruit Drop" Recipe

1. **Load ingredients** (if not already loaded):
   - Gin
   - Elderflower Liqueur
   - Lemon Juice (or use Grapefruit Juice)

2. **Create the recipe**:
   - Name: "Grapefruit Drop"
   - Description: "A refreshing citrus cocktail"
   - Ingredients:
     - 1.5 oz Gin
     - 0.75 oz Elderflower Liqueur
     - 0.5 oz Lemon Juice
   - Instructions: "Shake all ingredients with ice, strain into chilled glass"
   - Tags: cocktail, citrus, refreshing
   - Upload an image of the finished drink

3. **Add to a collection**:
   - Create "Summer Cocktails" collection
   - Add "Grapefruit Drop" to it
   - Upload a collection image

## Testing

### Run API tests:
```bash
cd backend
python3 test_api.py          # Test API structure
python3 test_functional.py   # Test full CRUD operations
```

### Manual testing:
1. Open http://localhost:8000
2. Navigate through Ingredients, Recipes, Collections
3. Test create, read, update, delete operations
4. Test search and filter functionality
5. Test image upload on all screens
6. Test on mobile device or resize browser window

## Security Features

- Input validation on backend
- Base64 image encoding
- File size limits (16MB max)
- Allowed file types (png, jpg, jpeg, gif, webp)
- Image resizing to prevent large uploads
- MongoDB injection protection via PyMongo

## Future Enhancements

Potential features for v2:
- User authentication
- Recipe ratings and reviews
- Inventory tracking
- Shopping list generation
- Recipe recommendations
- Social sharing
- Export recipes as PDF
- Barcode scanning for ingredients
- Integration with Bar Assistant API

## Credits

- Inspired by the Bar Assistant project
- Built for the "Neighborhood Sips" cocktail mixologist brand
- Created as a personal bar management system

## License

MIT License - Free to use and modify for personal or commercial use.
