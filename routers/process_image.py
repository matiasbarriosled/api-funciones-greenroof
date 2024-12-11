from skimage import color, measure
from skimage.filters import threshold_otsu
from fastapi import APIRouter

router_proc_img = APIRouter()
@router_proc_img.post("/process_image")
def process_image(image, top_n=5):
    pixel_to_meter_ratio = 0.1
    
    try:
        gray_image = color.rgb2gray(image / 255.0)
        thresh = threshold_otsu(gray_image)
        binary_image = gray_image > thresh

        labeled_image = measure.label(binary_image)
        regions = measure.regionprops(labeled_image)

        filtered_regions = [
            region for region in regions
            if region.area > 100
        ]

        areas_table = sorted(
            [
                (idx, region, region.area * (pixel_to_meter_ratio ** 2))
                for idx, region in enumerate(filtered_regions, start=1)
            ],
            key=lambda x: x[2], reverse=True
        )

        return areas_table[:top_n], binary_image, filtered_regions
    except Exception as e:
        return None, None, None