# EduHub MongoDB Project

An educational platform database system built with MongoDB and Python.

## Setup Instructions

1. Install MongoDB Community Server (v8.0 or higher)
2. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Start MongoDB service
4. Run the Jupyter notebook:
   ```bash
   jupyter notebook
   ```

## Project Structure

- `requirements.txt` - Python dependencies
- `eduhub_mongodb_project.ipynb` - Main interactive notebook
- `eduhub_queries.py` - Python module with database operations
- `data/` - Directory for sample data files
- `docs/` - Documentation files

## Collections

- `users`: Student and instructor profiles
- `courses`: Course information and metadata
- `enrollments`: Student course enrollments
- `lessons`: Course content and lessons
- `assignments`: Course assignments
- `submissions`: Student assignment submissions

## Features

- User management (students and instructors)
- Course management and categorization
- Enrollment system
- Assessment system
- Analytics and reporting
- Search and discovery capabilities

## Usage

1. Connect to MongoDB using the provided connection string
2. Run database setup operations in the notebook
3. Execute CRUD operations and queries
4. Analyze data using aggregation pipelines

## Contributing

Please ensure to follow the project's coding standards and documentation requirements.
