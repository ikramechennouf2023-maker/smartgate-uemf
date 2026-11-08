"""
Étape 3 : détecter la plaque sur une photo de voiture, puis la découper.
"""
from ultralytics import YOLO


class PlateDetector:
    """Trouve la plaque d'immatriculation sur une image."""

    def __init__(self, weights="models/plate_detector.pt", conf=0.25):
        self.model = YOLO(weights)   # charge le modèle entraîné sur Colab
        self.conf = conf             # seuil : on ignore les détections < 25 %

    def detect(self, image):
        """
        image : une image OpenCV (tableau de pixels).
        Retourne ((x1, y1, x2, y2), confiance) pour la meilleure plaque,
        ou None si aucune plaque n'est trouvée.
        """
        result = self.model(image, conf=self.conf, verbose=False)[0]

        if len(result.boxes) == 0:          # aucune plaque trouvée
            return None

        best = int(result.boxes.conf.argmax())          # la détection la plus sûre
        x1, y1, x2, y2 = result.boxes.xyxy[best].tolist()
        confidence = float(result.boxes.conf[best])
        return (int(x1), int(y1), int(x2), int(y2)), confidence


def crop_plate(image, box, margin=0.05):
    """
    Découpe la plaque dans l'image.
    margin = 5 % de marge autour, pour ne pas couper le bord des caractères.
    """
    x1, y1, x2, y2 = box
    h, w = image.shape[:2]                 # hauteur et largeur de l'image

    mx = int((x2 - x1) * margin)           # marge horizontale
    my = int((y2 - y1) * margin)           # marge verticale

    # max(0, …) et min(w, …) : on ne sort pas de l'image
    x1, y1 = max(0, x1 - mx), max(0, y1 - my)
    x2, y2 = min(w, x2 + mx), min(h, y2 + my)

    return image[y1:y2, x1:x2]             # ⚠️ d'abord les lignes (y), puis les colonnes (x)