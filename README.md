
# Web Scraping Service

This FastAPI application provides a web scraping service to take screenshots of web pages and manage their metadata.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Example `curl` Commands](#example-curl-commands)

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/your-repo/web-scraping-service.git
    cd web-scraping-service
    ```

2. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Start the FastAPI application:
    ```sh
    uvicorn main:app --reload
    ```

2. The service will be available at `http://127.0.0.1:8000`.

## API Endpoints

### `GET /isalive`

Checks if the server is alive.

**Response:**
```json
{
  "status": "alive"
}
```

### `POST /screenshots`

Starts the process of web page crawling and screenshot capturing.

**Parameters:**
- `url` (form data, required): The starting URL for the crawl.
- `num_links` (form data, required): The number of links to follow from the starting URL.

**Response:**
```json
{
  "id": "unique_id"
}
```

### `GET /screenshots/{screenshot_id}`

Gets the list of screenshot names for the provided ID.

**Response:**
```json
{
  "screenshots": ["screenshot_name1", "screenshot_name2"]
}
```

### `GET /screenshots/website/{screenshot_name}`

Gets the website URL associated with the provided screenshot name.

**Response:**
```json
{
  "website": "https://www.example.com"
}
```

### `GET /screenshots/type/{screenshot_name}`

Gets the scrapable status of the website associated with the provided screenshot name.

**Response:**
```json
{
  "scrapable": true
}
```

## Example `curl` Commands

### Check if the server is alive:
```sh
curl -X GET http://127.0.0.1:8000/isalive
```

### Post a valid screenshot request:
```sh
curl -X POST http://127.0.0.1:8000/screenshots -F "url=https://www.example.com" -F "num_links=2"
```
`

### Get screenshots by a valid ID:
Replace `{valid_id}` with an actual ID returned from the previous POST request.
```sh
curl -X GET http://127.0.0.1:8000/screenshots/{valid_id}
```


### Get the website URL by a valid screenshot name:
Replace `{valid_screenshot_name}` with an actual screenshot name.
```sh
curl -X GET http://127.0.0.1:8000/screenshots/website/{valid_screenshot_name}
```


### Check scrapable status by a valid screenshot name:
Replace `{valid_screenshot_name}` with an actual screenshot name.
```sh
curl -X GET http://127.0.0.1:8000/screenshots/type/{valid_screenshot_name}
```


