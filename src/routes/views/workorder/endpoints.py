from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import ValidationError

from src.routes.views.workorder.services import create_workorder, read_workorder, update_workorder, delete_workorder
from src.routes.models import WorkorderRequest, WorkorderResponse

router = APIRouter(tags=["Workorder"])


@router.post(
    '/workorder',
    description="Create a new workorder",
    response_model=WorkorderResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_workorder",
)
async def post_workorder_endpoint(workorder: WorkorderRequest) -> WorkorderResponse:
    try:
        created_workorder = create_workorder(workorder)
        return created_workorder
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation Error: {e.errors()}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the work order: {str(e)}"
        )


@router.get(
    '/workorder/{workorderid}',
    description="Get a workorder by id",
    response_model=WorkorderResponse,
    status_code=status.HTTP_200_OK,
    operation_id="get_workorder",
)
async def get_workorder_endpoint(workorderid: UUID) -> WorkorderResponse:
    try:
        workorder = read_workorder(workorderid)
        return workorder
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation Error: {e.errors()}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while getting the workorder: {str(e)}"
        )


@router.put(
    '/workorder/{workorderid}',
    description="Update a workorder",
    status_code=status.HTTP_200_OK,
    operation_id="update_workorder",
)
async def put_workorder_endpoint(workorderid: UUID, workorder: WorkorderRequest):
    try:
        updated_workorder = update_workorder(workorderid, workorder)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation Error: {e.errors()}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the workorder: {str(e)}"
        )


@router.delete(
    '/workorder/{workorderid}',
    description="Delete a workorder",
    status_code=status.HTTP_200_OK,
    operation_id="delete_workorder",
)
async def delete_workorder_endpoint(workorderid: UUID):
    try:
        delete_workorder(workorderid)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation Error: {e.errors()}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting workorder: {str(e)}"
        )
