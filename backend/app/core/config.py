from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", protected_namespaces=()
    )

    database_url: str = "mysql+pymysql://gold:gold@localhost:3306/gold_predict"
    cors_origins: str = (
        "http://localhost:5173"  # nhiều địa chỉ: ngăn cách bằng dấu phẩy
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
    jwt_secret: str = ""
    access_token_expire_minutes: int = 1440

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
