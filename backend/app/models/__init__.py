# Nếu TV4 đã merge models chính thức thì dùng bản của TV4, bỏ các file bản tạm này.
from app.models.gold import GoldPrice, GoldType  # noqa: F401
from app.models.ml import MlModel  # noqa: F401
from app.models.prediction import Prediction, PredictionItem  # noqa: F401
from app.models.user import User  # noqa: F401
