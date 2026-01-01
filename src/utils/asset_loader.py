"""
Asset loading utilities.
"""

from pathlib import Path

import pygame as pg

from ..config.paths import ASSETS_DIR


class AssetLoader:
    """
    Centralized asset loading with caching.

    Loads and caches images, sounds, and fonts to avoid
    redundant file I/O operations.
    """

    _instance: "AssetLoader | None" = None

    def __new__(cls) -> "AssetLoader":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_caches()
        return cls._instance

    def _init_caches(self) -> None:
        """Initialize asset caches."""
        self._images: dict[str, pg.Surface] = {}
        self._sounds: dict[str, pg.mixer.Sound] = {}
        self._fonts: dict[tuple[str | None, int], pg.font.Font] = {}

    def load_image(
        self, path: str | Path, convert_alpha: bool = True, scale: tuple[int, int] | None = None
    ) -> pg.Surface:
        """
        Load and cache an image.

        Args:
            path: Path relative to assets directory or absolute path.
            convert_alpha: Whether to convert with alpha channel.
            scale: Optional (width, height) to scale the image.

        Returns:
            Loaded pygame surface.
        """
        # Normalize path
        if not Path(path).is_absolute():
            path = ASSETS_DIR / path
        path = Path(path)

        cache_key = str(path)
        if scale:
            cache_key = f"{cache_key}_{scale[0]}x{scale[1]}"

        if cache_key not in self._images:
            img = pg.image.load(str(path))
            if convert_alpha:
                img = img.convert_alpha()
            else:
                img = img.convert()

            if scale:
                img = pg.transform.scale(img, scale)

            self._images[cache_key] = img

        return self._images[cache_key]

    def load_sound(self, path: str | Path) -> pg.mixer.Sound:
        """
        Load and cache a sound.

        Args:
            path: Path relative to assets directory or absolute path.

        Returns:
            Loaded pygame Sound object.
        """
        if not Path(path).is_absolute():
            path = ASSETS_DIR / path
        path = Path(path)

        cache_key = str(path)

        if cache_key not in self._sounds:
            self._sounds[cache_key] = pg.mixer.Sound(str(path))

        return self._sounds[cache_key]

    def get_font(self, name: str | None, size: int) -> pg.font.Font:
        """
        Get a font, cached.

        Args:
            name: Font name or None for default font.
            size: Font size.

        Returns:
            Pygame Font object.
        """
        cache_key = (name, size)

        if cache_key not in self._fonts:
            self._fonts[cache_key] = pg.font.Font(name, size)

        return self._fonts[cache_key]

    def clear_cache(self) -> None:
        """Clear all cached assets."""
        self._images.clear()
        self._sounds.clear()
        self._fonts.clear()

    @classmethod
    def get_instance(cls) -> "AssetLoader":
        """Get the singleton instance."""
        if cls._instance is None:
            return cls()
        return cls._instance
