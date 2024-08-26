from fastapi import APIRouter, Depends, WebSocket
from fastapi.responses import JSONResponse, Response
from sqlalchemy.testing.plugin.plugin_base import logging

from src.use_cases.cv_helper_use_case import CvHelperUseCase
from src.use_cases.create_cover_letter_use_case import CreateCoverLetterUseCase
from src.viewmodels.cover_letter_communication import CoverLetterCommunication
from src.viewmodels.job_advert_request import JobAdvertRequest

router = APIRouter(prefix="/cv")


@router.post("/summarize")
def summarize(
    job_advert_request: JobAdvertRequest,
    cv_helper_use_case: CvHelperUseCase = Depends(),
):
    try:
        answer = cv_helper_use_case.summarize_job_advert(job_advert_request.web_page)
        return JSONResponse(answer, 200)
    except SyntaxError as e:
        return Response(f"Could not read URL.\n{e}", status_code=400)
    except Exception as e:
        return Response(e, status_code=500)


@router.websocket("/dummy")
async def dummy_websocket(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        if "state" in data and data["state"] == "complete":
            break
        await websocket.send_text("This is the current state")
        await websocket.send_json({"This": ["is", "also", "possible"]})
    await websocket.close()


@router.websocket("/cover-letter")
async def cover_letter(
    websocket: WebSocket,
    write_cover_letter_use_case: CreateCoverLetterUseCase = Depends(),
):
    await websocket.accept()
    write_cover_letter_use_case.initialize()
    while True:
        data = await websocket.receive_json()
        try:
            parsed_data = CoverLetterCommunication(**data)
            if parsed_data.state == "close":
                break
            async for result in write_cover_letter_use_case.run(parsed_data):
                await websocket.send_json(result | {"status": "successful"})
        except SyntaxError as e:
            await websocket.send_json(
                {"status": "error", "message": f"Could not read URL.\n{e}"}
            )
        except Exception as e:
            await websocket.send_json({"status": "error", "message": e})

    await websocket.close()
