# Ecommerce Backend API

A FastAPI-based ecommerce backend application built for the HROne Backend Intern hiring task. This application provides APIs for managing products and orders with MongoDB as the database.

## Features

- **Product Management**: Create and list products with size variants
- **Order Management**: Create orders and retrieve user order history
- **Filtering & Pagination**: Support for filtering products by name/size and pagination
- **Data Validation**: Comprehensive input validation using Pydantic models
- **Database Integration**: MongoDB integration with proper error handling
- **Environment Configuration**: Secure configuration using environment variables

## Tech Stack

- **Backend Framework**: FastAPI (Python 3.10+)
- **Database**: MongoDB (using PyMongo)
- **Validation**: Pydantic
- **Server**: Uvicorn
- **Configuration**: Python-dotenv

## API Endpoints

### Products

#### Create Product
- **POST** `/products`
- **Request Body**:
```json
{
  "name": "Product Name",
  "price": 29.99,
  "description": "Product description",
  "sizes": [
    {"size": "large", "quantity": 10},
    {"size": "medium", "quantity": 5}
  ]
}
```
- **Response**:
```json
{
  "product_id": "507f1f77bcf86cd799439011"
}
```

#### List Products
- **GET** `/products`
- **Query Parameters**:
  - `name` (optional): Filter by product name (supports regex)
  - `size` (optional): Filter products with specific size
  - `limit` (optional, default=10): Number of products to return
  - `offset` (optional, default=0): Number of products to skip
- **Response**:
```json
{
  "products": [
    {
      "product_id": "507f1f77bcf86cd799439011",
      "name": "Product Name",
      "price": 29.99,
      "description": "Product description",
      "sizes": [
        {"size": "large", "quantity": 10}
      ]
    }
  ]
}
```

### Orders

#### Create Order
- **POST** `/orders`
- **Request Body**:
```json
{
  "user_id": "user123",
  "items": [
    {
      "product_id": "507f1f77bcf86cd799439011",
      "bought_quantity": 2,
      "total_amount": 59.98
    }
  ],
  "user_address": "123 Main St, City, State"
}
```
- **Response**:
```json
{
  "id": "507f1f77bcf86cd799439012"
}
```

#### Get User Orders
- **GET** `/orders/{user_id}`
- **Query Parameters**:
  - `limit` (optional, default=10): Number of orders to return
  - `offset` (optional, default=0): Number of orders to skip
- **Response**:
```json
{
  "orders": [
    {
      "order_id": "507f1f77bcf86cd799439012",
      "user_id": "user123",
      "items": [
        {
          "product_id": "507f1f77bcf86cd799439011",
          "bought_quantity": 2,
          "total_amount": 59.98
        }
      ],
      "user_address": "123 Main St, City, State",
      "timestamp": "2024-01-15T10:30:00Z",
      "total_amount": 59.98
    }
  ]
}
```

## Database Schema

### Products Collection
```javascript
{
  "_id": ObjectId,
  "name": String,
  "price": Number,
  "description": String (optional),
  "sizes": [
    {
      "size": String,
      "quantity": Number
    }
  ],
  "created_at": DateTime
}
```

### Orders Collection
```javascript
{
  "_id": ObjectId,
  "user_id": String,
  "items": [
    {
      "product_id": String,
      "bought_quantity": Number,
      "total_amount": Number
    }
  ],
  "user_address": String,
  "timestamp": DateTime,
  "total_amount": Number
}
```

## Installation & Setup

### Prerequisites
- Python 3.10+
- MongoDB (local installation or MongoDB Atlas)

### Local Development

1. **Clone the repository**:
```bash
git clone <repository-url>
cd ecommerce-backend
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:
   Create a `.env` file in the root directory:
```env
MONGO_URL=mongodb://localhost:27017/
```
   For MongoDB Atlas:
```env
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/
```

5. **Run the application**:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

### Production Deployment

The application is configured for deployment on platforms like Render or Railway:

1. **Set the `MONGO_URL` environment variable** with your MongoDB connection string
2. **The application will automatically bind to `0.0.0.0:8000`**
3. **Health check endpoint available at `/health`**

**Important**: The application will fail to start if `MONGO_URL` is not provided in environment variables for security reasons.

## API Documentation

Once the application is running, visit:
- **Interactive API docs**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative docs**: `http://localhost:8000/redoc` (ReDoc)

## Environment Variables

- `MONGO_URL` (required): MongoDB connection string

## Error Handling

The API includes comprehensive error handling:
- Input validation errors return 422 status codes
- Resource not found errors return 404 status codes
- Missing products in orders return 400 status codes
- Server errors return 500 status codes with descriptive messages

## Database Indexing

For better performance, consider adding these indexes:
```javascript
// Products collection
db.products.createIndex({ "name": 1 })
db.products.createIndex({ "sizes.size": 1 })

// Orders collection
db.orders.createIndex({ "user_id": 1 })
db.orders.createIndex({ "timestamp": -1 })
```

## Testing

You can test the APIs using:
- **Swagger UI**: Available at `/docs` endpoint
- **Postman**: Import the API endpoints
- **curl**: Command line testing

Example curl commands:
```bash
# Create a product
curl -X POST "http://localhost:8000/products" \
     -H "Content-Type: application/json" \
     -d '{"name":"Test Product","price":29.99,"description":"A test product","sizes":[{"size":"large","quantity":10}]}'

# List products
curl "http://localhost:8000/products?limit=5"

# Create an order (replace PRODUCT_ID with actual product ID)
curl -X POST "http://localhost:8000/orders" \
     -H "Content-Type: application/json" \
     -d '{"user_id":"user123","items":[{"product_id":"PRODUCT_ID","bought_quantity":1,"total_amount":29.99}],"user_address":"123 Main St"}'

# Get user orders
curl "http://localhost:8000/orders/user123"
```

## Project Structure

```
ecommerce-backend/
├── main.py              # Main FastAPI application
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (create this)
├── README.md           # Project documentation
└── .gitignore          # Git ignore file
```

## Key Features

1. **Secure Configuration**: Uses environment variables with validation
2. **Product ID Response**: Create product endpoint returns product_id
3. **Optional Description**: Product description is optional in the model
4. **Order ID Response**: Create order endpoint returns order id
5. **Comprehensive Validation**: Validates product existence when creating orders
6. **Database Connection**: Explicit database selection with connection validation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is built for the HROne Backend Intern hiring task.
