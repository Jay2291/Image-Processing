from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from typing import Annotated, Optional
import os
from PIL import Image

app = FastAPI()

storage_dir = "D:\\Chistats\\ImgMorph\\storage\\"
os.makedirs(storage_dir, exist_ok=True)

@app.post('/upload_img')
async def upload_img(files: list[UploadFile], crop: bool, rotate: bool, zoom: bool,
                    zoom_percent: Optional[int] = None,
                    rotate_angle: Optional[float] = None,
                    crop_left: Optional[float] = None, 
                    crop_top: Optional[float] = None, 
                    crop_right: Optional[float] = None, 
                    crop_bottom: Optional[float] = None
                    ):
    # cropped = None
    # rotated = None
    # zoomed = None
    imagesedit = {}
    for file in files:
        imgname = file.filename.split(".")
        img_path = storage_dir+f'{imgname[0]}\\'
        if not os.path.exists(img_path):
            os.makedirs(img_path)
        save_loc = os.path.join(img_path, file.filename)
        imageinfo={f"url":f"{imgname[0]}/{file.filename}"}
        with open(save_loc,'wb') as f:
            f.write(file.file.read())
        if crop:
            if crop_left and crop_top and crop_right and crop_bottom:
                cropped = crop_img(save_loc, (crop_left, crop_top, crop_right, crop_bottom))
                imageinfo.update({"cropped_url": f"{imgname[0]}/{os.path.basename(cropped)}"})
            else:
                return JSONResponse({"msg": "Crop values not given"})
        if rotate:
            if rotate_angle:
                rotated = roto_img(save_loc, rotate_angle)
                imageinfo.update({"rotate_url": f"{imgname[0]}/{os.path.basename(rotated)}"})
            else:
                return JSONResponse({"msg": "Rotate angle value not given"})
        if zoom:
            if zoom_percent:
                zoomed = zoomin_img(save_loc, zoom_percent)
                imageinfo.update({"zoom_url": f"{imgname[0]}/{os.path.basename(zoomed)}"})
            else:
                return JSONResponse({"msg": "Zoom percent value not given"})
        imagesedit.update({file.filename: imageinfo})
    return JSONResponse({"msg":imagesedit})

@app.get('/get_img')
async def get_img(filename: str):
    saved_loc = os.path.join(storage_dir, filename)
    if os.path.exists(saved_loc):
        return FileResponse(saved_loc)
    return JSONResponse({'msg':"File not found"})

def roto_img(img_path, angle):
    with Image.open(img_path) as img:
        w,h = img.size
        rot_img = img.rotate(angle, expand=True, center=(w,0))
        new_name = os.path.basename("rotated_"+os.path.basename(img_path))
        rotated_path = os.path.join(os.path.dirname(img_path), new_name)
        ver = 0
        while os.path.exists(rotated_path):
            ver += 1
            new_name = os.path.basename(f"rotated-v{ver}_"+os.path.basename(img_path))
            rotated_path = os.path.join(os.path.dirname(img_path), new_name)
        rot_img.save(rotated_path)
        return rotated_path

def crop_img(image_path, box):
    with Image.open(image_path) as img:
        cropped_img = img.crop(box)
        new_image_name = os.path.basename("cropped_"+os.path.basename(image_path))
        cropped_path = os.path.join(os.path.dirname(image_path), new_image_name)
        ver = 0
        while os.path.exists(cropped_path):
            ver += 1
            new_image_name = os.path.basename(f"cropped-v{ver}_"+os.path.basename(image_path))
            cropped_path = os.path.join(os.path.dirname(image_path), new_image_name)
        cropped_img.save(cropped_path)
        return cropped_path

def zoomin_img(image_path,zoom):
    with Image.open(image_path) as img:
        width, height = img.size
        zoom1 = zoom/100
        new_width = int(width * zoom1)
        new_height = int(height * zoom1)
        img_resized = img.resize((new_width, new_height), Image.LANCZOS)
        # left = (new_width - width) / 2
        # top = (new_height - height) / 2
        # right = (new_width + width) / 2
        # bottom = (new_height + height) / 2
        # img_cropped = img_resized.crop((left, top, right, bottom))
        new_image_name = os.path.basename("zoomed_" + os.path.basename(image_path))
        zoomed_path = os.path.join(os.path.dirname(image_path), new_image_name)
        ver = 0
        while os.path.exists(zoomed_path):
            ver += 1
            new_image_name = os.path.basename(f"zoomed-v{ver}_" + os.path.basename(image_path))
            zoomed_path = os.path.join(os.path.dirname(image_path), new_image_name)
        img_resized.save(zoomed_path)
        return zoomed_path