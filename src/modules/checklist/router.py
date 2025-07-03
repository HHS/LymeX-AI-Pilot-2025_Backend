from fastapi import APIRouter, UploadFile, File, HTTPException
import io
import asyncio
import json
from pathlib import Path
from src.infrastructure.minio import minio_client, generate_get_object_presigned_url
from src.environment import environment
from src.modules.checklist.master_checklist_model import MasterChecklist
from src.modules.checklist.master_checklist_schema import MasterChecklistQuestion
from src.modules.checklist.model import Checklist
from src.modules.checklist.schema import ChecklistQuestion, ChecklistProgress
import uuid


def get_checklist_folder(product_id: str) -> str:
    return f"product/{product_id}/checklist"


router = APIRouter()


@router.post("/master-checklist")
async def create_master_checklist():
    """Create master checklist records from the existing JSON file"""
    try:
        # Path to the JSON file
        json_file_path = Path(__file__).parent / "master_checklist.json"

        if not json_file_path.exists():
            raise HTTPException(
                status_code=404, detail="Master checklist JSON file not found"
            )

        # Read JSON data
        with open(json_file_path, "r") as file:
            questions = json.load(file)

        # Clear existing records
        await MasterChecklist.delete_all()

        # Create and insert new records
        inserted_records = []
        for question_data in questions:
            # Validate the question data
            validated_question = MasterChecklistQuestion(**question_data)

            # Create master checklist record
            master_record = MasterChecklist(
                question=validated_question.question,
                module=validated_question.module,
                draft=validated_question.draft,
                is_yes_or_no_question=validated_question.is_yes_or_no_question,
                default_answer=validated_question.default_answer,
            )

            # Insert into database
            inserted_record = await master_record.insert()
            inserted_records.append(inserted_record)

        return {
            "message": "Master checklist created successfully from JSON file",
            "records_inserted": len(inserted_records),
            "file_used": str(json_file_path),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating master checklist: {str(e)}"
        )


@router.get("/master-checklist")
async def get_master_checklist():
    """Get all master checklist questions"""
    try:
        records = await MasterChecklist.find_all().to_list()
        return {"total_records": len(records), "questions": records}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching master checklist: {str(e)}"
        )


@router.post("/upload-image")
async def upload_checklist_image(product_id: str, file: UploadFile = File(...)):
    try:
        # Generate a unique filename to prevent overwriting
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        object_name = f"{get_checklist_folder(product_id)}/{unique_filename}"
        file_content = await file.read()
        minio_client.put_object(
            bucket_name=environment.minio_bucket,
            object_name=object_name,
            length=len(file_content),
            data=io.BytesIO(file_content),
            content_type=file.content_type,
        )
        url = await generate_get_object_presigned_url(object_name)
        return {
            "object_name": object_name,
            "url": url,
            "message": "Image uploaded successfully",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents")
async def get_checklist_documents(product_id: str):
    try:
        prefix = f"{get_checklist_folder(product_id)}/"
        objects = await asyncio.to_thread(
            minio_client.list_objects,
            bucket_name=environment.minio_bucket,
            prefix=prefix,
            recursive=True,
        )
        documents = []
        for obj in objects:
            url = await generate_get_object_presigned_url(obj.object_name)
            documents.append({"object_name": obj.object_name, "url": url})
        return {"documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_or_create_checklist(product_id: str):
    """Get checklist by product_id, create if not exists using master checklist"""
    try:
        # Try to find existing checklist
        checklist = await Checklist.find_one({"product_id": product_id})

        if checklist:
            return {
                "message": "Checklist found",
                "checklist": checklist,
                "created": False,
            }

        # If not found, create new checklist from master checklist
        master_questions = await MasterChecklist.find_all().to_list()

        if not master_questions:
            raise HTTPException(
                status_code=500,
                detail="No master checklist questions found. Please populate master checklist first.",
            )

        # Create checklist questions from master checklist
        checklist_questions = []
        for i, master_q in enumerate(master_questions):
            checklist_question = ChecklistQuestion(
                id=f"{product_id}_q_{i+1}",
                question=master_q.question,
                status="incomplete",
                module=master_q.module,
                draft=master_q.draft,
                is_yes_or_no_question=master_q.is_yes_or_no_question,
                default_answer=master_q.default_answer,
            )
            checklist_questions.append(checklist_question)

        # Create progress
        progress = ChecklistProgress(total=len(checklist_questions), completed=0)

        # Create new checklist
        new_checklist = Checklist(
            product_id=product_id,
            ai_analysis_status="not_started",
            checklist=progress,
            questions=checklist_questions,
        )

        # Save to database
        await new_checklist.insert()

        return {
            "message": "New checklist created from master checklist",
            "checklist": new_checklist,
            "created": True,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting/creating checklist: {str(e)}"
        )
