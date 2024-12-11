from fastapi import FastAPI

from routers.load_mapics import router_mapics
from routers.arrange_figures import router_arr_fig
from routers.process_image import router_proc_img

app = FastAPI()
app.include_router(router_mapics)
app.include_router(router_arr_fig)
app.include_router(router_proc_img)