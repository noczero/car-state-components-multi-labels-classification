from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.logger import logger
from starlette.concurrency import run_in_threadpool
from starlette.responses import JSONResponse

from models import CarPhysicalChangeExplainer, get_explainer_model

router = APIRouter()

ExplainerModelDep = Annotated[CarPhysicalChangeExplainer, Depends(get_explainer_model)]


@router.post("/predict", summary="Explain car state components image")
async def predict(model: ExplainerModelDep, image: UploadFile = File(...)):
    try:
        # 1. Read image contents
        image_contents = await image.read()
        if not image_contents:
            raise HTTPException(status_code=400, detail="No image content found or image is empty.")

        # 2. Basic validation (can be expanded)
        allowed_image_types = ["image/jpeg", "image/png"]  # Example, adjust as needed
        if image.content_type not in allowed_image_types:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Invalid image type: {image.content_type}. "
                    f"Allowed types are: {', '.join(allowed_image_types)}"
                )
            )

        # input_tensor = model.preprocess_image(image_contents)
        # prediction_result = model.predict_image(input_tensor)

        # 3. Perform blocking operations (preprocessing and prediction) in a thread pool
        try:
            # Run synchronous preprocessing in a thread pool
            input_tensor = await run_in_threadpool(model.preprocess_image_bytes, image_contents)

            # Run synchronous prediction in a thread pool
            prediction_result = await run_in_threadpool(model.completions, input_tensor)
        except ValueError as ve:  # Catch specific errors from preprocessing/prediction
            logger.warning(f"ValueError during model processing: {ve}")
            raise HTTPException(status_code=400, detail=str(ve))

        return JSONResponse(prediction_result)

    except HTTPException as e:
        # Re-raise HTTPException to be handled by FastAPI's default error handling
        raise e
    except ValueError as ve:  # Catch specific errors from preprocessing
        logger.warning(f"ValueError in /components: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        # Log the full error for server-side debugging
        logger.error(f"An unexpected error occurred in /components endpoint: {e}", exc_info=True)
        # Return a generic 500 error to the client
        raise HTTPException(status_code=500, detail="An internal server error occurred while processing the image.")
    finally:
        # Always close the uploaded file
        if image:
            await image.close()
