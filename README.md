# FastAPI E-commerce Microservices

This project is a backend system for a simple e-commerce platform, built using a microservice architecture with Python and **FastAPI**. It consists of three independent services that communicate via a shared MongoDB database.

The services are deployed on Render and are publicly accessible.

## 🚀 Live Services & API Docs

| Service | Description | Base URL | Live API Docs (Swagger) |
| :--- | :--- | :--- | :--- |
| 👤 **User Service** | Manages user registration & login. | `https://user-service-fawu.onrender.com` | [**/docs**](https://user-service-fawu.onrender.com/docs) |
| 📦 **Product Service** | Manages product catalog (create, list, search). | `https://ps-latest-1.onrender.com` | [**/docs**](https://ps-latest-1.onrender.com/docs) |
| 🛒 **Order Service** | Manages order creation & retrieval. | `https://order-service-4oek.onrender.com` | [**/docs**](https://order-service-4oek.onrender.com/docs) |

---

## 🛠️ Technology Stack

* **Framework:** **FastAPI** for high-performance REST APIs.
* **Database:** **MongoDB** (accessed via **PyMongo**).
* **Data Validation:** **Pydantic** for request/response modeling.
* **Authentication:** **JWT** (JSON Web Tokens) for auth, using `python-jose`.
* **Password Hashing:** **Passlib** with `bcrypt`.
* **Deployment:** **Render**.

---

## 🏛️ Service Architecture

The project is divided into three core microservices:

1.  **User & Auth Service:**
    * Handles all user-related operations.
    * `POST /users/register`: Creates a new user account with a hashed password.
    * `POST /users/login`: Verifies credentials and issues a JWT access token.
    * `GET /health/db`: Checks the database connection.

2.  **Product Catalog Service:**
    * Manages the inventory of products.
    * `POST /products`: Adds a new product to the database.
    * `GET /products`: Lists all products. Can be filtered by name using the `?q=` query parameter (case-insensitive regex search).
    * `GET /health/db`: Checks the database connection.

3.  **Order Service:**
    * Manages customer orders.
    * `POST /orders`: Creates a new order. This endpoint performs several crucial checks:
        * Validates all `product_id`s.
        * Checks if the requested `quantity` is available in the product's `stock`.
        * Atomically decrements the `stock` for each product in the order upon successful creation.
    * `GET /orders/{order_id}`: Retrieves the details of a specific order by its ID.
    * `GET /health/db`: Checks the database connection.

---

## 📋 API Endpoint Details

You can find the full interactive documentation at the **/docs** link for each service listed above. Here is a quick reference.

### 👤 User Service (`https://user-service-fawu.onrender.com`)

* **`POST /users/register`**
    * **Description:** Creates a new user.
    * **Request Body:**
        ```json
        {
          "email": "user@example.com",
          "password": "your_strong_password",
          "name": "Test User"
        }
        ```
    * **Response (200):**
        ```json
        {
          "id": "60d...a1",
          "email": "user@example.com",
          "name": "Test User"
        }
        ```

* **`POST /users/login`**
    * **Description:** Logs in an existing user and returns a JWT token.
    * **Request Body:**
        ```json
        {
          "email": "user@example.com",
          "password": "your_strong_password"
        }
        ```
    * **Response (200):**
        ```json
        {
          "access_token": "eyJ...w5c",
          "token_type": "bearer"
        }
        ```

### 📦 Product Service (`https://ps-latest-1.onrender.com`)

* **`POST /products`**
    * **Description:** Creates a new product.
    * **Request Body:**
        ```json
        {
          "name": "Laptop",
          "description": "A powerful laptop",
          "price": 1299.99,
          "category": "Electronics",
          "stock": 50
        }
        ```
    * **Response (201):**
        ```json
        {
          "name": "Laptop",
          "description": "A powerful laptop",
          "price": 1299.99,
          "category": "Electronics",
          "stock": 50,
          "id": "60d...b2"
        }
        ```

* **`GET /products`**
    * **Description:** Lists all products.
    * **Query Parameter:** `?q=laptop` (to search for products with "laptop" in the name).
    * **Response (200):** `List[ProductOut]`

### 🛒 Order Service (`https://order-service-4oek.onrender.com`)

* **`POST /orders`**
    * **Description:** Creates a new order and decrements product stock.
    * **Request Body:**
        ```json
        {
          "user_id": "60d...a1", // The 'id' from the User service
          "items": [
            {
              "product_id": "60d...b2", // The 'id' from the Product service
              "quantity": 1
            }
          ]
        }
        ```
    * **Response (201):**
        ```json
        {
          "id": "60d...c3",
          "status": "PLACED"
        }
        ```

* **`GET /orders/{order_id}`**
    * **Description:** Retrieves a specific order.
    * **Response (200):**
        ```json
        {
          "id": "60d...c3",
          "user_id": "60d...a1",
          "items": [
            {
              "product_id": "60d...b2",
              "quantity": 1
            }
          ],
          "status": "PLACED"
        }
        ```

---

## 🏁 Example Workflow

1.  **Register a user:**
    * `POST https://user-service-fawu.onrender.com/users/register`
    * Save the returned `id` (e.g., `"60d...a1"`).

2.  **(Optional) Log in:**
    * `POST https://user-service-fawu.onrender.com/users/login`
    * Get the `access_token` (Note: The current Order/Product APIs do not use this token, but this is how you would get it).

3.  **Create a product:**
    * `POST https://ps-latest-1.onrender.com/products`
    * Save the returned `id` (e.g., `"60d...b2"`).

4.  **Create an order:**
    * `POST https://order-service-4oek.onrender.com/orders`
    * Use the `user_id` from step 1 and the `product_id` from step 3 in the request body.
    * Save the returned order `id` (e.g., `"60d...c3"`).

5.  **Check the order:**
    * `GET https://order-service-4oek.onrender.com/orders/60d...c3`

---

## 🏃 Running Locally

To run these services locally, you would need to:

1.  Clone this repository (assuming it's in one).
2.  Create a `.env` file in each service's directory.
3.  Add the required environment variables:
    * `MONGO_URI`: Your MongoDB connection string.
    * `DB_NAME`: The name of your database.
    * `JWT_SECRET`: A long, random, secret string (for the User service).
4.  Install dependencies for each service. The main dependencies are:
    ```bash
    pip install fastapi "uvicorn[standard]" pymongo "pydantic[email]" passlib "python-jose[cryptography]"
    ```
5.  Run each service from its directory using Uvicorn:
    ```bash
    # In service-1 directory
    uvicorn main:app --reload --port 8001
    
    # In service-2 directory
    uvicorn main:app --reload --port 8002
    
    # In service-3 directory
    uvicorn main:app --reload --port 8003
    ```
