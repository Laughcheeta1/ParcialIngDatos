# Books.toscrape.com Web Scraper

Web scraper para extraer información de libros desde books.toscrape.com y almacenarla en una base de datos PostgreSQL.

## Características

- Scraping completo de libros incluyendo:
  - Título, precio, UPC
  - Stock disponible
  - Categoría
  - Descripción
  - Rating (convertido a reviews)
  - URL de imagen
- Base de datos PostgreSQL con modelos relacionales
- CRUD operations completas
- Menú interactivo para gestión de datos
- Manejo de errores y duplicados

## Instalación

### 1. Clonar/Crear el proyecto
```bash
cd Parcial/
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar PostgreSQL

#### Opción A: Usar Docker
```bash
docker-compose up -d
```

#### Opción B: PostgreSQL local
Crear base de datos y usuario, luego actualizar `.env`:
```
DATABASE_URL=postgresql://tu_usuario:tu_password@localhost:5432/biblioteca
```

## Uso

### Modo Interactivo
```bash
python main.py
```

Opciones del menú:
1. **Inicializar/Recrear base de datos**: Crea las tablas necesarias
2. **Ejecutar web scraper**: Scrape libros de books.toscrape.com
3. **Ver estadísticas**: Muestra estadísticas de la base de datos
4. **Buscar libros**: Búsqueda por título
5. **Ver detalles de un libro**: Buscar por UPC

### Modo Directo (Scraping automático)
```bash
python main.py --scrape
```

### Solo Scraper
```bash
python scraper.py
```

## Estructura del Proyecto

```
Parcial/
├── models.py           # Modelos SQLModel de la base de datos
├── database.py         # Configuración y conexión a PostgreSQL
├── crud.py            # Operaciones CRUD para todos los modelos
├── scraper.py         # Lógica de web scraping
├── main.py            # Aplicación principal con menú
├── requirements.txt   # Dependencias del proyecto
├── .env              # Configuración de base de datos
├── docker-compose.yml # Configuración Docker para PostgreSQL
└── README.md         # Esta documentación
```

## Modelos de Base de Datos

- **Book**: Información principal del libro
- **Category**: Categorías de libros
- **Stock**: Control de inventario
- **Review**: Reviews y puntuaciones
- **Scores**: Puntuación agregada por libro
- **TaxRate**: Tasas de impuesto

## Notas Técnicas

- El scraper respeta un delay de 0.5 segundos entre requests
- Maneja duplicados verificando por UPC
- Los ratings del sitio se convierten en reviews automáticas
- Soporta scraping por páginas configurables
- Incluye manejo de errores y reintentos

## Ejemplos de Uso

```python
# Crear una categoría
from crud import CategoryCRUD
category = CategoryCRUD.create("Fiction")

# Buscar un libro por UPC
from crud import BookCRUD
book = BookCRUD.get_by_upc("978-0-123456-78-9")

# Obtener todas las reviews de un libro
from crud import ReviewCRUD
reviews = ReviewCRUD.get_book_reviews(book_id=1)
```