# import io
# import os
# import uvicorn
# from fastapi import FastAPI, File, UploadFile, HTTPException
# from fastapi.responses import StreamingResponse
# from fastapi.middleware.cors import CORSMiddleware
# import numpy as np
# import cv2
# from insightface.app import FaceAnalysis
# from insightface.model_zoo import get_model
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse

# app = FastAPI(title="Face Swap API")

# # Allow CORS (optional, adjust as needed)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Change this to the specific domain in production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Path to the model
# MODEL_PATH = os.path.join("models", "inswapper_128.onnx")

# # Initialize models globally to load them once
# @app.on_event("startup")
# def load_models():
#     global face_app, swapper
#     face_app = FaceAnalysis(name='buffalo_l')
#     face_app.prepare(ctx_id=0, det_size=(640, 640))
#     swapper = get_model(MODEL_PATH)
#     # Removed swapper.prepare(ctx_id=0) as INSwapper does not have this method

# def read_image(file: UploadFile) -> np.ndarray:
#     try:
#         contents = file.file.read()
#         nparr = np.frombuffer(contents, np.uint8)
#         img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#         if img is None:
#             raise ValueError("Invalid image file.")
#         return img
#     finally:
#         file.file.close()

# def encode_image(img: np.ndarray) -> bytes:
#     _, buffer = cv2.imencode('.jpg', img)
#     return buffer.tobytes()

# def swap_faces(source_img: np.ndarray, target_img: np.ndarray) -> np.ndarray:
#     # Detect faces in both images
#     source_faces = face_app.get(source_img)
#     target_faces = face_app.get(target_img)

#     if len(source_faces) == 0:
#         raise ValueError("No face detected in the source image.")
#     if len(target_faces) == 0:
#         raise ValueError("No face detected in the target image.")

#     # For simplicity, we'll use the first detected face from the source
#     source_face = source_faces[0]

#     # Iterate over all detected faces in the target image and swap
#     for target_face in target_faces:
#         target_img = swapper.get(target_img, target_face, source_face, paste_back=True)

#     return target_img

# @app.post("/swap_faces/")
# async def swap_faces_endpoint(
#     source_image: UploadFile = File(..., description="Source image file (jpg, jpeg, png)."),
#     target_image: UploadFile = File(..., description="Target image file (jpg, jpeg, png).")
# ):
#     # Validate file extensions
#     allowed_extensions = {"jpg", "jpeg", "png"}
#     source_ext = source_image.filename.split(".")[-1].lower()
#     target_ext = target_image.filename.split(".")[-1].lower()

#     if source_ext not in allowed_extensions:
#         raise HTTPException(status_code=400, detail="Source image must be jpg, jpeg, or png.")
#     if target_ext not in allowed_extensions:
#         raise HTTPException(status_code=400, detail="Target image must be jpg, jpeg, or png.")

#     # Read images
#     try:
#         source_img = read_image(source_image)
#         target_img = read_image(target_image)
#     except ValueError as ve:
#         raise HTTPException(status_code=400, detail=str(ve))

#     # Perform face swap
#     try:
#         swapped_img = swap_faces(source_img, target_img)
#     except ValueError as ve:
#         raise HTTPException(status_code=400, detail=str(ve))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Face swapping failed: {str(e)}")

#     # Encode image to bytes
#     swapped_bytes = encode_image(swapped_img)

#     return StreamingResponse(
#         io.BytesIO(swapped_bytes),
#         media_type="image/jpeg",
#         headers={"Content-Disposition": "attachment; filename=swapped_result.jpg"}
#     )


# app.mount("/static", StaticFiles(directory="static"), name="static")

# # Serve the index.html at the root
# @app.get("/", response_class=FileResponse)
# def read_root():
#     return FileResponse("static/index.html")


import io
import os
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import numpy as np
import cv2
from insightface.app import FaceAnalysis
from insightface.model_zoo import get_model
import gdown  # For downloading the model from Google Drive

app = FastAPI(title="Face Swap API")

# Allow CORS (optional, adjust as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Google Drive file ID for the model
MODEL_DRIVE_FILE_ID = '13_ksjO8sNIqwdLx4x3VwaFmRK5P7Tjvz'
MODEL_PATH = "inswapper_128.onnx"  # Downloaded file name

# Function to download the model from Google Drive if not already present
def download_model():
    if not os.path.exists(MODEL_PATH):
        print("Downloading model from Google Drive...")
        url = f'https://drive.google.com/uc?id={MODEL_DRIVE_FILE_ID}'
        gdown.download(url, MODEL_PATH, quiet=False)
        print("Model downloaded successfully!")

# Initialize models globally to load them once
@app.on_event("startup")
def load_models():
    global face_app, swapper
    download_model()  # Ensure the model is downloaded before loading it
    face_app = FaceAnalysis(name='buffalo_l')
    face_app.prepare(ctx_id=0, det_size=(640, 640))
    swapper = get_model(MODEL_PATH)

def read_image(file: UploadFile) -> np.ndarray:
    try:
        contents = file.file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Invalid image file.")
        return img
    finally:
        file.file.close()

def encode_image(img: np.ndarray) -> bytes:
    _, buffer = cv2.imencode('.jpg', img)
    return buffer.tobytes()

def swap_faces(source_img: np.ndarray, target_img: np.ndarray) -> np.ndarray:
    # Detect faces in both images
    source_faces = face_app.get(source_img)
    target_faces = face_app.get(target_img)

    if len(source_faces) == 0:
        raise ValueError("No face detected in the source image.")
    if len(target_faces) == 0:
        raise ValueError("No face detected in the target image.")

    # For simplicity, we'll use the first detected face from the source
    source_face = source_faces[0]

    # Iterate over all detected faces in the target image and swap
    for target_face in target_faces:
        target_img = swapper.get(target_img, target_face, source_face, paste_back=True)

    return target_img

@app.post("/swap_faces/")
async def swap_faces_endpoint(
    source_image: UploadFile = File(..., description="Source image file (jpg, jpeg, png)."),
    target_image: UploadFile = File(..., description="Target image file (jpg, jpeg, png).")
):
    # Validate file extensions
    allowed_extensions = {"jpg", "jpeg", "png"}
    source_ext = source_image.filename.split(".")[-1].lower()
    target_ext = target_image.filename.split(".")[-1].lower()

    if source_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Source image must be jpg, jpeg, or png.")
    if target_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Target image must be jpg, jpeg, or png.")

    # Read images
    try:
        source_img = read_image(source_image)
        target_img = read_image(target_image)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    # Perform face swap
    try:
        swapped_img = swap_faces(source_img, target_img)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Face swapping failed: {str(e)}")

    # Encode image to bytes
    swapped_bytes = encode_image(swapped_img)

    return StreamingResponse(
        io.BytesIO(swapped_bytes),
        media_type="image/jpeg",
        headers={"Content-Disposition": "attachment; filename=swapped_result.jpg"}
    )

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve the index.html at the root
@app.get("/", response_class=FileResponse)
def read_root():
    return FileResponse("static/index.html")

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
