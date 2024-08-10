from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.use_cases.cv_helper_use_case import CvHelperUseCase
from src.viewmodels.job_advert_request import JobAdvertRequest

router = APIRouter(prefix="/cv")

@router.post("/summarize")
def summarize(job_advert_request: JobAdvertRequest, cv_helper_use_case: CvHelperUseCase = Depends()):
    answer = cv_helper_use_case.summarize_job_advert(job_advert_request)
    return JSONResponse(answer, 200)