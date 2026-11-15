"""
Étape B : lire les caractères d'une plaque découpée avec le YOLO "caractères".
Renvoie la liste des caractères triés de gauche à droite + la confiance.
"""
import cv2
from ultralytics import YOLO


class PlateReader:

    def __init__(self, weights="models/char_reader.pt", conf=0.25):
        self.model = YOLO(weights)
        self.conf = conf

    def read(self, plate_img, etirer=True):
        if etirer:
            plate_img = cv2.resize(plate_img, (640, 640))   # comme les images d'entraînement (Roboflow)
        result = self.model(plate_img, conf=self.conf, verbose=False)[0]
        boites = []
        for box in result.boxes:
            x1, _, x2, _ = box.xyxy[0].tolist()
            boites.append({
                "centre": (x1 + x2) / 2,          # milieu horizontal du caractère
                "largeur": x2 - x1,
                "nom": result.names[int(box.cls)],
                "conf": float(box.conf),
            })

        boites = self._dedoublonner(boites)
        boites.sort(key=lambda b: b["centre"])    # de GAUCHE à DROITE

        caracteres = [b["nom"] for b in boites]
        confiance = min((b["conf"] for b in boites), default=0.0)
        return caracteres, confiance

    @staticmethod
    def _dedoublonner(boites):
        """
        Parfois YOLO met 2 réponses sur le MÊME caractère (ex. '1' à 0,80 et '7' à 0,40).
        Si deux boîtes sont presque au même endroit, on garde la plus sûre.
        """
        gardees = []
        for b in sorted(boites, key=lambda b: -b["conf"]):        # les plus sûres d'abord
            trop_proche = any(
                abs(b["centre"] - g["centre"]) < 0.5 * min(b["largeur"], g["largeur"])
                for g in gardees
            )
            if not trop_proche:
                gardees.append(b)
        return gardees