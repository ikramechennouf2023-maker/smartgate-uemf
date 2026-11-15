import os
from roboflow import Roboflow

rf = Roboflow(api_key=os.environ["ROBOFLOW_API_KEY"])    # lit la clé dans le Terminal, pas dans le code
rf.workspace("midvi").project("arabic-license-plates").version(3).download(
    "yolov8", location="data/dataset_b"
)
print("✅ Dataset B dans data/dataset_b")