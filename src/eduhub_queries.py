from pymongo import MongoClient, IndexModel, ASCENDING, DESCENDING
from datetime import datetime
import pandas as pd
from typing import Dict, List, Optional

class EduHubDB:
    def __init__(self, connection_string: str = 'mongodb://localhost:27017/'):
        print("Initializing database connection...")
        self.client = MongoClient(connection_string)
        self.db = self.client['eduhub_db']
        self.initialize_collections()

    def initialize_collections(self):
        """Initialize collections with validation rules"""

        def setup_collection(name: str, schema: dict):
            if name not in self.db.list_collection_names():
                print(f"Creating collection: {name}")
                self.db.create_collection(name)
            print(f"Applying validation to collection: {name}")
            self.db.command("collMod", name, validator=schema)

    # Users schema
        user_schema = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["email", "firstName", "lastName", "role"],
                "properties": {
                    "email": {"bsonType": "string", "pattern": "^\\S+@\\S+\\.\\S+$"},
                    "firstName": {"bsonType": "string"},
                    "lastName": {"bsonType": "string"},
                    "role": {"enum": ["student", "instructor"]},
                    "dateJoined": {"bsonType": "date"},
                    "isActive": {"bsonType": "bool"}
                }
            }
        }

        # Courses schema
        course_schema = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["title", "instructorId", "category", "level"],
                "properties": {
                    "title": {"bsonType": "string"},
                    "instructorId": {"bsonType": "string"},
                    "category": {"bsonType": "string"},
                    "level": {"enum": ["beginner", "intermediate", "advanced"]},
                    "price": {"bsonType": "double", "minimum": 0},
                    "isPublished": {"bsonType": "bool"}
                }
            }
        }

        # Enrollments schema (you missed this earlier)
        enrollment_schema = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["studentId", "courseId", "enrollmentDate"],
                "properties": {
                    "studentId": {"bsonType": "string"},
                    "courseId": {"bsonType": "string"},
                    "enrollmentDate": {"bsonType": "date"},
                    "status": {"enum": ["active", "completed", "dropped"]}
                }
            }
        }

        setup_collection("users", user_schema)
        setup_collection("courses", course_schema)
        setup_collection("enrollments", enrollment_schema)
    
    def create_indexes(self):
        """Create necessary indexes for performance optimization"""
        # Users indexes
        self.db.users.create_index([("email", ASCENDING)], unique=True)
        self.db.users.create_index([("role", ASCENDING)])
        
        # Courses indexes
        self.db.courses.create_index([("title", ASCENDING)])
        self.db.courses.create_index([("category", ASCENDING)])
        self.db.courses.create_index([("tags", ASCENDING)])
        
        # Enrollments indexes
        self.db.enrollments.create_index([
            ("studentId", ASCENDING),
            ("courseId", ASCENDING)
        ], unique=True)

    def add_user(self, user_data: Dict) -> str:
        """Add a new user to the database"""
        user_data['dateJoined'] = datetime.utcnow()
        user_data['isActive'] = True
        result = self.db.users.insert_one(user_data)
        return str(result.inserted_id)

    def add_course(self, course_data: Dict) -> str:
        """Add a new course to the database"""
        course_data['createdAt'] = datetime.utcnow()
        course_data['updatedAt'] = datetime.utcnow()
        result = self.db.courses.insert_one(course_data)
        return str(result.inserted_id)

    def enroll_student(self, student_id: str, course_id: str) -> bool:
        """Enroll a student in a course"""
        enrollment = {
            "studentId": student_id,
            "courseId": course_id,
            "enrollmentDate": datetime.utcnow(),
            "status": "active"
        }
        result = self.db.enrollments.insert_one(enrollment)
        return result.acknowledged

    def get_courses_by_category(self, category: str) -> List[Dict]:
        """Get all courses in a specific category"""
        return list(self.db.courses.find({"category": category}))

    def get_course_details_with_instructor(self, course_id: str) -> Optional[Dict]:
        """Get course details with instructor information"""
        course = self.db.courses.find_one({"_id": course_id})
        if course:
            instructor = self.db.users.find_one({"_id": course["instructorId"]})
            return {
                "course": course,
                "instructor": instructor
            }
        return None

    def update_user_profile(self, user_id: str, updates: Dict) -> bool:
        """Update user profile information"""
        result = self.db.users.update_one(
            {"_id": user_id},
            {"$set": updates}
        )
        return result.modified_count > 0

    def mark_course_as_published(self, course_id: str) -> bool:
        """Mark a course as published"""
        result = self.db.courses.update_one(
            {"_id": course_id},
            {"$set": {"isPublished": True}}
        )
        return result.modified_count > 0

    def get_course_enrollment_stats(self) -> pd.DataFrame:
        """Get course enrollment statistics using aggregation"""
        pipeline = [
            {
                "$group": {
                    "_id": "$courseId",
                    "totalEnrollments": {"$sum": 1},
                    "activeStudents": {
                        "$sum": {"$cond": [{"$eq": ["$status", "active"]}, 1, 0]}
                    }
                }
            },
            {
                "$lookup": {
                    "from": "courses",
                    "localField": "_id",
                    "foreignField": "_id",
                    "as": "course"
                }
            },
            {
                "$unwind": "$course"
            },
            {
                "$project": {
                    "courseId": 1,
                    "courseTitle": "$course.title",
                    "totalEnrollments": 1,
                    "activeStudents": 1,
                    "enrollmentRate": {
                        "$divide": ["$activeStudents", "$totalEnrollments"]
                    }
                }
            }
        ]
        
        results = list(self.db.enrollments.aggregate(pipeline))
        return pd.DataFrame(results)

    def close_connection(self):
        """Close MongoDB connection"""
        self.client.close()

# Example usage
if __name__ == "__main__":
    db = EduHubDB()
    # db.create_indexes()
    
    # Example operations
    user_data = {
        "email": "john.doe@example.com",
        "firstName": "John",
        "lastName": "Doe",
        "role": "student"
    }
    
    course_data = {
        "title": "Introduction to Python",
        "description": "Learn Python programming from scratch",
        "instructorId": "instructor123",
        "category": "Programming",
        "level": "beginner",
        "price": 99.99
    }
    
    user_id = db.add_user(user_data)
    course_id = db.add_course(course_data)
    
    db.enroll_student(user_id, course_id)
    
    db.close_connection()

    def __init__(self, connection_string: str = 'mongodb://localhost:27017/'):
        print("Initializing database connection...")
        self.client = MongoClient(connection_string)
        self.db = self.client['eduhub_db']
        self.initialize_collections()

    def initialize_collections(self):
        """Initialize collections with validation rules"""

        def setup_collection(name: str, schema: dict):
            if name not in self.db.list_collection_names():
                print(f"Creating collection: {name}")
                self.db.create_collection(name)
            print(f"Applying validation to collection: {name}")
            self.db.command("collMod", name, validator=schema)