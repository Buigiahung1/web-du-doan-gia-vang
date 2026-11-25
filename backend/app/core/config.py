from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", protected_namespaces=()
    )

    database_url: str = "mysql+pymysql://gold:gold@localhost:3306/gold_predict"
    cors_origins: str = (
        "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5500,http://127.0.0.1:8000,http://localhost:8000,null"
    )
    model_dir: str = "../ml/artifacts"
    predictor_loader: str = "ml.src.predict:load_predictor"
    default_gold_type: str = "XAU_VND_LUONG"
    use_stub_model: bool = (
        False  # True: dùng model "ngày mai = hôm nay" khi TV6 chưa xong
    )
    predict_timeout_s: float = 10.0
    predict_rate_limit_per_min: int = 20
    inference_workers: int = 2
    cache_ttl_s: int = 120
    # Không có mặc định: phải đặt JWT_SECRET (>= 32 ký tự ngẫu nhiên) mới đăng nhập được.
    jwt_secret: str = ""
    jwt_secret_key: str = ""
    access_token_expire_minutes: int = 1440

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("DATABASE_URL không được để trống!")
        return v.strip()

    @field_validator("cors_origins")
    @classmethod
    def validate_cors_origins(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("CORS_ORIGINS không được để trống!")
        return v.strip()

    def model_post_init(self, __context) -> None:
        if not self.jwt_secret and self.jwt_secret_key:
            self.jwt_secret = self.jwt_secret_key
        elif not self.jwt_secret_key and self.jwt_secret:
            self.jwt_secret_key = self.jwt_secret

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
