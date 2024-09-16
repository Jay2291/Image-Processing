from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse ,FileResponse
from typing import Annotated, Optional
import cv2
import os

app = FastAPI()
dire = "D:\\Chistats\\ImgMorph\\imagescv\\"
os.makedirs(dire, exist_ok=True)

@app.post('/upload') 
async def upload_img(files: list[UploadFile], # Grayscale: bool = None,
                    Crop: bool = None, 
                    top_crop: Optional[int] = None,
                    left_crop: Optional[int] = None,
                    bottom_crop: Optional[int] = None,
                    right_crop: Optional[int] = None,
                    Zoom: bool= None, Zoom_Percent: Optional[float] = None,
                    Rotate: bool=None, Rotate_Angle: Optional[float] = None
                    ):
    imagesedited = {}
    for file in files:
        imgname = file.filename.split(".")
        img_dir = dire+f'{imgname[0]}\\'
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
        oneimage={f"url":f"{imgname[0]}/{file.filename}"}
        img_path = os.path.join(img_dir, file.filename)
        with open(img_path, 'wb') as f:
            f.write(file.file.read())
        run_no, run = run_fold(img_path)
        if Rotate:
            rotimg = rotating(img_path, run_no, Rotate_Angle)
            oneimage.update({"Rotate_url": f"{imgname[0]}/Run_{run}/{os.path.basename(rotimg)}"})
        if Zoom:
            zoimg = zooming(img_path, run_no, Zoom_Percent)
            oneimage.update({"Zoom_url": f"{imgname[0]}/Run_{run}/{os.path.basename(zoimg)}"})
        if Crop:
            crpimg = cropping(img_path, run_no, top_crop, left_crop, bottom_crop, right_crop)
            oneimage.update({"Crop_url": f"{imgname[0]}/Run_{run}/{os.path.basename(crpimg)}"})
        # if Grayscale:
        #     graimg = graying(img_path, run_no)
        #     oneimage.update({"Grayscale_url": f"{imgname[0]}/Run_{run}/{os.path.basename(graimg)}"})
        imagesedited.update({file.filename: oneimage})
    return JSONResponse({"msg":imagesedited})

@app.get('/get_img')
async def get_img(filename: str):
    saved_loc = os.path.join(dire, filename)
    if os.path.exists(saved_loc):
        return FileResponse(saved_loc)
    return JSONResponse({'msg':"File not found"})

def rotating(img_path, run_no, angle):
    img = cv2.imread(img_path)
    he, wi = img.shape[0:2]
    x, y = wi // 2, he // 2
    rotmat = cv2.getRotationMatrix2D((x, y), angle, .5)
    rotimg = cv2.warpAffine(img,rotmat, (wi,he))
    img_name = os.path.basename("rotated_"+os.path.basename(img_path))
    rotated_path = os.path.join(run_no, img_name)
    cv2.imwrite(rotated_path, rotimg)
    return rotated_path

def cropping(img_path, run_no, sr, sc, er, ec):
    img = cv2.imread(img_path)
    startRow = int(sr)
    startCol = int(sc)
    endRow = int(er)
    endCol = int(ec)
    crop = img[startRow:endRow, startCol:endCol]
    img_name = os.path.basename("cropped_"+os.path.basename(img_path))
    cropped_path = os.path.join(run_no, img_name)
    cv2.imwrite(cropped_path, crop)
    return img_name

def zooming(img_path, run_no, zoom_per):
    img = cv2.imread(img_path)
    z = zoom_per/100
    zoom =cv2.resize(img, (0,0), fx=z, fy=z)
    img_name = os.path.basename("zoomed_"+os.path.basename(img_path))
    zoomed_path = os.path.join(run_no, img_name)
    cv2.imwrite(zoomed_path, zoom)
    # cv2.imshow("img", rotimg)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return img_name

def graying(img_path, run_no):
    img = cv2.imread(img_path)
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_name = os.path.basename("grayscale_"+os.path.basename(img_path))
    gray_path = os.path.join(run_no, img_name)
    cv2.imwrite(gray_path, gray_img)
    return img_name

def run_fold(img_path):
    run = 0
    new_path = os.path.dirname(img_path)+f'\\Run_{run}\\'
    while os.path.exists(new_path):
        run += 1
        new_path = os.path.dirname(img_path)+f'\\Run_{run}\\'
    if not os.path.exists(new_path):
        os.makedirs(new_path)
    return new_path, run