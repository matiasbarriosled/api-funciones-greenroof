from fastapi import APIRouter

router_arr_fig = APIRouter()
@router_arr_fig.post("/arrange_figures")
def arrange_figures(region, rect_width, rect_height, pattern):
    pixel_to_meter_ratio = 0.1
    try:
        positions = []
        minr, minc, maxr, maxc = region.bbox
        if pattern == "H":
            group_positions = [
                (0, 0), (0, rect_height), (rect_width, rect_height),
                (2 * rect_width, 0), (2 * rect_width, rect_height)
            ]
        elif pattern == "L":
            group_positions = [
                (0, 0), (0, rect_height), (0, 2 * rect_height),
                (rect_width, 2 * rect_height)
            ]
        else:  # "Rectángulo simple"
            group_positions = [(0, 0)]

        for x, y in group_positions:
            pixel_x = int(x / pixel_to_meter_ratio) + minc
            pixel_y = int(y / pixel_to_meter_ratio) + minr
            positions.append((pixel_x, pixel_y))

        return positions
    except Exception as e:
        return []