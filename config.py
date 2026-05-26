import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    bot_token: str
    admin_id: int
    founder_username: str
    channel_url: str
    site_url: str


def get_settings() -> Settings:
    token = os.getenv("BOT_TOKEN", "").strip()
    admin_raw = os.getenv("ADMIN_ID", "").strip()

    if not token:
        raise RuntimeError("BOT_TOKEN не задан. Скопируйте .env.example → .env")
    if not admin_raw:
        raise RuntimeError("ADMIN_ID не задан. Узнайте свой ID у @userinfobot")

    return Settings(
        bot_token=token,
        admin_id=int(admin_raw),
        founder_username=os.getenv("FOUNDER_USERNAME", "rostg").strip().lstrip("@"),
        channel_url=os.getenv("CHANNEL_URL", "https://t.me/vnedrimai").strip(),
        site_url=os.getenv("SITE_URL", "https://rostgagarina-ops.github.io/vnedriai/").strip(),
    )
