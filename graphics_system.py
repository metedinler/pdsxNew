"""
Graphics and GUI System Module for PDSX Interpreter
QBasic-style grafik komutları ve terminal UI
"""

from typing import List, Any, Dict, Tuple
import time
import random
import os
import sys
from .base_command import BaseCommand, PDSXCommandError

try:
    import curses
    CURSES_AVAILABLE = True
except ImportError:
    CURSES_AVAILABLE = False


class GraphicsSystem(BaseCommand):
    """Grafik ve GUI komutları"""
    
    # Renk sabitleri
    COLORS = {
        "BLACK": 0,
        "BLUE": 1,
        "GREEN": 2,
        "CYAN": 3,
        "RED": 4,
        "MAGENTA": 5,
        "YELLOW": 6,
        "WHITE": 7,
        "BROWN": 8,  # YELLOW ile aynı
        "LIGHTGRAY": 9,
        "DARKGRAY": 10,
        "LIGHTBLUE": 11,
        "LIGHTGREEN": 12,
        "LIGHTCYAN": 13,
        "LIGHTRED": 14,
        "LIGHTMAGENTA": 15,
        "LIGHTYELLOW": 16,
        "BRIGHTWHITE": 17
    }
    
    def __init__(self, interpreter):
        super().__init__(interpreter)
        self.screen = None
        self.current_fg = "WHITE"
        self.current_bg = "BLACK"
        self.cursor_x = 0
        self.cursor_y = 0
        self.screen_width = 80
        self.screen_height = 25
        self.timer_start = time.time()
        self.color_pairs = {}
        self._pixel_buffer: Dict[Tuple[int, int], int] = {}
        self._legacy_image_sprite_ids: Dict[int, int] = {}
        
        # PHASE 1: Sprite Manager (24 Ekim 2025)
        from .graphics.sprite_manager import SpriteManager
        self.sprite_manager = SpriteManager()
        
        # PHASE 2: Font Manager + Text Renderer (24 Ekim 2025)
        from .graphics.font_manager import FontManager
        from .graphics.text_renderer import TextRenderer
        self.font_manager = FontManager()
        self.text_renderer = TextRenderer(self.font_manager)
        
        # PHASE 3: Z-Order + Collision Detection (24 Ekim 2025)
        from .graphics.z_order_manager import ZOrderManager
        from .graphics.collision_detector import CollisionDetector
        from .graphics.spatial_hash_grid import SpatialHashGrid
        self.z_order = ZOrderManager()
        self.collision_detector = CollisionDetector()
        self.spatial_grid = SpatialHashGrid(cell_size=64)
        
        # PHASE 4: Animation System (24 Ekim 2025)
        from .graphics.frame_animation_manager import FrameAnimationManager
        from .graphics.tween_system import TweenSystem
        from .graphics.timeline_manager import TimelineManager
        self.animation_manager = FrameAnimationManager()
        self.tween_system = TweenSystem()
        self.timeline_manager = TimelineManager()
        
        # PHASE 5: Advanced Rendering (24 Ekim 2025)
        from .graphics.camera_system import CameraSystem
        from .graphics.viewport_manager import ViewportManager
        from .graphics.render_layer_manager import RenderLayerManager
        from .graphics.post_processor import PostProcessor
        self.camera_system = CameraSystem()
        self.viewport_manager = ViewportManager()
        self.render_layer_manager = RenderLayerManager()
        self.post_processor = PostProcessor()
        
        # PHASE 6: Complete Game Engine (24 Ekim 2025)
        from .graphics.lighting_system import LightingSystem
        from .graphics.particle_system import ParticleSystem
        from .graphics.audio_system import AudioSystem
        from .graphics.physics_engine import PhysicsEngine
        self.lighting_system = LightingSystem()
        self.particle_system = ParticleSystem(max_particles=10000)
        self.audio_system = AudioSystem()
        self.physics_engine = PhysicsEngine(gravity=(0, 980))

    def _map_legacy_image_sprite_id(self, requested_id: int) -> int:
        if 129 <= requested_id <= 256:
            return requested_id

        if requested_id in self._legacy_image_sprite_ids:
            return self._legacy_image_sprite_ids[requested_id]

        used_internal_ids = set(self._legacy_image_sprite_ids.values())
        for candidate in range(129, 257):
            if candidate in used_internal_ids:
                continue
            if self.sprite_manager.get_sprite(candidate) is not None:
                continue
            self._legacy_image_sprite_ids[requested_id] = candidate
            return candidate

        raise PDSXCommandError("CREATE IMAGE SPRITE: uygun image sprite ID kalmadi (129-256)")

    def _set_variable(self, name: str, value: Any, context: Dict[str, Any] = None):
        if context is None:
            context = getattr(self.interpreter, 'context', {})
        if hasattr(self.interpreter, 'set_variable'):
            try:
                self.interpreter.set_variable(name, value)
                return
            except Exception:
                pass
        if 'global_vars' not in context:
            context['global_vars'] = {}
        context['global_vars'][name] = value

    def _get_variable(self, name: str, context: Dict[str, Any] = None, default: Any = None) -> Any:
        if context is None:
            context = getattr(self.interpreter, 'context', {})
        if hasattr(self.interpreter, 'get_variable'):
            try:
                return self.interpreter.get_variable(name)
            except Exception:
                pass
        if name in context.get('local_vars', {}):
            return context['local_vars'][name]
        if name in context.get('global_vars', {}):
            return context['global_vars'][name]
        if name in context.get('variables', {}):
            return context['variables'][name]
        return default

    def _read_key_nonblocking(self) -> str:
        if os.name == 'nt':
            try:
                import msvcrt
                if msvcrt.kbhit():
                    key = msvcrt.getwch()
                    if key == '\x00' or key == '\xe0':
                        special = msvcrt.getwch()
                        return f"SPECIAL:{ord(special)}"
                    return key
            except Exception:
                return ""
            return ""
        if CURSES_AVAILABLE and self.screen is not None:
            try:
                self.screen.nodelay(True)
                ch = self.screen.getch()
                if ch == -1:
                    return ""
                if 0 <= ch <= 255:
                    return chr(ch)
                return f"SPECIAL:{ch}"
            except Exception:
                return ""
        return ""

    def _read_key_blocking(self) -> str:
        if os.name == 'nt':
            try:
                import msvcrt
                key = msvcrt.getwch()
                if key == '\x00' or key == '\xe0':
                    special = msvcrt.getwch()
                    return f"SPECIAL:{ord(special)}"
                return key
            except Exception:
                pass
        if CURSES_AVAILABLE and self.screen is not None:
            try:
                self.screen.nodelay(False)
                ch = self.screen.getch()
                if 0 <= ch <= 255:
                    return chr(ch)
                return f"SPECIAL:{ch}"
            except Exception:
                pass
        value = input()
        return value[0] if value else ""

    def _split_csv_quoted(self, text: str) -> List[str]:
        parts = []
        current = []
        in_quotes = False
        quote_char = ''

        for char in text:
            if char in ('"', "'"):
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif quote_char == char:
                    in_quotes = False
                current.append(char)
            elif char == ',' and not in_quotes:
                token = ''.join(current).strip()
                if token:
                    parts.append(token)
                current = []
            else:
                current.append(char)

        tail = ''.join(current).strip()
        if tail:
            parts.append(tail)

        return parts

    def cmd_create_image_sprite_compat(self, args: List[str], context: Dict[str, Any] = None):
        """Compatibility: CREATE IMAGE SPRITE id, "file", x, y [AS IMAGE]"""
        if not args:
            raise PDSXCommandError("CREATE IMAGE SPRITE: arguman gerekli")

        raw = args[0].strip()
        raw_upper = raw.upper()
        if raw_upper.endswith(" AS IMAGE"):
            raw = raw[:-9].strip()

        parsed = self._split_csv_quoted(raw)
        if len(parsed) < 4:
            raise PDSXCommandError("CREATE IMAGE SPRITE: id, image, x, y gerekli")

        requested_id = int(self.evaluate_expression(parsed[0], context))
        internal_id = self._map_legacy_image_sprite_id(requested_id)
        mapped = parsed[:]
        mapped[0] = str(internal_id)
        self.cmd_sprite_load(mapped[:6], context)
        return requested_id

    def cmd_create_ascii_sprite_compat(self, args: List[str], context: Dict[str, Any] = None):
        """Compatibility: CREATE ASCII SPRITE id, x, y, "chars""" 
        if not args:
            raise PDSXCommandError("CREATE ASCII SPRITE: arguman gerekli")

        parsed = self._split_csv_quoted(args[0])
        if len(parsed) < 4:
            raise PDSXCommandError("CREATE ASCII SPRITE: id, x, y, chars gerekli")

        sprite_id = parsed[0]
        second = parsed[1].strip()
        third = parsed[2].strip()
        fourth = parsed[3].strip()

        second_is_chars = (
            (len(second) >= 2 and second[0] == second[-1] and second[0] in ('"', "'"))
            or (not second.replace('.', '', 1).lstrip('-').isdigit())
        )

        if second_is_chars:
            normalized = [sprite_id, third, fourth, second]
        else:
            normalized = [sprite_id, second, third, fourth]

        return self.cmd_sprite_create_ascii(normalized[:6], context)

    def cmd_draw_sprite_compat(self, args: List[str], context: Dict[str, Any] = None):
        """Compatibility: DRAW SPRITE id, "file" AT x, y"""
        if not args:
            raise PDSXCommandError("DRAW SPRITE: arguman gerekli")

        raw = args[0].strip()
        raw_upper = raw.upper()
        if ' AT ' not in raw_upper:
            raise PDSXCommandError("DRAW SPRITE: AT x, y bekleniyor")

        at_idx = raw_upper.find(' AT ')
        left = raw[:at_idx].strip()
        right = raw[at_idx + 4:].strip()

        left_parts = self._split_csv_quoted(left)
        right_parts = self._split_csv_quoted(right)

        if len(left_parts) < 1 or len(right_parts) < 2:
            raise PDSXCommandError("DRAW SPRITE: id ve x,y gerekli")

        requested_id = int(self.evaluate_expression(left_parts[0], context))
        sprite_id = self._legacy_image_sprite_ids.get(requested_id, requested_id)
        x = int(self.evaluate_expression(right_parts[0], context))
        y = int(self.evaluate_expression(right_parts[1], context))

        sprite = self.sprite_manager.get_sprite(sprite_id)
        if sprite is None:
            if len(left_parts) >= 2:
                image_path = str(self.evaluate_expression(left_parts[1], context)).strip('"\'')
                if requested_id != sprite_id:
                    target_id = sprite_id
                else:
                    target_id = self._map_legacy_image_sprite_id(requested_id)
                self.cmd_sprite_load([str(target_id), f'"{image_path}"', str(x), str(y)], context)
                self._legacy_image_sprite_ids[requested_id] = target_id
            else:
                raise PDSXCommandError(f"DRAW SPRITE: sprite bulunamadi ({requested_id})")
        else:
            sprite.x = x
            sprite.y = y
            sprite.visible = True

        return requested_id

    def cmd_collision_on(self, args: List[str], context: Dict[str, Any] = None):
        if context is None:
            context = getattr(self.interpreter, 'context', {})
        context['__collision_enabled__'] = True
        return True

    def cmd_collision_off(self, args: List[str], context: Dict[str, Any] = None):
        if context is None:
            context = getattr(self.interpreter, 'context', {})
        context['__collision_enabled__'] = False
        return False
    
    def _register_commands(self):
        """Grafik komutlarını kaydet"""
        # Renk komutları
        self.register_command("COLOR", self.cmd_color, "Set foreground/background color")
        self.register_command("BLACK", self.cmd_black, "Black color constant")
        self.register_command("BLUE", self.cmd_blue, "Blue color constant")
        self.register_command("GREEN", self.cmd_green, "Green color constant")
        self.register_command("CYAN", self.cmd_cyan, "Cyan color constant")
        self.register_command("RED", self.cmd_red, "Red color constant")
        self.register_command("MAGENTA", self.cmd_magenta, "Magenta color constant")
        self.register_command("YELLOW", self.cmd_yellow, "Yellow color constant")
        self.register_command("WHITE", self.cmd_white, "White color constant")
        self.register_command("BROWN", self.cmd_brown, "Brown color constant")
        self.register_command("LIGHTGRAY", self.cmd_lightgray, "Light gray constant")
        self.register_command("DARKGRAY", self.cmd_darkgray, "Dark gray constant")
        self.register_command("LIGHTBLUE", self.cmd_lightblue, "Light blue constant")
        self.register_command("LIGHTGREEN", self.cmd_lightgreen, "Light green constant")
        self.register_command("LIGHTCYAN", self.cmd_lightcyan, "Light cyan constant")
        self.register_command("LIGHTRED", self.cmd_lightred, "Light red constant")
        self.register_command("LIGHTMAGENTA", self.cmd_lightmagenta, "Light magenta constant")
        self.register_command("BRIGHTYELLOW", self.cmd_brightyellow, "Bright yellow constant")
        self.register_command("BRIGHTWHITE", self.cmd_brightwhite, "Bright white constant")
        
        # Ekran komutları
        self.register_command("SCREEN", self.cmd_screen, "Set screen mode")
        self.register_command("CLS", self.cmd_cls, "Clear screen")
        self.register_command("WIDTH", self.cmd_width, "Set screen width")
        self.register_command("LOCATE", self.cmd_locate, "Position cursor")
        self.register_command("CSRLIN", self.cmd_csrlin, "Get cursor line")
        self.register_command("POS", self.cmd_pos, "Get cursor column")
        self.register_command("VIEW", self.cmd_view, "Set viewport")
        self.register_command("WINDOW", self.cmd_window, "Set window coordinates")
        self.register_command("PALETTE", self.cmd_palette, "Set color palette")
        
        # Çizim komutları
        self.register_command("PSET", self.cmd_pset, "Set pixel")
        self.register_command("PRESET", self.cmd_preset, "Reset pixel")
        self.register_command("POINT", self.cmd_point, "Get pixel color")
        self.register_command("LINE", self.cmd_line, "Draw line")
        self.register_command("CIRCLE", self.cmd_circle, "Draw circle")
        self.register_command("ELLIPSE", self.cmd_ellipse, "Draw ellipse")
        self.register_command("ARC", self.cmd_arc, "Draw arc")
        self.register_command("BOX", self.cmd_box, "Draw box")
        self.register_command("RECT", self.cmd_rect, "Draw rectangle")
        self.register_command("PAINT", self.cmd_paint, "Fill area")
        self.register_command("GET_IMAGE", self.cmd_get_image, "Get screen region")
        self.register_command("PUT_IMAGE", self.cmd_put_image, "Put screen region")
        self.register_command("DRAW", self.cmd_draw, "Draw with string commands")
        
        # Sprite ve animasyon (Legacy - eski sistem)
        self.register_command("SPRITE", self.cmd_sprite, "Create sprite (legacy)")
        self.register_command("MOVESPRITE", self.cmd_movesprite, "Move sprite (legacy)")
        self.register_command("SHOWSPRITE", self.cmd_showsprite, "Show sprite (legacy)")
        self.register_command("HIDESPRITE", self.cmd_hidesprite, "Hide sprite (legacy)")

        # Legacy script compatibility bridge (multi-word syntax)
        self.register_command("CREATE_IMAGE_SPRITE", self.cmd_create_image_sprite_compat,
                    "Legacy syntax bridge", "CREATE IMAGE SPRITE id, \"file\", x, y [AS IMAGE]")
        self.register_command("CREATE_ASCII_SPRITE", self.cmd_create_ascii_sprite_compat,
                    "Legacy syntax bridge", "CREATE ASCII SPRITE id, x, y, \"chars\"")
        self.register_command("DRAW_SPRITE", self.cmd_draw_sprite_compat,
                    "Legacy syntax bridge", "DRAW SPRITE id, \"file\" AT x, y")
        self.register_command("COLLISION_ON", self.cmd_collision_on,
                    "Enable collision checks", "COLLISION ON")
        self.register_command("COLLISION_OFF", self.cmd_collision_off,
                    "Disable collision checks", "COLLISION OFF")
        
        # PHASE 1: Advanced Sprite Manager (24 Ekim 2025)
        # Note: Using single-word commands due to parser limitations
        
        # Syntax: SPRITEA sprite_id, x, y, chars [, layer] [, color]
        self.register_command("SPRITEA", self.cmd_sprite_create_ascii,
                            "Create ASCII sprite (ID: 1-128)",
                            "SPRITEA 1, 10, 10, \"@\"")
        
        # Syntax: SPRITEI sprite_id, image_path, x, y [, layer] [, scale]
        self.register_command("SPRITEI", self.cmd_sprite_load,
                            "Load image sprite (ID: 129-256)",
                            "SPRITEI 129, \"player.png\", 100, 100")
        
        # Syntax: SPRITEM sprite_id, dx, dy
        self.register_command("SPRITEM", self.cmd_sprite_move,
                            "Move sprite relatively",
                            "SPRITEM 1, 5, -3")
        
        # Syntax: SPRITEP sprite_id, x, y
        self.register_command("SPRITEP", self.cmd_sprite_position,
                            "Set sprite absolute position",
                            "SPRITEP 1, 100, 200")
        
        # Syntax: SPRITEV sprite_id, true/false
        self.register_command("SPRITEV", self.cmd_sprite_visible,
                            "Set sprite visibility",
                            "SPRITEV 1, TRUE")
        
        # Syntax: SPRITEL sprite_id, layer_value
        self.register_command("SPRITEL", self.cmd_sprite_layer,
                            "Set sprite z-order layer",
                            "SPRITEL 1, 10")
        
        # Syntax: SPRITED sprite_id
        self.register_command("SPRITED", self.cmd_sprite_destroy,
                            "Destroy sprite",
                            "SPRITED 1")
        
        # Syntax: SPRITEINF sprite_id
        self.register_command("SPRITEINF", self.cmd_sprite_info,
                            "Get sprite information",
                            "info = SPRITEINF 1")
        
        # Syntax: SPRITECNT [type]
        self.register_command("SPRITECNT", self.cmd_sprite_count,
                            "Get sprite count",
                            "count = SPRITECNT \"ASCII\"")
        
        # Syntax: SPRITECLR [type]
        self.register_command("SPRITECLR", self.cmd_sprite_clear,
                            "Clear sprites",
                            "SPRITECLR \"ALL\"")
        
        # PHASE 2: Font Manager Commands (24 Ekim 2025)
        
        # Syntax: FONTLOAD font_id, font_path, base_size
        self.register_command("FONTLOAD", self.cmd_font_load,
                            "Load TTF font (ID: 1-256)",
                            "FONTLOAD 1, \"arial.ttf\", 16")
        
        # Syntax: FONTSYS font_id, font_name, base_size
        self.register_command("FONTSYS", self.cmd_font_system,
                            "Load system font",
                            "FONTSYS 2, \"Arial\", 16")
        
        # Syntax: FONTFREE font_id
        self.register_command("FONTFREE", self.cmd_font_unload,
                            "Unload font",
                            "FONTFREE 1")
        
        # Syntax: TEXTDRAW font_id, x, y, text, size [, r, g, b]
        self.register_command("TEXTDRAW", self.cmd_text_draw,
                            "Draw text",
                            "TEXTDRAW 1, 100, 100, \"Hello\", 16")
        
        # Syntax: TEXTROT font_id, x, y, text, size, angle [, r, g, b]
        self.register_command("TEXTROT", self.cmd_text_rotated,
                            "Draw rotated text",
                            "TEXTROT 1, 100, 100, \"Hello\", 16, 45")
        
        # Syntax: TEXTMULTI font_id, x, y, text, size, line_spacing
        self.register_command("TEXTMULTI", self.cmd_text_multiline,
                            "Draw multi-line text",
                            "TEXTMULTI 1, 50, 50, \"Line1\\nLine2\", 14, 1.2")
        
        # Syntax: FONTINFO font_id
        self.register_command("FONTINFO", self.cmd_font_info,
                            "Get font information",
                            "info = FONTINFO 1")
        
        # Syntax: FONTCNT
        self.register_command("FONTCNT", self.cmd_font_count,
                            "Get loaded font count",
                            "count = FONTCNT")
        
        # PHASE 3: Collision Detection Commands (24 Ekim 2025)
        
        # Syntax: CAABB sprite_id1, sprite_id2
        self.register_command("CAABB", self.cmd_collision_aabb,
                            "Check AABB collision",
                            "collided = CAABB 1, 2")
        
        # Syntax: CCIRCLE sprite_id1, sprite_id2 [, radius1, radius2]
        self.register_command("CCIRCLE", self.cmd_collision_circle,
                            "Check circle collision",
                            "collided = CCIRCLE 1, 2")
        
        # Syntax: CPIXEL sprite_id1, sprite_id2
        self.register_command("CPIXEL", self.cmd_collision_pixel,
                            "Check pixel-perfect collision",
                            "collided = CPIXEL 129, 130")
        
        # Syntax: CPOINT sprite_id, x, y
        self.register_command("CPOINT", self.cmd_collision_point,
                            "Check point collision",
                            "hit = CPOINT 1, 100, 150")
        
        # Syntax: CLIST sprite_id, collision_type
        self.register_command("CLIST", self.cmd_collision_list,
                            "Check collision with all sprites",
                            "collisions = CLIST 1, \"AABB\"")
        
        # Syntax: SSORT [min_layer, max_layer]
        self.register_command("SSORT", self.cmd_sprite_sort,
                            "Get sorted sprite list by layer",
                            "sorted = SSORT")
        
        # Syntax: GINSERT sprite_id
        self.register_command("GINSERT", self.cmd_grid_insert,
                            "Insert sprite into spatial grid",
                            "GINSERT 1")
        
        # Syntax: GQUERY x, y, width, height
        self.register_command("GQUERY", self.cmd_grid_query,
                            "Query sprites in area",
                            "sprites = GQUERY 0, 0, 320, 240")
        
        # Syntax: GNEARBY sprite_id
        self.register_command("GNEARBY", self.cmd_grid_nearby,
                            "Get nearby sprites from grid",
                            "nearby = GNEARBY 1")
        
        # Zaman ve timer
        self.register_command("TIMER", self.cmd_timer, "Get elapsed time")
        self.register_command("SLEEP", self.cmd_sleep, "Sleep for seconds")
        self.register_command("WAIT", self.cmd_wait, "Wait for condition")
        
        # Klavye ve fare
        self.register_command("INKEY", self.cmd_inkey, "Get keyboard input")
        self.register_command("INPUT", self.cmd_input, "Get user input")
        self.register_command("GETKEY", self.cmd_getkey, "Wait for keypress")
        self.register_command("KBHIT", self.cmd_kbhit, "Check keyboard hit")
        
        # Bitwise operatörler
        self.register_command("SHL", self.cmd_shl, "Shift left")
        self.register_command("SHR", self.cmd_shr, "Shift right")
        self.register_command("AND", self.cmd_and, "Bitwise AND")
        self.register_command("OR", self.cmd_or, "Bitwise OR")
        self.register_command("XOR", self.cmd_xor, "Bitwise XOR")
        self.register_command("NOT", self.cmd_not, "Bitwise NOT")
        self.register_command("BITFIELD", self.cmd_bitfield, "Extract bit field")
        self.register_command("SETBIT", self.cmd_setbit, "Set bit")
        self.register_command("CLRBIT", self.cmd_clrbit, "Clear bit")
        self.register_command("TESTBIT", self.cmd_testbit, "Test bit")
        
        # RGBA ve renk manipülasyonu
        self.register_command("RGBA", self.cmd_rgba, "Create RGBA color")
        self.register_command("RGB", self.cmd_rgb, "Create RGB color")
        self.register_command("GETR", self.cmd_getr, "Get red component")
        self.register_command("GETG", self.cmd_getg, "Get green component")
        self.register_command("GETB", self.cmd_getb, "Get blue component")
        self.register_command("GETA", self.cmd_geta, "Get alpha component")
        
        # Hizalama ve pozisyon
        self.register_command("ALIGN", self.cmd_align, "Align value to boundary")
        self.register_command("CLAMP", self.cmd_clamp, "Clamp value to range")
        self.register_command("LERP", self.cmd_lerp, "Linear interpolation")
        
        # PHASE 5: Advanced Rendering Commands (24 Ekim 2025)
        
        # Camera commands
        self.register_command("CAMCREATE", self.cmd_camera_create,
                            "Create camera",
                            "cam = CAMCREATE 0, 0, 1.0, 800, 600")
        self.register_command("CAMPOS", self.cmd_camera_position,
                            "Set camera position",
                            "CAMPOS 1, 100, 200")
        self.register_command("CAMZOOM", self.cmd_camera_zoom,
                            "Set camera zoom",
                            "CAMZOOM 1, 2.0")
        self.register_command("CAMFOLLOW", self.cmd_camera_follow,
                            "Camera follow sprite",
                            "CAMFOLLOW 1, 5, 3.0, 0, 0")
        self.register_command("CAMSHAKE", self.cmd_camera_shake,
                            "Camera shake effect",
                            "CAMSHAKE 1, 10.0, 0.5")
        
        # Viewport commands
        self.register_command("VIEWPORT", self.cmd_viewport_create,
                            "Create viewport",
                            "vp = VIEWPORT 0, 0, 400, 600, 1")
        self.register_command("VIEWCAM", self.cmd_viewport_camera,
                            "Set viewport camera",
                            "VIEWCAM 1, 2")
        self.register_command("VIEWACTIVE", self.cmd_viewport_active,
                            "Set viewport active",
                            "VIEWACTIVE 1, 1")
        
        # Render layer commands
        self.register_command("LAYERCREATE", self.cmd_layer_create,
                            "Create render layer",
                            "layer = LAYERCREATE \"bg\", 0, \"normal\", 1.0")
        self.register_command("LAYERADD", self.cmd_layer_add_sprite,
                            "Add sprite to layer",
                            "LAYERADD 1, 5")
        self.register_command("LAYERVIS", self.cmd_layer_visibility,
                            "Set layer visibility",
                            "LAYERVIS 1, 0")
        self.register_command("LAYEROPACITY", self.cmd_layer_opacity,
                            "Set layer opacity",
                            "LAYEROPACITY 1, 0.5")
        
        # Post-processing commands
        self.register_command("EFFECTADD", self.cmd_effect_add,
                            "Add post-processing effect",
                            "effect = EFFECTADD \"blur\", 0.5")
        self.register_command("EFFECTSET", self.cmd_effect_set,
                            "Set effect parameter",
                            "EFFECTSET 1, \"radius\", 5")
        self.register_command("EFFECTCLEAR", self.cmd_effect_clear,
                            "Clear all effects",
                            "EFFECTCLEAR")
        
        # PHASE 6: Complete Game Engine Commands (24 Ekim 2025)
        
        # Lighting commands
        self.register_command("LIGHTPOINT", self.cmd_light_point,
                            "Add point light",
                            "light = LIGHTPOINT 100, 150, 255, 200, 100, 1.0, 200")
        self.register_command("LIGHTDIR", self.cmd_light_directional,
                            "Add directional light",
                            "sun = LIGHTDIR 45, 255, 240, 220, 0.8")
        self.register_command("LIGHTSPOT", self.cmd_light_spotlight,
                            "Add spotlight",
                            "spot = LIGHTSPOT 200, 100, 90, 30, 255, 255, 255, 1.0, 300")
        self.register_command("LIGHTPOS", self.cmd_light_position,
                            "Set light position",
                            "LIGHTPOS light, 150, 200")
        self.register_command("LIGHTCOLOR", self.cmd_light_color,
                            "Set light color",
                            "LIGHTCOLOR light, 255, 100, 50")
        self.register_command("AMBIENT", self.cmd_ambient_light,
                            "Set ambient light",
                            "AMBIENT 30, 30, 40, 0.3")
        
        # Particle commands
        self.register_command("PEMIT", self.cmd_particle_emitter,
                            "Create particle emitter",
                            "emitter = PEMIT 100, 200, 50")
        self.register_command("PPRESET", self.cmd_particle_preset,
                            "Create preset emitter",
                            "fire = PPRESET \"fire\", 100, 200")
        self.register_command("PBURST", self.cmd_particle_burst,
                            "Emit particle burst",
                            "PBURST emitter, 100")
        self.register_command("PUPDATE", self.cmd_particle_update,
                            "Update particle system",
                            "PUPDATE 0.016")
        
        # Audio commands
        self.register_command("SOUNDLOAD", self.cmd_sound_load,
                            "Load sound effect",
                            "sfx = SOUNDLOAD \"explosion.wav\"")
        self.register_command("SOUNDPLAY", self.cmd_sound_play,
                            "Play sound",
                            "SOUNDPLAY sfx, 0.8")
        self.register_command("SOUNDPLAY3D", self.cmd_sound_play_3d,
                            "Play 3D sound",
                            "SOUNDPLAY3D sfx, 100, 200, 1.0")
        self.register_command("MUSICLOAD", self.cmd_music_load,
                            "Load music",
                            "MUSICLOAD \"background.mp3\"")
        self.register_command("MUSICPLAY", self.cmd_music_play,
                            "Play music",
                            "MUSICPLAY 1, 2.0")
        self.register_command("VOLUME", self.cmd_volume,
                            "Set volume",
                            "VOLUME \"master\", 0.7")
        
        # Physics commands
        self.register_command("BODYCREATE", self.cmd_body_create,
                            "Create rigid body",
                            "body = BODYCREATE sprite, \"dynamic\", 100, 200")
        self.register_command("BODYFORCE", self.cmd_body_force,
                            "Apply force",
                            "BODYFORCE body, 500, 0")
        self.register_command("BODYIMPULSE", self.cmd_body_impulse,
                            "Apply impulse",
                            "BODYIMPULSE body, 100, -200")
        self.register_command("BODYVEL", self.cmd_body_velocity,
                            "Set velocity",
                            "BODYVEL body, 50, 0")
        self.register_command("PHYSSTEP", self.cmd_physics_step,
                            "Update physics",
                            "PHYSSTEP 0.016")
    
    # ========== Renk Sabitleri ==========
    
    def cmd_black(self, args: List[str], context: Dict[str, Any] = None):
        """BLACK renk sabiti: 0"""
        return self.COLORS["BLACK"]
    
    def cmd_blue(self, args: List[str], context: Dict[str, Any] = None):
        """BLUE renk sabiti: 1"""
        return self.COLORS["BLUE"]
    
    def cmd_green(self, args: List[str], context: Dict[str, Any] = None):
        """GREEN renk sabiti: 2"""
        return self.COLORS["GREEN"]
    
    def cmd_cyan(self, args: List[str], context: Dict[str, Any] = None):
        """CYAN renk sabiti: 3"""
        return self.COLORS["CYAN"]
    
    def cmd_red(self, args: List[str], context: Dict[str, Any] = None):
        """RED renk sabiti: 4"""
        return self.COLORS["RED"]
    
    def cmd_magenta(self, args: List[str], context: Dict[str, Any] = None):
        """MAGENTA renk sabiti: 5"""
        return self.COLORS["MAGENTA"]
    
    def cmd_yellow(self, args: List[str], context: Dict[str, Any] = None):
        """YELLOW renk sabiti: 6"""
        return self.COLORS["YELLOW"]
    
    def cmd_white(self, args: List[str], context: Dict[str, Any] = None):
        """WHITE renk sabiti: 7"""
        return self.COLORS["WHITE"]
    
    def cmd_brown(self, args: List[str], context: Dict[str, Any] = None):
        """BROWN renk sabiti: 8 (YELLOW)"""
        return self.COLORS["BROWN"]
    
    def cmd_lightgray(self, args: List[str], context: Dict[str, Any] = None):
        """LIGHTGRAY renk sabiti: 9"""
        return self.COLORS["LIGHTGRAY"]
    
    def cmd_darkgray(self, args: List[str], context: Dict[str, Any] = None):
        """DARKGRAY renk sabiti: 10"""
        return self.COLORS["DARKGRAY"]
    
    def cmd_lightblue(self, args: List[str], context: Dict[str, Any] = None):
        """LIGHTBLUE renk sabiti: 11"""
        return self.COLORS["LIGHTBLUE"]
    
    def cmd_lightgreen(self, args: List[str], context: Dict[str, Any] = None):
        """LIGHTGREEN renk sabiti: 12"""
        return self.COLORS["LIGHTGREEN"]
    
    def cmd_lightcyan(self, args: List[str], context: Dict[str, Any] = None):
        """LIGHTCYAN renk sabiti: 13"""
        return self.COLORS["LIGHTCYAN"]
    
    def cmd_lightred(self, args: List[str], context: Dict[str, Any] = None):
        """LIGHTRED renk sabiti: 14"""
        return self.COLORS["LIGHTRED"]
    
    def cmd_lightmagenta(self, args: List[str], context: Dict[str, Any] = None):
        """LIGHTMAGENTA renk sabiti: 15"""
        return self.COLORS["LIGHTMAGENTA"]
    
    def cmd_brightyellow(self, args: List[str], context: Dict[str, Any] = None):
        """BRIGHTYELLOW renk sabiti: 16"""
        return self.COLORS["LIGHTYELLOW"]
    
    def cmd_brightwhite(self, args: List[str], context: Dict[str, Any] = None):
        """BRIGHTWHITE renk sabiti: 17"""
        return self.COLORS["BRIGHTWHITE"]
    
    # ========== Ekran Komutları ==========
    
    def cmd_color(self, args: List[str], context: Dict[str, Any] = None):
        """Renk ayarla: COLOR fg [bg]"""
        if len(args) < 1:
            raise PDSXCommandError("COLOR fg [bg] gerekli")
        
        fg = int(args[0])
        bg = int(args[1]) if len(args) > 1 else None
        
        self.current_fg = self._color_num_to_name(fg)
        if bg is not None:
            self.current_bg = self._color_num_to_name(bg)
        
        return f"COLOR {fg}, {bg}"
    
    def cmd_screen(self, args: List[str], context: Dict[str, Any] = None):
        """Ekran modu: SCREEN mode"""
        if len(args) < 1:
            raise PDSXCommandError("SCREEN mode gerekli")
        
        mode = int(args[0])
        
        if mode == 0:
            self.screen_width = 80
            self.screen_height = 25
        elif mode == 1:
            self.screen_width = 40
            self.screen_height = 25
        elif mode == 2:
            self.screen_width = 80
            self.screen_height = 25
        elif mode == 7:
            self.screen_width = 320
            self.screen_height = 200
        elif mode == 13:
            self.screen_width = 640
            self.screen_height = 480
        
        return f"SCREEN {mode} ({self.screen_width}x{self.screen_height})"
    
    def cmd_cls(self, args: List[str], context: Dict[str, Any] = None):
        """Ekranı temizle: CLS"""
        self.cursor_x = 0
        self.cursor_y = 0
        return "CLS"
    
    def cmd_width(self, args: List[str], context: Dict[str, Any] = None):
        """Ekran genişliği: WIDTH columns [rows]"""
        if len(args) < 1:
            return self.screen_width
        
        self.screen_width = int(args[0])
        if len(args) > 1:
            self.screen_height = int(args[1])
        
        return f"WIDTH {self.screen_width}, {self.screen_height}"
    
    def cmd_locate(self, args: List[str], context: Dict[str, Any] = None):
        """İmleç konumu: LOCATE row [col]"""
        if len(args) < 1:
            raise PDSXCommandError("LOCATE row [col] gerekli")
        
        self.cursor_y = int(args[0]) - 1  # 1-based to 0-based
        if len(args) > 1:
            self.cursor_x = int(args[1]) - 1
        
        return f"LOCATE {self.cursor_y + 1}, {self.cursor_x + 1}"
    
    def cmd_csrlin(self, args: List[str], context: Dict[str, Any] = None):
        """İmleç satırı: CSRLIN"""
        return self.cursor_y + 1  # 0-based to 1-based
    
    def cmd_pos(self, args: List[str], context: Dict[str, Any] = None):
        """İmleç sütunu: POS(0)"""
        return self.cursor_x + 1  # 0-based to 1-based
    
    def cmd_view(self, args: List[str], context: Dict[str, Any] = None):
        """Viewport: VIEW [x1, y1, x2, y2]"""
        if len(args) < 4:
            return "VIEW RESET"
        
        x1, y1, x2, y2 = map(int, args[:4])
        return f"VIEW ({x1}, {y1})-({x2}, {y2})"
    
    def cmd_window(self, args: List[str], context: Dict[str, Any] = None):
        """Window koordinatları: WINDOW [x1, y1, x2, y2]"""
        if len(args) < 4:
            return "WINDOW RESET"
        
        x1, y1, x2, y2 = map(float, args[:4])
        return f"WINDOW ({x1}, {y1})-({x2}, {y2})"
    
    def cmd_palette(self, args: List[str], context: Dict[str, Any] = None):
        """Palet ayarla: PALETTE color, value"""
        if len(args) < 2:
            raise PDSXCommandError("PALETTE color, value gerekli")
        
        color = int(args[0])
        value = int(args[1])
        return f"PALETTE {color}, {value}"
    
    # ========== Çizim Komutları ==========
    
    def cmd_pset(self, args: List[str], context: Dict[str, Any] = None):
        """Piksel ayarla: PSET (x, y) [color]"""
        if len(args) < 2:
            raise PDSXCommandError("PSET (x, y) [color] gerekli")
        
        x = int(args[0])
        y = int(args[1])
        color = int(args[2]) if len(args) > 2 else None
        self._pixel_buffer[(x, y)] = 0 if color is None else color
        return f"PSET ({x}, {y}), {color}"
    
    def cmd_preset(self, args: List[str], context: Dict[str, Any] = None):
        """Piksel sıfırla: PRESET (x, y)"""
        if len(args) < 2:
            raise PDSXCommandError("PRESET (x, y) gerekli")
        
        x = int(args[0])
        y = int(args[1])
        self._pixel_buffer[(x, y)] = 0
        return f"PRESET ({x}, {y})"
    
    def cmd_point(self, args: List[str], context: Dict[str, Any] = None):
        """Piksel oku: POINT (x, y)"""
        if len(args) < 2:
            raise PDSXCommandError("POINT (x, y) gerekli")
        
        x = int(args[0])
        y = int(args[1])
        return self._pixel_buffer.get((x, y), 0)
    
    def cmd_line(self, args: List[str], context: Dict[str, Any] = None):
        """Çizgi çiz: LINE (x1, y1)-(x2, y2) [color] [B/BF]"""
        if len(args) < 4:
            raise PDSXCommandError("LINE (x1, y1)-(x2, y2) gerekli")
        
        x1, y1, x2, y2 = map(int, args[:4])
        color = int(args[4]) if len(args) > 4 else None
        style = args[5] if len(args) > 5 else None
        
        return f"LINE ({x1}, {y1})-({x2}, {y2}), {color}, {style}"
    
    def cmd_circle(self, args: List[str], context: Dict[str, Any] = None):
        """Daire çiz: CIRCLE (x, y), radius [color]"""
        if len(args) < 3:
            raise PDSXCommandError("CIRCLE (x, y), radius gerekli")
        
        x = int(args[0])
        y = int(args[1])
        radius = float(args[2])
        color = int(args[3]) if len(args) > 3 else None
        
        return f"CIRCLE ({x}, {y}), {radius}, {color}"
    
    def cmd_ellipse(self, args: List[str], context: Dict[str, Any] = None):
        """Elips çiz: ELLIPSE (x, y), rx, ry [color]"""
        if len(args) < 4:
            raise PDSXCommandError("ELLIPSE (x, y), rx, ry gerekli")
        
        x, y = int(args[0]), int(args[1])
        rx, ry = float(args[2]), float(args[3])
        color = int(args[4]) if len(args) > 4 else None
        
        return f"ELLIPSE ({x}, {y}), {rx}, {ry}, {color}"
    
    def cmd_arc(self, args: List[str], context: Dict[str, Any] = None):
        """Yay çiz: ARC (x, y), radius, start, end [color]"""
        if len(args) < 5:
            raise PDSXCommandError("ARC (x, y), radius, start, end gerekli")
        
        x, y = int(args[0]), int(args[1])
        radius = float(args[2])
        start, end = float(args[3]), float(args[4])
        color = int(args[5]) if len(args) > 5 else None
        
        return f"ARC ({x}, {y}), {radius}, {start}, {end}, {color}"
    
    def cmd_box(self, args: List[str], context: Dict[str, Any] = None):
        """Kutu çiz: BOX (x, y, width, height) [color] [fill]"""
        if len(args) < 4:
            raise PDSXCommandError("BOX (x, y, width, height) gerekli")
        
        x, y = int(args[0]), int(args[1])
        width, height = int(args[2]), int(args[3])
        color = int(args[4]) if len(args) > 4 else None
        fill = bool(int(args[5])) if len(args) > 5 else False
        
        return f"BOX ({x}, {y}, {width}, {height}), {color}, {fill}"
    
    def cmd_rect(self, args: List[str], context: Dict[str, Any] = None):
        """Dikdörtgen: RECT (x1, y1, x2, y2) [color] [fill]"""
        if len(args) < 4:
            raise PDSXCommandError("RECT (x1, y1, x2, y2) gerekli")
        
        x1, y1, x2, y2 = map(int, args[:4])
        color = int(args[4]) if len(args) > 4 else None
        fill = bool(int(args[5])) if len(args) > 5 else False
        
        return f"RECT ({x1}, {y1}, {x2}, {y2}), {color}, {fill}"
    
    def cmd_paint(self, args: List[str], context: Dict[str, Any] = None):
        """Doldur: PAINT (x, y) [color] [border]"""
        if len(args) < 2:
            raise PDSXCommandError("PAINT (x, y) gerekli")
        
        x, y = int(args[0]), int(args[1])
        color = int(args[2]) if len(args) > 2 else None
        border = int(args[3]) if len(args) > 3 else None
        
        return f"PAINT ({x}, {y}), {color}, {border}"
    
    def cmd_get_image(self, args: List[str], context: Dict[str, Any] = None):
        """Görüntü al: GET (x1, y1)-(x2, y2), array"""
        if len(args) < 5:
            raise PDSXCommandError("GET (x1, y1)-(x2, y2), array gerekli")
        
        x1, y1, x2, y2 = map(int, args[:4])
        array_name = args[4]

        width = max(0, x2 - x1)
        height = max(0, y2 - y1)
        image_data = []
        for row in range(height):
            line = []
            for col in range(width):
                px = x1 + col
                py = y1 + row
                line.append(self._pixel_buffer.get((px, py), 0))
            image_data.append(line)
        self._set_variable(array_name, image_data, context)
        
        return f"GET ({x1}, {y1})-({x2}, {y2}), {array_name}"
    
    def cmd_put_image(self, args: List[str], context: Dict[str, Any] = None):
        """Görüntü koy: PUT (x, y), array [action]"""
        if len(args) < 3:
            raise PDSXCommandError("PUT (x, y), array gerekli")
        
        x, y = int(args[0]), int(args[1])
        array_name = args[2]
        action = args[3] if len(args) > 3 else "PSET"

        image_data = self._get_variable(array_name, context)
        if isinstance(image_data, list):
            for row_index, row in enumerate(image_data):
                if not isinstance(row, list):
                    continue
                for col_index, value in enumerate(row):
                    target_x = x + col_index
                    target_y = y + row_index
                    if action.upper() == "PRESET":
                        self._pixel_buffer[(target_x, target_y)] = 0
                    else:
                        try:
                            self._pixel_buffer[(target_x, target_y)] = int(value)
                        except Exception:
                            self._pixel_buffer[(target_x, target_y)] = 0
        return f"PUT ({x}, {y}), {array_name}, {action}"
    
    def cmd_draw(self, args: List[str], context: Dict[str, Any] = None):
        """DRAW komutu: DRAW command_string"""
        if len(args) < 1:
            raise PDSXCommandError("DRAW command_string gerekli")
        
        command = ' '.join(args)
        return f"DRAW {command}"
    
    # ========== Sprite Komutları ==========
    
    def cmd_sprite(self, args: List[str], context: Dict[str, Any] = None):
        """Sprite oluştur: SPRITE name width height"""
        if len(args) < 3:
            raise PDSXCommandError("SPRITE name width height gerekli")
        
        name = args[0]
        width = int(args[1])
        height = int(args[2])
        
        sprite_data = {
            'width': width,
            'height': height,
            'x': 0,
            'y': 0,
            'visible': True,
            'pixels': [[' ' for _ in range(width)] for _ in range(height)]
        }
        
        self._set_variable(f"SPRITE_{name}", sprite_data, context)
        return f"SPRITE {name} ({width}x{height})"
    
    def cmd_movesprite(self, args: List[str], context: Dict[str, Any] = None):
        """Sprite taşı: MOVESPRITE name x y"""
        if len(args) < 3:
            raise PDSXCommandError("MOVESPRITE name x y gerekli")
        
        name = args[0]
        x = int(args[1])
        y = int(args[2])
        
        sprite = self._get_variable(f"SPRITE_{name}", context)
        if not isinstance(sprite, dict):
            raise PDSXCommandError(f"Sprite bulunamadi: {name}")
        sprite['x'] = x
        sprite['y'] = y
        
        return f"MOVESPRITE {name} to ({x}, {y})"
    
    def cmd_showsprite(self, args: List[str], context: Dict[str, Any] = None):
        """Sprite göster: SHOWSPRITE name"""
        if len(args) < 1:
            raise PDSXCommandError("SHOWSPRITE name gerekli")
        
        name = args[0]
        sprite = self._get_variable(f"SPRITE_{name}", context)
        if not isinstance(sprite, dict):
            raise PDSXCommandError(f"Sprite bulunamadi: {name}")
        sprite['visible'] = True
        
        return f"SHOWSPRITE {name}"
    
    def cmd_hidesprite(self, args: List[str], context: Dict[str, Any] = None):
        """Sprite gizle: HIDESPRITE name"""
        if len(args) < 1:
            raise PDSXCommandError("HIDESPRITE name gerekli")
        
        name = args[0]
        sprite = self._get_variable(f"SPRITE_{name}", context)
        if not isinstance(sprite, dict):
            raise PDSXCommandError(f"Sprite bulunamadi: {name}")
        sprite['visible'] = False
        
        return f"HIDESPRITE {name}"
    
    # ========== Zaman Komutları ==========
    
    def cmd_timer(self, args: List[str], context: Dict[str, Any] = None):
        """Zamanlayıcı: TIMER"""
        elapsed = time.time() - self.timer_start
        return elapsed
    
    def cmd_sleep(self, args: List[str], context: Dict[str, Any] = None):
        """Uyku: SLEEP seconds"""
        if len(args) < 1:
            raise PDSXCommandError("SLEEP seconds gerekli")
        
        seconds = float(args[0])
        time.sleep(seconds)
        return f"SLEEP {seconds}"
    
    def cmd_wait(self, args: List[str], context: Dict[str, Any] = None):
        """Bekle: WAIT port, and_mask [xor_mask]"""
        if len(args) < 2:
            raise PDSXCommandError("WAIT port, and_mask gerekli")
        
        port = int(args[0])
        and_mask = int(args[1])
        xor_mask = int(args[2]) if len(args) > 2 else 0

        if context is None:
            context = getattr(self.interpreter, 'context', {})

        start = time.time()
        timeout_s = 1.0
        while True:
            ports = context.get('__ports__', {})
            port_value = int(ports.get(port, 0)) if isinstance(ports, dict) else 0
            condition = (port_value & and_mask) ^ xor_mask
            if condition != 0:
                return port_value
            if time.time() - start >= timeout_s:
                return port_value
            time.sleep(0.01)
    
    # ========== Klavye Komutları ==========
    
    def cmd_inkey(self, args: List[str], context: Dict[str, Any] = None):
        """Tuş oku: INKEY$"""
        key = self._read_key_nonblocking()
        return key if key else ""
    
    def cmd_input(self, args: List[str], context: Dict[str, Any] = None):
        """Girdi al: INPUT [prompt] variable"""
        if len(args) < 1:
            raise PDSXCommandError("INPUT variable gerekli")
        
        if len(args) > 1:
            prompt = args[0]
            var_name = args[1]
        else:
            prompt = ""
            var_name = args[0]
        
        value = input(prompt)
        
        # Tip dönüşümü
        try:
            value = int(value)
        except ValueError:
            try:
                value = float(value)
            except ValueError:
                pass
        
        self._set_variable(var_name, value, context)
        return value
    
    def cmd_getkey(self, args: List[str], context: Dict[str, Any] = None):
        """Tuş bekle: GETKEY"""
        return self._read_key_blocking()
    
    def cmd_kbhit(self, args: List[str], context: Dict[str, Any] = None):
        """Klavye kontrol: KBHIT"""
        key = self._read_key_nonblocking()
        if key and context is not None:
            context['__last_key__'] = key
        return 1 if key else 0
    
    # ========== Bitwise Operatörler ==========
    
    def cmd_shl(self, args: List[str], context: Dict[str, Any] = None):
        """Sola kaydır: SHL value, shift"""
        if len(args) < 2:
            raise PDSXCommandError("SHL value, shift gerekli")
        
        value = int(args[0])
        shift = int(args[1])
        return value << shift
    
    def cmd_shr(self, args: List[str], context: Dict[str, Any] = None):
        """Sağa kaydır: SHR value, shift"""
        if len(args) < 2:
            raise PDSXCommandError("SHR value, shift gerekli")
        
        value = int(args[0])
        shift = int(args[1])
        return value >> shift
    
    def cmd_and(self, args: List[str], context: Dict[str, Any] = None):
        """Bitwise AND: AND a, b"""
        if len(args) < 2:
            raise PDSXCommandError("AND a, b gerekli")
        
        a = int(args[0])
        b = int(args[1])
        return a & b
    
    def cmd_or(self, args: List[str], context: Dict[str, Any] = None):
        """Bitwise OR: OR a, b"""
        if len(args) < 2:
            raise PDSXCommandError("OR a, b gerekli")
        
        a = int(args[0])
        b = int(args[1])
        return a | b
    
    def cmd_xor(self, args: List[str], context: Dict[str, Any] = None):
        """Bitwise XOR: XOR a, b"""
        if len(args) < 2:
            raise PDSXCommandError("XOR a, b gerekli")
        
        a = int(args[0])
        b = int(args[1])
        return a ^ b
    
    def cmd_not(self, args: List[str], context: Dict[str, Any] = None):
        """Bitwise NOT: NOT value"""
        if len(args) < 1:
            raise PDSXCommandError("NOT value gerekli")
        
        value = int(args[0])
        return ~value
    
    def cmd_bitfield(self, args: List[str], context: Dict[str, Any] = None):
        """Bit alanı çıkar: BITFIELD value, start, length"""
        if len(args) < 3:
            raise PDSXCommandError("BITFIELD value, start, length gerekli")
        
        value = int(args[0])
        start = int(args[1])
        length = int(args[2])
        
        mask = (1 << length) - 1
        return (value >> start) & mask
    
    def cmd_setbit(self, args: List[str], context: Dict[str, Any] = None):
        """Bit ayarla: SETBIT value, bit"""
        if len(args) < 2:
            raise PDSXCommandError("SETBIT value, bit gerekli")
        
        value = int(args[0])
        bit = int(args[1])
        return value | (1 << bit)
    
    def cmd_clrbit(self, args: List[str], context: Dict[str, Any] = None):
        """Bit temizle: CLRBIT value, bit"""
        if len(args) < 2:
            raise PDSXCommandError("CLRBIT value, bit gerekli")
        
        value = int(args[0])
        bit = int(args[1])
        return value & ~(1 << bit)
    
    def cmd_testbit(self, args: List[str], context: Dict[str, Any] = None):
        """Bit test: TESTBIT value, bit"""
        if len(args) < 2:
            raise PDSXCommandError("TESTBIT value, bit gerekli")
        
        value = int(args[0])
        bit = int(args[1])
        return bool(value & (1 << bit))
    
    # ========== RGBA Komutları ==========
    
    def cmd_rgba(self, args: List[str], context: Dict[str, Any] = None):
        """RGBA renk: RGBA r, g, b, a"""
        if len(args) < 4:
            raise PDSXCommandError("RGBA r, g, b, a gerekli")
        
        r = int(args[0])
        g = int(args[1])
        b = int(args[2])
        a = int(args[3])
        
        return (r << 24) | (g << 16) | (b << 8) | a
    
    def cmd_rgb(self, args: List[str], context: Dict[str, Any] = None):
        """RGB renk: RGB r, g, b"""
        if len(args) < 3:
            raise PDSXCommandError("RGB r, g, b gerekli")
        
        r = int(args[0])
        g = int(args[1])
        b = int(args[2])
        
        return (r << 16) | (g << 8) | b
    
    def cmd_getr(self, args: List[str], context: Dict[str, Any] = None):
        """Kırmızı bileşen: GETR color"""
        if len(args) < 1:
            raise PDSXCommandError("GETR color gerekli")
        
        color = int(args[0])
        return (color >> 16) & 0xFF
    
    def cmd_getg(self, args: List[str], context: Dict[str, Any] = None):
        """Yeşil bileşen: GETG color"""
        if len(args) < 1:
            raise PDSXCommandError("GETG color gerekli")
        
        color = int(args[0])
        return (color >> 8) & 0xFF
    
    def cmd_getb(self, args: List[str], context: Dict[str, Any] = None):
        """Mavi bileşen: GETB color"""
        if len(args) < 1:
            raise PDSXCommandError("GETB color gerekli")
        
        color = int(args[0])
        return color & 0xFF
    
    def cmd_geta(self, args: List[str], context: Dict[str, Any] = None):
        """Alpha bileşen: GETA color"""
        if len(args) < 1:
            raise PDSXCommandError("GETA color gerekli")
        
        color = int(args[0])
        return (color >> 24) & 0xFF
    
    # ========== Yardımcı Komutlar ==========
    
    def cmd_align(self, args: List[str], context: Dict[str, Any] = None):
        """Hizala: ALIGN value, boundary"""
        if len(args) < 2:
            raise PDSXCommandError("ALIGN value, boundary gerekli")
        
        value = int(args[0])
        boundary = int(args[1])
        
        return ((value + boundary - 1) // boundary) * boundary
    
    def cmd_clamp(self, args: List[str], context: Dict[str, Any] = None):
        """Sınırla: CLAMP value, min, max"""
        if len(args) < 3:
            raise PDSXCommandError("CLAMP value, min, max gerekli")
        
        value = float(args[0])
        min_val = float(args[1])
        max_val = float(args[2])
        
        return max(min_val, min(value, max_val))
    
    def cmd_lerp(self, args: List[str], context: Dict[str, Any] = None):
        """Lineer interpolasyon: LERP a, b, t"""
        if len(args) < 3:
            raise PDSXCommandError("LERP a, b, t gerekli")
        
        a = float(args[0])
        b = float(args[1])
        t = float(args[2])
        
        return a + (b - a) * t
    
    # ========== Yardımcı Metodlar ==========
    
    def _color_num_to_name(self, num: int) -> str:
        """Renk numarasını isme çevir"""
        for name, value in self.COLORS.items():
            if value == num:
                return name
        return "WHITE"
    
    def _color_name_to_num(self, name: str) -> int:
        """Renk ismini numaraya çevir"""
        return self.COLORS.get(name.upper(), 7)
    
    # ============================================================================
    # PHASE 1: ADVANCED SPRITE MANAGER COMMANDS (24 Ekim 2025)
    # ============================================================================
    
    def cmd_sprite_create_ascii(self, args: List[str], context: Dict[str, Any] = None):
        """
        SPRITE CREATE ASCII - ASCII sprite oluştur
        
        Syntax: SPRITE CREATE ASCII sprite_id, x, y, chars [, layer] [, color]
        
        Args:
            sprite_id: Sprite ID (1-128)
            x: X koordinatı
            y: Y koordinatı
            chars: Sprite karakterleri (string veya multi-line)
            layer: Z-order layer (opsiyonel, default: 0)
            color: ANSI color code (opsiyonel)
        
        Example:
            SPRITE CREATE ASCII 1, 10, 10, "@"
            SPRITE CREATE ASCII 2, 20, 20, "O-O", 5, "31"
        """
        if len(args) < 4:
            raise PDSXCommandError("SPRITE CREATE ASCII: sprite_id, x, y, chars gerekli")
        
        sprite_id = int(self.evaluate_expression(args[0], context))
        x = int(self.evaluate_expression(args[1], context))
        y = int(self.evaluate_expression(args[2], context))
        chars = str(self.evaluate_expression(args[3], context))
        
        # Optional parameters
        layer = int(self.evaluate_expression(args[4], context)) if len(args) > 4 else 0
        color = str(self.evaluate_expression(args[5], context)) if len(args) > 5 else None
        
        try:
            sprite = self.sprite_manager.create_ascii_sprite(
                sprite_id, x, y, chars,
                visible=True,
                layer=layer,
                color=color
            )
            
            if self.interpreter.debug_mode:
                print(f"[SPRITE] Created ASCII sprite: {sprite}")
            
            return sprite_id
            
        except ValueError as e:
            raise PDSXCommandError(f"SPRITE CREATE ASCII: {e}")
    
    def cmd_sprite_load(self, args: List[str], context: Dict[str, Any] = None):
        """
        SPRITE LOAD - Image sprite yükle
        
        Syntax: SPRITE LOAD sprite_id, image_path, x, y [, layer] [, scale]
        
        Args:
            sprite_id: Sprite ID (129-256)
            image_path: Image dosyasının yolu
            x: X koordinatı
            y: Y koordinatı
            layer: Z-order layer (opsiyonel, default: 0)
            scale: Ölçek faktörü (opsiyonel, default: 1.0)
        
        Example:
            SPRITE LOAD 129, "player.png", 100, 100
            SPRITE LOAD 130, "enemy.png", 200, 150, 10, 2.0
        """
        if len(args) < 4:
            raise PDSXCommandError("SPRITE LOAD: sprite_id, image_path, x, y gerekli")
        
        sprite_id = int(self.evaluate_expression(args[0], context))
        image_path = str(self.evaluate_expression(args[1], context)).strip('"\'')
        x = int(self.evaluate_expression(args[2], context))
        y = int(self.evaluate_expression(args[3], context))
        
        # Optional parameters
        layer = int(self.evaluate_expression(args[4], context)) if len(args) > 4 else 0
        scale = float(self.evaluate_expression(args[5], context)) if len(args) > 5 else 1.0
        
        try:
            sprite = self.sprite_manager.load_image_sprite(
                sprite_id, image_path, x, y,
                visible=True,
                layer=layer,
                scale=scale
            )
            
            if self.interpreter.debug_mode:
                print(f"[SPRITE] Loaded image sprite: {sprite}")
            
            return sprite_id
            
        except (ValueError, FileNotFoundError) as e:
            raise PDSXCommandError(f"SPRITE LOAD: {e}")
    
    def cmd_sprite_move(self, args: List[str], context: Dict[str, Any] = None):
        """
        SPRITE MOVE - Sprite'ı göreceli hareket ettir
        
        Syntax: SPRITE MOVE sprite_id, dx, dy
        
        Example: SPRITE MOVE 1, 5, -3
        """
        if len(args) < 3:
            raise PDSXCommandError("SPRITE MOVE: sprite_id, dx, dy gerekli")
        
        sprite_id = int(self.evaluate_expression(args[0], context))
        dx = int(self.evaluate_expression(args[1], context))
        dy = int(self.evaluate_expression(args[2], context))
        
        if not self.sprite_manager.move_sprite(sprite_id, dx, dy):
            raise PDSXCommandError(f"SPRITE MOVE: Sprite {sprite_id} bulunamadı")
        
        if self.interpreter.debug_mode:
            sprite = self.sprite_manager.get_sprite(sprite_id)
            print(f"[SPRITE] Moved sprite {sprite_id} to ({sprite.x}, {sprite.y})")
    
    def cmd_sprite_position(self, args: List[str], context: Dict[str, Any] = None):
        """
        SPRITE POSITION - Sprite'ın pozisyonunu mutlak ayarla
        
        Syntax: SPRITE POSITION sprite_id, x, y
        
        Example: SPRITE POSITION 1, 100, 200
        """
        if len(args) < 3:
            raise PDSXCommandError("SPRITE POSITION: sprite_id, x, y gerekli")
        
        sprite_id = int(self.evaluate_expression(args[0], context))
        x = int(self.evaluate_expression(args[1], context))
        y = int(self.evaluate_expression(args[2], context))
        
        if not self.sprite_manager.set_sprite_position(sprite_id, x, y):
            raise PDSXCommandError(f"SPRITE POSITION: Sprite {sprite_id} bulunamadı")
        
        if self.interpreter.debug_mode:
            print(f"[SPRITE] Set sprite {sprite_id} position to ({x}, {y})")
    
    def cmd_sprite_visible(self, args: List[str], context: Dict[str, Any] = None):
        """
        SPRITE VISIBLE - Sprite görünürlüğünü ayarla
        
        Syntax: SPRITE VISIBLE sprite_id, true/false
        
        Example: SPRITE VISIBLE 1, FALSE
        """
        if len(args) < 2:
            raise PDSXCommandError("SPRITE VISIBLE: sprite_id, visible gerekli")
        
        sprite_id = int(self.evaluate_expression(args[0], context))
        visible_str = str(self.evaluate_expression(args[1], context)).upper()
        visible = visible_str in ['TRUE', '1', 'YES', 'ON']
        
        if not self.sprite_manager.set_sprite_visible(sprite_id, visible):
            raise PDSXCommandError(f"SPRITE VISIBLE: Sprite {sprite_id} bulunamadı")
        
        if self.interpreter.debug_mode:
            print(f"[SPRITE] Set sprite {sprite_id} visible: {visible}")
    
    def cmd_sprite_layer(self, args: List[str], context: Dict[str, Any] = None):
        """
        SPRITE LAYER - Sprite z-order layer'ını ayarla
        
        Syntax: SPRITE LAYER sprite_id, layer_value
        
        Example: SPRITE LAYER 1, 10
        """
        if len(args) < 2:
            raise PDSXCommandError("SPRITE LAYER: sprite_id, layer gerekli")
        
        sprite_id = int(self.evaluate_expression(args[0], context))
        layer = int(self.evaluate_expression(args[1], context))
        
        if not self.sprite_manager.set_sprite_layer(sprite_id, layer):
            raise PDSXCommandError(f"SPRITE LAYER: Sprite {sprite_id} bulunamadı")
        
        if self.interpreter.debug_mode:
            print(f"[SPRITE] Set sprite {sprite_id} layer: {layer}")
    
    def cmd_sprite_destroy(self, args: List[str], context: Dict[str, Any] = None):
        """
        SPRITE DESTROY - Sprite'ı yok et
        
        Syntax: SPRITE DESTROY sprite_id
        
        Example: SPRITE DESTROY 1
        """
        if len(args) < 1:
            raise PDSXCommandError("SPRITE DESTROY: sprite_id gerekli")
        
        sprite_id = int(self.evaluate_expression(args[0], context))
        
        if not self.sprite_manager.destroy_sprite(sprite_id):
            raise PDSXCommandError(f"SPRITE DESTROY: Sprite {sprite_id} bulunamadı")
        
        if self.interpreter.debug_mode:
            print(f"[SPRITE] Destroyed sprite {sprite_id}")
    
    def cmd_sprite_info(self, args: List[str], context: Dict[str, Any] = None):
        """
        SPRITE INFO - Sprite bilgilerini döndür
        
        Syntax: info = SPRITE INFO sprite_id
        
        Returns: Dictionary veya None
        
        Example: info = SPRITE INFO 1
        """
        if len(args) < 1:
            raise PDSXCommandError("SPRITE INFO: sprite_id gerekli")
        
        sprite_id = int(self.evaluate_expression(args[0], context))
        info = self.sprite_manager.get_sprite_info(sprite_id)
        
        if info is None:
            raise PDSXCommandError(f"SPRITE INFO: Sprite {sprite_id} bulunamadı")
        
        if self.interpreter.debug_mode:
            print(f"[SPRITE] Info for sprite {sprite_id}: {info}")
        
        return info
    
    def cmd_sprite_count(self, args: List[str], context: Dict[str, Any] = None):
        """
        SPRITE COUNT - Sprite sayısını döndür
        
        Syntax: count = SPRITE COUNT [type]
        
        Args:
            type: "ASCII", "IMAGE", "ALL" (opsiyonel, default: "ALL")
        
        Example:
            total = SPRITE COUNT
            ascii_count = SPRITE COUNT "ASCII"
        """
        stats = self.sprite_manager.get_stats()
        
        if len(args) == 0:
            return stats['total_count']
        
        sprite_type = str(self.evaluate_expression(args[0], context)).upper()
        
        if sprite_type == "ASCII":
            return stats['ascii_count']
        elif sprite_type == "IMAGE":
            return stats['image_count']
        elif sprite_type == "ALL":
            return stats['total_count']
        else:
            raise PDSXCommandError(f"SPRITE COUNT: Geçersiz tip '{sprite_type}'")
    
    def cmd_sprite_clear(self, args: List[str], context: Dict[str, Any] = None):
        """
        SPRITE CLEAR - Sprite'ları temizle
        
        Syntax: SPRITE CLEAR [type]
        
        Args:
            type: "ASCII", "IMAGE", "ALL" (opsiyonel, default: "ALL")
        
        Example:
            SPRITE CLEAR
            SPRITE CLEAR "ASCII"
        """
        if len(args) == 0:
            self.sprite_manager.clear_all_sprites()
            if self.interpreter.debug_mode:
                print("[SPRITE] Cleared all sprites")
            return
        
        sprite_type = str(self.evaluate_expression(args[0], context)).upper()
        
        if sprite_type == "ASCII":
            self.sprite_manager.clear_ascii_sprites()
            if self.interpreter.debug_mode:
                print("[SPRITE] Cleared ASCII sprites")
        elif sprite_type == "IMAGE":
            self.sprite_manager.clear_image_sprites()
            if self.interpreter.debug_mode:
                print("[SPRITE] Cleared image sprites")
        elif sprite_type == "ALL":
            self.sprite_manager.clear_all_sprites()
            if self.interpreter.debug_mode:
                print("[SPRITE] Cleared all sprites")
        else:
            raise PDSXCommandError(f"SPRITE CLEAR: Geçersiz tip '{sprite_type}'")
    
    # ========================================================================
    # PHASE 2: FONT MANAGER COMMANDS (24 Ekim 2025)
    # ========================================================================
    
    def cmd_font_load(self, args: List[str], context: Dict[str, Any] = None):
        """
        FONTLOAD - Load TTF font
        
        Syntax: FONTLOAD font_id, font_path, base_size
        
        Args:
            font_id: Font ID (1-256)
            font_path: TTF dosya yolu
            base_size: Temel font boyutu
        
        Example: FONTLOAD 1, "arial.ttf", 16
        """
        if len(args) < 3:
            raise PDSXCommandError("FONTLOAD: font_id, font_path, base_size gerekli")
        
        font_id = int(self.evaluate_expression(args[0], context))
        font_path = str(self.evaluate_expression(args[1], context)).strip('"\'')
        base_size = int(self.evaluate_expression(args[2], context))
        
        try:
            self.font_manager.load_font(font_id, font_path, base_size)
            if self.interpreter.debug_mode:
                print(f"[FONT] Loaded font {font_id} from '{font_path}' (size: {base_size})")
        except Exception as e:
            raise PDSXCommandError(f"FONTLOAD: {e}")
    
    def cmd_font_system(self, args: List[str], context: Dict[str, Any] = None):
        """
        FONTSYS - Load system font
        
        Syntax: FONTSYS font_id, font_name, base_size
        
        Args:
            font_id: Font ID (1-256)
            font_name: System font name (e.g., "Arial", "Times")
            base_size: Temel font boyutu
        
        Example: FONTSYS 2, "Arial", 16
        """
        if len(args) < 3:
            raise PDSXCommandError("FONTSYS: font_id, font_name, base_size gerekli")
        
        font_id = int(self.evaluate_expression(args[0], context))
        font_name = str(self.evaluate_expression(args[1], context)).strip('"\'')
        base_size = int(self.evaluate_expression(args[2], context))
        
        try:
            self.font_manager.load_system_font(font_id, font_name, base_size)
            if self.interpreter.debug_mode:
                print(f"[FONT] Loaded system font {font_id}: '{font_name}' (size: {base_size})")
        except Exception as e:
            raise PDSXCommandError(f"FONTSYS: {e}")
    
    def cmd_font_unload(self, args: List[str], context: Dict[str, Any] = None):
        """
        FONTFREE - Unload font
        
        Syntax: FONTFREE font_id
        
        Args:
            font_id: Font ID to unload
        
        Example: FONTFREE 1
        """
        if len(args) < 1:
            raise PDSXCommandError("FONTFREE: font_id gerekli")
        
        font_id = int(self.evaluate_expression(args[0], context))
        
        try:
            self.font_manager.unload_font(font_id)
            if self.interpreter.debug_mode:
                print(f"[FONT] Unloaded font {font_id}")
        except Exception as e:
            raise PDSXCommandError(f"FONTFREE: {e}")
    
    def cmd_text_draw(self, args: List[str], context: Dict[str, Any] = None):
        """
        TEXTDRAW - Draw text
        
        Syntax: TEXTDRAW font_id, x, y, text, size [, r, g, b]
        
        Args:
            font_id: Font ID
            x, y: Position
            text: Text to render
            size: Font size
            r, g, b: Color (optional, default: white)
        
        Example: TEXTDRAW 1, 100, 100, "Hello World", 16
        """
        if len(args) < 5:
            raise PDSXCommandError("TEXTDRAW: font_id, x, y, text, size gerekli")
        
        font_id = int(self.evaluate_expression(args[0], context))
        x = int(self.evaluate_expression(args[1], context))
        y = int(self.evaluate_expression(args[2], context))
        text = str(self.evaluate_expression(args[3], context)).strip('"\'')
        size = int(self.evaluate_expression(args[4], context))
        
        # Color (optional)
        color = (255, 255, 255)
        if len(args) >= 8:
            r = int(self.evaluate_expression(args[5], context))
            g = int(self.evaluate_expression(args[6], context))
            b = int(self.evaluate_expression(args[7], context))
            color = (r, g, b)
        
        try:
            from .graphics.text_renderer import TextStyle
            style = TextStyle(color=color)
            surface = self.text_renderer.render_text(font_id, text, size, style)
            
            if self.interpreter.debug_mode:
                print(f"[TEXT] Rendered '{text}' at ({x}, {y}) with font {font_id}")
            
            return surface
        except Exception as e:
            raise PDSXCommandError(f"TEXTDRAW: {e}")
    
    def cmd_text_rotated(self, args: List[str], context: Dict[str, Any] = None):
        """
        TEXTROT - Draw rotated text
        
        Syntax: TEXTROT font_id, x, y, text, size, angle [, r, g, b]
        
        Args:
            font_id: Font ID
            x, y: Position
            text: Text to render
            size: Font size
            angle: Rotation angle (degrees)
            r, g, b: Color (optional, default: white)
        
        Example: TEXTROT 1, 100, 100, "Rotated", 16, 45
        """
        if len(args) < 6:
            raise PDSXCommandError("TEXTROT: font_id, x, y, text, size, angle gerekli")
        
        font_id = int(self.evaluate_expression(args[0], context))
        x = int(self.evaluate_expression(args[1], context))
        y = int(self.evaluate_expression(args[2], context))
        text = str(self.evaluate_expression(args[3], context)).strip('"\'')
        size = int(self.evaluate_expression(args[4], context))
        angle = float(self.evaluate_expression(args[5], context))
        
        # Color (optional)
        color = (255, 255, 255)
        if len(args) >= 9:
            r = int(self.evaluate_expression(args[6], context))
            g = int(self.evaluate_expression(args[7], context))
            b = int(self.evaluate_expression(args[8], context))
            color = (r, g, b)
        
        try:
            from .graphics.text_renderer import TextStyle
            style = TextStyle(color=color)
            surface = self.text_renderer.render_rotated_text(
                font_id, text, size, angle, style, use_cache=True
            )
            
            if self.interpreter.debug_mode:
                print(f"[TEXT] Rendered rotated '{text}' at ({x}, {y}) "
                      f"with angle {angle}° using font {font_id}")
            
            return surface
        except Exception as e:
            raise PDSXCommandError(f"TEXTROT: {e}")
    
    def cmd_text_multiline(self, args: List[str], context: Dict[str, Any] = None):
        """
        TEXTMULTI - Draw multi-line text
        
        Syntax: TEXTMULTI font_id, x, y, text, size, line_spacing
        
        Args:
            font_id: Font ID
            x, y: Position
            text: Multi-line text (\\n separated)
            size: Font size
            line_spacing: Line spacing multiplier (e.g., 1.2)
        
        Example: TEXTMULTI 1, 50, 50, "Line1\\nLine2", 14, 1.2
        """
        if len(args) < 6:
            raise PDSXCommandError("TEXTMULTI: font_id, x, y, text, size, line_spacing gerekli")
        
        font_id = int(self.evaluate_expression(args[0], context))
        x = int(self.evaluate_expression(args[1], context))
        y = int(self.evaluate_expression(args[2], context))
        text = str(self.evaluate_expression(args[3], context)).strip('"\'')
        size = int(self.evaluate_expression(args[4], context))
        line_spacing = float(self.evaluate_expression(args[5], context))
        
        try:
            from .graphics.text_renderer import TextStyle
            style = TextStyle()
            surface = self.text_renderer.render_multiline_text(
                font_id, text, size, line_spacing, style
            )
            
            if self.interpreter.debug_mode:
                print(f"[TEXT] Rendered multi-line text at ({x}, {y}) using font {font_id}")
            
            return surface
        except Exception as e:
            raise PDSXCommandError(f"TEXTMULTI: {e}")
    
    def cmd_font_info(self, args: List[str], context: Dict[str, Any] = None):
        """
        FONTINFO - Get font information
        
        Syntax: info = FONTINFO font_id
        
        Returns: Dictionary with font information
        
        Example: info = FONTINFO 1
        """
        if len(args) < 1:
            raise PDSXCommandError("FONTINFO: font_id gerekli")
        
        font_id = int(self.evaluate_expression(args[0], context))
        
        try:
            info = self.font_manager.get_font_info(font_id)
            if info is None:
                raise PDSXCommandError(f"FONTINFO: Font {font_id} bulunamadı")
            
            # Convert to dict
            font_dict = {
                'font_id': info.font_id,
                'font_path': info.font_path,
                'base_size': info.base_size,
                'is_system_font': info.is_system_font,
                'family_name': info.family_name,
                'cached_sizes': len(info._size_cache)
            }
            
            if self.interpreter.debug_mode:
                print(f"[FONT] Info for font {font_id}: {font_dict}")
            
            return font_dict
        except Exception as e:
            raise PDSXCommandError(f"FONTINFO: {e}")
    
    def cmd_font_count(self, args: List[str], context: Dict[str, Any] = None):
        """
        FONTCNT - Get loaded font count
        
        Syntax: count = FONTCNT
        
        Returns: Number of loaded fonts
        
        Example: count = FONTCNT
        """
        stats = self.font_manager.get_stats()
        count = stats['loaded_count']
        
        if self.interpreter.debug_mode:
            print(f"[FONT] Loaded fonts: {count}")
        
        return count
    
    # ========================================================================
    # PHASE 3: COLLISION DETECTION COMMANDS (24 Ekim 2025)
    # ========================================================================
    
    def cmd_collision_aabb(self, args: List[str], context: Dict[str, Any] = None):
        """
        CAABB - Check AABB collision
        
        Syntax: collided = CAABB sprite_id1, sprite_id2
        
        Args:
            sprite_id1: First sprite ID
            sprite_id2: Second sprite ID
        
        Returns: True if collision, False otherwise
        
        Example: hit = CAABB 1, 2
        """
        if len(args) < 2:
            raise PDSXCommandError("CAABB: sprite_id1, sprite_id2 gerekli")
        
        sprite_id1 = int(self.evaluate_expression(args[0], context))
        sprite_id2 = int(self.evaluate_expression(args[1], context))
        
        # Get sprites
        sprite1 = self.sprite_manager.get_sprite(sprite_id1)
        sprite2 = self.sprite_manager.get_sprite(sprite_id2)
        
        if not sprite1 or not sprite2:
            raise PDSXCommandError(f"CAABB: Sprite bulunamadı")
        
        # Check collision
        info = self.collision_detector.check_aabb(sprite1, sprite2, sprite_id1, sprite_id2)
        
        if self.interpreter.debug_mode and info.collided:
            print(f"[COLLISION] AABB collision: {sprite_id1} <-> {sprite_id2} "
                  f"(overlap: {info.overlap_x:.1f}, {info.overlap_y:.1f})")
        
        return info.collided
    
    def cmd_collision_circle(self, args: List[str], context: Dict[str, Any] = None):
        """
        CCIRCLE - Check circle collision
        
        Syntax: collided = CCIRCLE sprite_id1, sprite_id2 [, radius1, radius2]
        
        Args:
            sprite_id1: First sprite ID
            sprite_id2: Second sprite ID
            radius1: First circle radius (optional)
            radius2: Second circle radius (optional)
        
        Returns: True if collision, False otherwise
        
        Example: hit = CCIRCLE 1, 2, 16, 24
        """
        if len(args) < 2:
            raise PDSXCommandError("CCIRCLE: sprite_id1, sprite_id2 gerekli")
        
        sprite_id1 = int(self.evaluate_expression(args[0], context))
        sprite_id2 = int(self.evaluate_expression(args[1], context))
        
        radius1 = None
        radius2 = None
        if len(args) >= 4:
            radius1 = float(self.evaluate_expression(args[2], context))
            radius2 = float(self.evaluate_expression(args[3], context))
        
        # Get sprites
        sprite1 = self.sprite_manager.get_sprite(sprite_id1)
        sprite2 = self.sprite_manager.get_sprite(sprite_id2)
        
        if not sprite1 or not sprite2:
            raise PDSXCommandError(f"CCIRCLE: Sprite bulunamadı")
        
        # Check collision
        info = self.collision_detector.check_circle(
            sprite1, sprite2, radius1, radius2, sprite_id1, sprite_id2
        )
        
        if self.interpreter.debug_mode and info.collided:
            print(f"[COLLISION] Circle collision: {sprite_id1} <-> {sprite_id2}")
        
        return info.collided
    
    def cmd_collision_pixel(self, args: List[str], context: Dict[str, Any] = None):
        """
        CPIXEL - Check pixel-perfect collision
        
        Syntax: collided = CPIXEL sprite_id1, sprite_id2
        
        Args:
            sprite_id1: First sprite ID (ImageSprite)
            sprite_id2: Second sprite ID (ImageSprite)
        
        Returns: True if collision, False otherwise
        
        Example: hit = CPIXEL 129, 130
        """
        if len(args) < 2:
            raise PDSXCommandError("CPIXEL: sprite_id1, sprite_id2 gerekli")
        
        sprite_id1 = int(self.evaluate_expression(args[0], context))
        sprite_id2 = int(self.evaluate_expression(args[1], context))
        
        # Get sprites
        sprite1 = self.sprite_manager.get_sprite(sprite_id1)
        sprite2 = self.sprite_manager.get_sprite(sprite_id2)
        
        if not sprite1 or not sprite2:
            raise PDSXCommandError(f"CPIXEL: Sprite bulunamadı")
        
        # Check collision
        info = self.collision_detector.check_pixel_perfect(sprite1, sprite2, sprite_id1, sprite_id2)
        
        if self.interpreter.debug_mode and info.collided:
            print(f"[COLLISION] Pixel collision: {sprite_id1} <-> {sprite_id2}")
        
        return info.collided
    
    def cmd_collision_point(self, args: List[str], context: Dict[str, Any] = None):
        """
        CPOINT - Check point collision with sprite
        
        Syntax: hit = CPOINT sprite_id, x, y
        
        Args:
            sprite_id: Sprite ID
            x, y: Point coordinates
        
        Returns: True if point inside sprite, False otherwise
        
        Example: hit = CPOINT 1, 100, 150
        """
        if len(args) < 3:
            raise PDSXCommandError("CPOINT: sprite_id, x, y gerekli")
        
        sprite_id = int(self.evaluate_expression(args[0], context))
        x = float(self.evaluate_expression(args[1], context))
        y = float(self.evaluate_expression(args[2], context))
        
        # Get sprite
        sprite = self.sprite_manager.get_sprite(sprite_id)
        if not sprite:
            raise PDSXCommandError(f"CPOINT: Sprite {sprite_id} bulunamadı")
        
        # Check point
        hit = self.collision_detector.check_point(sprite, x, y)
        
        if self.interpreter.debug_mode and hit:
            print(f"[COLLISION] Point ({x}, {y}) inside sprite {sprite_id}")
        
        return hit
    
    def cmd_collision_list(self, args: List[str], context: Dict[str, Any] = None):
        """
        CLIST - Check collision with all visible sprites
        
        Syntax: collisions = CLIST sprite_id, collision_type
        
        Args:
            sprite_id: Sprite ID to check
            collision_type: "AABB", "Circle", or "Pixel"
        
        Returns: List of colliding sprite IDs
        
        Example: collisions = CLIST 1, "AABB"
        """
        if len(args) < 2:
            raise PDSXCommandError("CLIST: sprite_id, collision_type gerekli")
        
        sprite_id = int(self.evaluate_expression(args[0], context))
        collision_type = str(self.evaluate_expression(args[1], context)).upper().strip('"\'')
        
        # Get sprite
        sprite = self.sprite_manager.get_sprite(sprite_id)
        if not sprite:
            raise PDSXCommandError(f"CLIST: Sprite {sprite_id} bulunamadı")
        
        # Get all other visible sprites
        all_sprites = self.sprite_manager.get_visible_sprites()
        sprite_list = [(sid, spr) for sid, spr in all_sprites.items() if sid != sprite_id]
        
        # Check collisions
        collisions = self.collision_detector.check_collision_list(sprite, sprite_list, collision_type)
        
        # Return list of IDs
        collision_ids = [info.sprite2_id for info in collisions]
        
        if self.interpreter.debug_mode:
            print(f"[COLLISION] Sprite {sprite_id} collides with {len(collision_ids)} sprites ({collision_type})")
        
        return collision_ids
    
    def cmd_sprite_sort(self, args: List[str], context: Dict[str, Any] = None):
        """
        SSORT - Get sorted sprite list by layer
        
        Syntax: sorted = SSORT [min_layer, max_layer]
        
        Args:
            min_layer: Minimum layer (optional)
            max_layer: Maximum layer (optional)
        
        Returns: List of sprite IDs sorted by layer
        
        Example:
            all_sorted = SSORT
            range_sorted = SSORT 0, 10
        """
        # Sync sprites to Z-Order system
        self._sync_z_order()
        
        if len(args) == 0:
            # Get all sorted
            sprites = self.z_order.get_sorted_sprites()
        elif len(args) >= 2:
            # Get range
            min_layer = int(self.evaluate_expression(args[0], context))
            max_layer = int(self.evaluate_expression(args[1], context))
            sprites = self.z_order.get_sprites_in_layer_range(min_layer, max_layer)
        else:
            raise PDSXCommandError("SSORT: 0 veya 2 parametre gerekli")
        
        # Extract sprite IDs
        sprite_ids = []
        for layered in self.z_order._sprites:
            sprite_ids.append(layered.sprite_id)
        
        if self.interpreter.debug_mode:
            print(f"[Z-ORDER] Sorted {len(sprite_ids)} sprites")
        
        return sprite_ids
    
    def cmd_grid_insert(self, args: List[str], context: Dict[str, Any] = None):
        """
        GINSERT - Insert sprite into spatial grid
        
        Syntax: GINSERT sprite_id
        
        Args:
            sprite_id: Sprite ID to insert
        
        Example: GINSERT 1
        """
        if len(args) < 1:
            raise PDSXCommandError("GINSERT: sprite_id gerekli")
        
        sprite_id = int(self.evaluate_expression(args[0], context))
        
        # Get sprite
        sprite = self.sprite_manager.get_sprite(sprite_id)
        if not sprite:
            raise PDSXCommandError(f"GINSERT: Sprite {sprite_id} bulunamadı")
        
        # Get bounds
        bounds = sprite.get_bounds()
        if bounds:
            x, y, w, h = bounds
            self.spatial_grid.insert(sprite_id, x, y, w, h)
            
            if self.interpreter.debug_mode:
                print(f"[GRID] Inserted sprite {sprite_id} at ({x}, {y})")
    
    def cmd_grid_query(self, args: List[str], context: Dict[str, Any] = None):
        """
        GQUERY - Query sprites in area
        
        Syntax: sprites = GQUERY x, y, width, height
        
        Args:
            x, y: Query area position
            width, height: Query area size
        
        Returns: List of sprite IDs in area
        
        Example: sprites = GQUERY 0, 0, 320, 240
        """
        if len(args) < 4:
            raise PDSXCommandError("GQUERY: x, y, width, height gerekli")
        
        x = float(self.evaluate_expression(args[0], context))
        y = float(self.evaluate_expression(args[1], context))
        width = float(self.evaluate_expression(args[2], context))
        height = float(self.evaluate_expression(args[3], context))
        
        # Query grid
        sprite_ids = list(self.spatial_grid.query(x, y, width, height))
        
        if self.interpreter.debug_mode:
            print(f"[GRID] Found {len(sprite_ids)} sprites in area ({x}, {y}, {width}, {height})")
        
        return sprite_ids
    
    def cmd_grid_nearby(self, args: List[str], context: Dict[str, Any] = None):
        """
        GNEARBY - Get nearby sprites from grid
        
        Syntax: nearby = GNEARBY sprite_id
        
        Args:
            sprite_id: Sprite ID
        
        Returns: List of nearby sprite IDs
        
        Example: nearby = GNEARBY 1
        """
        if len(args) < 1:
            raise PDSXCommandError("GNEARBY: sprite_id gerekli")
        
        sprite_id = int(self.evaluate_expression(args[0], context))
        
        # Get nearby
        nearby_ids = list(self.spatial_grid.get_nearby_sprites(sprite_id))
        
        if self.interpreter.debug_mode:
            print(f"[GRID] Found {len(nearby_ids)} nearby sprites for {sprite_id}")
        
        return nearby_ids
    
    # ========================================================================
    # INTERNAL HELPERS
    # ========================================================================
    
    def _sync_z_order(self):
        """Sync sprite manager sprites to Z-Order system"""
        # Clear Z-Order
        self.z_order.clear()
        
        # Add all sprites
        for sprite_id, sprite in self.sprite_manager.get_all_sprites().items():
            layer = sprite.layer if hasattr(sprite, 'layer') else 0
            self.z_order.add_sprite(sprite_id, layer, sprite)
    
    # ========================================================================
    # PHASE 4: ANIMATION COMMANDS (24 Ekim 2025)
    # ========================================================================
    
    def cmd_animation_create(self, args: List[str], context: Dict[str, Any] = None):
        """
        ANIMCREATE - Create frame animation
        
        Syntax: anim_id = ANIMCREATE name, sprite_ids, fps, loop_mode
        
        Args:
            name: Animation name
            sprite_ids: List of sprite IDs for frames
            fps: Frames per second
            loop_mode: "loop", "once", or "ping-pong"
        
        Returns: Animation ID
        
        Example: anim_id = ANIMCREATE "walk", [1, 2, 3], 10, "loop"
        """
        if len(args) < 4:
            raise PDSXCommandError("ANIMCREATE: name, sprite_ids, fps, loop_mode gerekli")
        
        name = str(self.evaluate_expression(args[0], context))
        sprite_ids = self.evaluate_expression(args[1], context)
        fps = float(self.evaluate_expression(args[2], context))
        loop_mode = str(self.evaluate_expression(args[3], context))
        
        # Create animation
        anim_id = self.animation_manager.create_animation(
            name=name,
            sprite_ids=sprite_ids,
            fps=fps,
            loop_mode=loop_mode
        )
        
        if self.interpreter.debug_mode:
            print(f"[ANIM] Created animation {anim_id}: {name} ({len(sprite_ids)} frames @ {fps} FPS)")
        
        return anim_id
    
    def cmd_animation_play(self, args: List[str], context: Dict[str, Any] = None):
        """
        ANIMPLAY - Play animation
        
        Syntax: ANIMPLAY anim_id, [restart]
        
        Args:
            anim_id: Animation ID
            restart: Optional, True to restart (default: True)
        
        Returns: True if successful
        
        Example: ANIMPLAY 1
        """
        if len(args) < 1:
            raise PDSXCommandError("ANIMPLAY: anim_id gerekli")
        
        anim_id = int(self.evaluate_expression(args[0], context))
        restart = True
        if len(args) > 1:
            restart = bool(self.evaluate_expression(args[1], context))
        
        success = self.animation_manager.play_animation(anim_id, restart)
        
        if self.interpreter.debug_mode:
            print(f"[ANIM] Play animation {anim_id} (restart={restart})")
        
        return success
    
    def cmd_animation_pause(self, args: List[str], context: Dict[str, Any] = None):
        """
        ANIMPAUSE - Pause animation
        
        Syntax: ANIMPAUSE anim_id
        
        Args:
            anim_id: Animation ID
        
        Returns: True if successful
        
        Example: ANIMPAUSE 1
        """
        if len(args) < 1:
            raise PDSXCommandError("ANIMPAUSE: anim_id gerekli")
        
        anim_id = int(self.evaluate_expression(args[0], context))
        success = self.animation_manager.pause_animation(anim_id)
        
        if self.interpreter.debug_mode:
            print(f"[ANIM] Pause animation {anim_id}")
        
        return success
    
    def cmd_animation_stop(self, args: List[str], context: Dict[str, Any] = None):
        """
        ANIMSTOP - Stop animation and reset
        
        Syntax: ANIMSTOP anim_id
        
        Args:
            anim_id: Animation ID
        
        Returns: True if successful
        
        Example: ANIMSTOP 1
        """
        if len(args) < 1:
            raise PDSXCommandError("ANIMSTOP: anim_id gerekli")
        
        anim_id = int(self.evaluate_expression(args[0], context))
        success = self.animation_manager.stop_animation(anim_id)
        
        if self.interpreter.debug_mode:
            print(f"[ANIM] Stop animation {anim_id}")
        
        return success
    
    def cmd_animation_update(self, args: List[str], context: Dict[str, Any] = None):
        """
        ANIMUPDATE - Update all animations
        
        Syntax: ANIMUPDATE delta_time
        
        Args:
            delta_time: Time elapsed since last update (seconds)
        
        Returns: None
        
        Example: ANIMUPDATE 0.016  # ~60 FPS
        """
        if len(args) < 1:
            raise PDSXCommandError("ANIMUPDATE: delta_time gerekli")
        
        delta_time = float(self.evaluate_expression(args[0], context))
        self.animation_manager.update(delta_time)
        
        return None
    
    def cmd_animation_frame(self, args: List[str], context: Dict[str, Any] = None):
        """
        ANIMFRAME - Get current frame sprite ID
        
        Syntax: sprite_id = ANIMFRAME anim_id
        
        Args:
            anim_id: Animation ID
        
        Returns: Current sprite ID
        
        Example: sprite_id = ANIMFRAME 1
        """
        if len(args) < 1:
            raise PDSXCommandError("ANIMFRAME: anim_id gerekli")
        
        anim_id = int(self.evaluate_expression(args[0], context))
        sprite_id = self.animation_manager.get_current_sprite_id(anim_id)
        
        return sprite_id
    
    # Tween Commands
    
    def cmd_tween_create(self, args: List[str], context: Dict[str, Any] = None):
        """
        TWEEN - Create property tween
        
        Syntax: tween_id = TWEEN sprite_id, property, end_value, duration, easing
        
        Args:
            sprite_id: Target sprite ID
            property: Property name ("x", "y", "rotation", "scale", "alpha")
            end_value: Target value
            duration: Duration in seconds
            easing: Easing function name
        
        Returns: Tween ID
        
        Example: tween_id = TWEEN 1, "x", 100, 2.0, "ease_out_quad"
        """
        if len(args) < 5:
            raise PDSXCommandError("TWEEN: sprite_id, property, end_value, duration, easing gerekli")
        
        sprite_id = int(self.evaluate_expression(args[0], context))
        property_name = str(self.evaluate_expression(args[1], context))
        end_value = float(self.evaluate_expression(args[2], context))
        duration = float(self.evaluate_expression(args[3], context))
        easing = str(self.evaluate_expression(args[4], context))
        
        # Get current value from sprite
        sprite = self.sprite_manager.get_sprite(sprite_id)
        if not sprite:
            raise PDSXCommandError(f"TWEEN: Sprite {sprite_id} not found")
        
        start_value = 0.0
        if property_name == "x":
            start_value = sprite.x
        elif property_name == "y":
            start_value = sprite.y
        elif property_name == "rotation":
            start_value = getattr(sprite, 'rotation', 0.0)
        elif property_name == "scale":
            start_value = getattr(sprite, 'scale', 1.0)
        elif property_name == "alpha":
            start_value = getattr(sprite, 'alpha', 1.0)
        
        # Create tween
        tween_id = self.tween_system.create_tween(
            target_id=sprite_id,
            property_name=property_name,
            end_value=end_value,
            duration=duration,
            start_value=start_value,
            easing=easing
        )
        
        if self.interpreter.debug_mode:
            print(f"[TWEEN] Created tween {tween_id}: sprite {sprite_id}.{property_name} {start_value} → {end_value} ({duration}s, {easing})")
        
        return tween_id
    
    def cmd_tween_sequence(self, args: List[str], context: Dict[str, Any] = None):
        """
        TWEENSEQ - Create tween sequence
        
        Syntax: seq_id = TWEENSEQ tween_ids, loop
        
        Args:
            tween_ids: List of tween IDs
            loop: Loop the sequence
        
        Returns: Sequence ID
        
        Example: seq_id = TWEENSEQ [1, 2, 3], False
        """
        if len(args) < 2:
            raise PDSXCommandError("TWEENSEQ: tween_ids, loop gerekli")
        
        tween_ids = self.evaluate_expression(args[0], context)
        loop = bool(self.evaluate_expression(args[1], context))
        
        seq_id = self.tween_system.create_sequence(tween_ids, loop)
        
        if self.interpreter.debug_mode:
            print(f"[TWEEN] Created sequence {seq_id}: {len(tween_ids)} tweens (loop={loop})")
        
        return seq_id
    
    def cmd_tween_parallel(self, args: List[str], context: Dict[str, Any] = None):
        """
        TWEENPAR - Create parallel tweens
        
        Syntax: par_id = TWEENPAR tween_ids
        
        Args:
            tween_ids: List of tween IDs
        
        Returns: Parallel ID
        
        Example: par_id = TWEENPAR [1, 2]
        """
        if len(args) < 1:
            raise PDSXCommandError("TWEENPAR: tween_ids gerekli")
        
        tween_ids = self.evaluate_expression(args[0], context)
        
        par_id = self.tween_system.create_parallel(tween_ids)
        
        if self.interpreter.debug_mode:
            print(f"[TWEEN] Created parallel {par_id}: {len(tween_ids)} tweens")
        
        return par_id
    
    def cmd_tween_update(self, args: List[str], context: Dict[str, Any] = None):
        """
        TWEENUPDATE - Update all tweens
        
        Syntax: TWEENUPDATE delta_time
        
        Args:
            delta_time: Time elapsed since last update (seconds)
        
        Returns: None
        
        Example: TWEENUPDATE 0.016
        """
        if len(args) < 1:
            raise PDSXCommandError("TWEENUPDATE: delta_time gerekli")
        
        delta_time = float(self.evaluate_expression(args[0], context))
        self.tween_system.update(delta_time)
        
        # Apply tween values to sprites
        for tween_id, tween in self.tween_system._tweens.items():
            if tween.is_active:
                value = self.tween_system.get_tween_value(tween_id)
                if value is not None:
                    sprite = self.sprite_manager.get_sprite(tween.target_id)
                    if sprite:
                        if tween.property_name == "x":
                            sprite.x = value
                        elif tween.property_name == "y":
                            sprite.y = value
                        elif tween.property_name == "rotation":
                            sprite.rotation = value
                        elif tween.property_name == "scale":
                            sprite.scale = value
                        elif tween.property_name == "alpha":
                            sprite.alpha = value
        
        return None
    
    def cmd_tween_stop(self, args: List[str], context: Dict[str, Any] = None):
        """
        TWEENSTOP - Stop a tween
        
        Syntax: TWEENSTOP tween_id
        
        Args:
            tween_id: Tween ID
        
        Returns: True if successful
        
        Example: TWEENSTOP 1
        """
        if len(args) < 1:
            raise PDSXCommandError("TWEENSTOP: tween_id gerekli")
        
        tween_id = int(self.evaluate_expression(args[0], context))
        success = self.tween_system.stop_tween(tween_id)
        
        if self.interpreter.debug_mode:
            print(f"[TWEEN] Stop tween {tween_id}")
        
        return success
    
    # Timeline Commands
    
    def cmd_timeline_create(self, args: List[str], context: Dict[str, Any] = None):
        """
        TLCREATE - Create timeline
        
        Syntax: timeline_id = TLCREATE name, duration, loop
        
        Args:
            name: Timeline name
            duration: Duration in seconds
            loop: Loop timeline
        
        Returns: Timeline ID
        
        Example: timeline_id = TLCREATE "scene1", 5.0, True
        """
        if len(args) < 3:
            raise PDSXCommandError("TLCREATE: name, duration, loop gerekli")
        
        name = str(self.evaluate_expression(args[0], context))
        duration = float(self.evaluate_expression(args[1], context))
        loop = bool(self.evaluate_expression(args[2], context))
        
        timeline_id = self.timeline_manager.create_timeline(name, duration, loop)
        
        if self.interpreter.debug_mode:
            print(f"[TIMELINE] Created timeline {timeline_id}: {name} ({duration}s, loop={loop})")
        
        return timeline_id
    
    def cmd_timeline_add_track(self, args: List[str], context: Dict[str, Any] = None):
        """
        TLADDTRACK - Add track to timeline
        
        Syntax: track_id = TLADDTRACK timeline_id, sprite_id, property
        
        Args:
            timeline_id: Timeline ID
            sprite_id: Target sprite ID
            property: Property name
        
        Returns: Track ID
        
        Example: track_id = TLADDTRACK 1, 1, "x"
        """
        if len(args) < 3:
            raise PDSXCommandError("TLADDTRACK: timeline_id, sprite_id, property gerekli")
        
        timeline_id = int(self.evaluate_expression(args[0], context))
        sprite_id = int(self.evaluate_expression(args[1], context))
        property_name = str(self.evaluate_expression(args[2], context))
        
        track_id = self.timeline_manager.add_track(timeline_id, sprite_id, property_name)
        
        if self.interpreter.debug_mode:
            print(f"[TIMELINE] Added track {track_id} to timeline {timeline_id}: sprite {sprite_id}.{property_name}")
        
        return track_id
    
    def cmd_timeline_add_keyframe(self, args: List[str], context: Dict[str, Any] = None):
        """
        TLADDKEY - Add keyframe to track
        
        Syntax: TLADDKEY timeline_id, track_idx, time, value, easing
        
        Args:
            timeline_id: Timeline ID
            track_idx: Track index (0-based)
            time: Time in seconds
            value: Value at this time
            easing: Easing function name
        
        Returns: True if successful
        
        Example: TLADDKEY 1, 0, 0.0, 0, "linear"
        """
        if len(args) < 5:
            raise PDSXCommandError("TLADDKEY: timeline_id, track_idx, time, value, easing gerekli")
        
        timeline_id = int(self.evaluate_expression(args[0], context))
        track_idx = int(self.evaluate_expression(args[1], context))
        time = float(self.evaluate_expression(args[2], context))
        value = self.evaluate_expression(args[3], context)
        easing = str(self.evaluate_expression(args[4], context))
        
        success = self.timeline_manager.add_keyframe_by_index(
            timeline_id, track_idx, time, value, easing
        )
        
        if self.interpreter.debug_mode:
            print(f"[TIMELINE] Added keyframe to timeline {timeline_id} track {track_idx}: t={time}s, v={value}, easing={easing}")
        
        return success
    
    def cmd_timeline_play(self, args: List[str], context: Dict[str, Any] = None):
        """
        TLPLAY - Play timeline
        
        Syntax: TLPLAY timeline_id, [restart]
        
        Args:
            timeline_id: Timeline ID
            restart: Optional, True to restart
        
        Returns: True if successful
        
        Example: TLPLAY 1
        """
        if len(args) < 1:
            raise PDSXCommandError("TLPLAY: timeline_id gerekli")
        
        timeline_id = int(self.evaluate_expression(args[0], context))
        restart = True
        if len(args) > 1:
            restart = bool(self.evaluate_expression(args[1], context))
        
        success = self.timeline_manager.play_timeline(timeline_id, restart)
        
        if self.interpreter.debug_mode:
            print(f"[TIMELINE] Play timeline {timeline_id} (restart={restart})")
        
        return success
    
    def cmd_timeline_update(self, args: List[str], context: Dict[str, Any] = None):
        """
        TLUPDATE - Update all timelines
        
        Syntax: TLUPDATE delta_time
        
        Args:
            delta_time: Time elapsed since last update (seconds)
        
        Returns: None
        
        Example: TLUPDATE 0.016
        """
        if len(args) < 1:
            raise PDSXCommandError("TLUPDATE: delta_time gerekli")
        
        delta_time = float(self.evaluate_expression(args[0], context))
        self.timeline_manager.update(delta_time)
        
        # Apply timeline values to sprites
        for timeline_id, timeline in self.timeline_manager._timelines.items():
            if timeline.is_playing:
                values = self.timeline_manager.get_current_values(timeline_id)
                if values:
                    for sprite_id, properties in values.items():
                        sprite = self.sprite_manager.get_sprite(sprite_id)
                        if sprite:
                            for prop, val in properties.items():
                                if prop == "x":
                                    sprite.x = val
                                elif prop == "y":
                                    sprite.y = val
                                elif prop == "rotation":
                                    sprite.rotation = val
                                elif prop == "scale":
                                    sprite.scale = val
                                elif prop == "alpha":
                                    sprite.alpha = val
        
        return None
    
    def cmd_timeline_seek(self, args: List[str], context: Dict[str, Any] = None):
        """
        TLSEEK - Seek timeline to time
        
        Syntax: TLSEEK timeline_id, time
        
        Args:
            timeline_id: Timeline ID
            time: Time in seconds
        
        Returns: True if successful
        
        Example: TLSEEK 1, 2.5
        """
        if len(args) < 2:
            raise PDSXCommandError("TLSEEK: timeline_id, time gerekli")
        
        timeline_id = int(self.evaluate_expression(args[0], context))
        time = float(self.evaluate_expression(args[1], context))
        
        success = self.timeline_manager.seek_timeline(timeline_id, time)
        
        if self.interpreter.debug_mode:
            print(f"[TIMELINE] Seek timeline {timeline_id} to {time}s")
        
        return success
    
    def cmd_timeline_stop(self, args: List[str], context: Dict[str, Any] = None):
        """
        TLSTOP - Stop timeline
        
        Syntax: TLSTOP timeline_id
        
        Args:
            timeline_id: Timeline ID
        
        Returns: True if successful
        
        Example: TLSTOP 1
        """
        if len(args) < 1:
            raise PDSXCommandError("TLSTOP: timeline_id gerekli")
        
        timeline_id = int(self.evaluate_expression(args[0], context))
        success = self.timeline_manager.stop_timeline(timeline_id)
        
        if self.interpreter.debug_mode:
            print(f"[TIMELINE] Stop timeline {timeline_id}")
        
        return success
    
    # ========== PHASE 5: ADVANCED RENDERING COMMANDS ==========
    
    # Camera Commands
    
    def cmd_camera_create(self, args: List[str], context: Dict[str, Any] = None):
        """
        CAMCREATE - Create camera
        
        Syntax: CAMCREATE x, y, zoom, viewport_width, viewport_height
        
        Args:
            x, y: Camera position
            zoom: Zoom level (0.1-10.0)
            viewport_width, viewport_height: Viewport size
        
        Returns: Camera ID
        
        Example: cam = CAMCREATE 0, 0, 1.0, 800, 600
        """
        if len(args) < 5:
            raise PDSXCommandError("CAMCREATE: x, y, zoom, width, height gerekli")
        
        x = float(self.evaluate_expression(args[0], context))
        y = float(self.evaluate_expression(args[1], context))
        zoom = float(self.evaluate_expression(args[2], context))
        width = int(self.evaluate_expression(args[3], context))
        height = int(self.evaluate_expression(args[4], context))
        
        camera_id = self.camera_system.create_camera(x, y, zoom, width, height)
        
        if self.interpreter.debug_mode:
            print(f"[CAMERA] Created camera {camera_id} at ({x}, {y}) zoom={zoom}")
        
        return camera_id
    
    def cmd_camera_position(self, args: List[str], context: Dict[str, Any] = None):
        """
        CAMPOS - Set camera position
        
        Syntax: CAMPOS camera_id, x, y
        
        Args:
            camera_id: Camera ID
            x, y: New position
        
        Returns: True if successful
        
        Example: CAMPOS 1, 100, 200
        """
        if len(args) < 3:
            raise PDSXCommandError("CAMPOS: camera_id, x, y gerekli")
        
        camera_id = int(self.evaluate_expression(args[0], context))
        x = float(self.evaluate_expression(args[1], context))
        y = float(self.evaluate_expression(args[2], context))
        
        success = self.camera_system.set_position(camera_id, x, y)
        
        if self.interpreter.debug_mode:
            print(f"[CAMERA] Set camera {camera_id} position to ({x}, {y})")
        
        return success
    
    def cmd_camera_zoom(self, args: List[str], context: Dict[str, Any] = None):
        """
        CAMZOOM - Set camera zoom
        
        Syntax: CAMZOOM camera_id, zoom
        
        Args:
            camera_id: Camera ID
            zoom: Zoom level (0.1-10.0)
        
        Returns: True if successful
        
        Example: CAMZOOM 1, 2.0
        """
        if len(args) < 2:
            raise PDSXCommandError("CAMZOOM: camera_id, zoom gerekli")
        
        camera_id = int(self.evaluate_expression(args[0], context))
        zoom = float(self.evaluate_expression(args[1], context))
        
        success = self.camera_system.set_zoom(camera_id, zoom)
        
        if self.interpreter.debug_mode:
            print(f"[CAMERA] Set camera {camera_id} zoom to {zoom}")
        
        return success
    
    def cmd_camera_follow(self, args: List[str], context: Dict[str, Any] = None):
        """
        CAMFOLLOW - Make camera follow sprite
        
        Syntax: CAMFOLLOW camera_id, sprite_id, speed, offset_x, offset_y
        
        Args:
            camera_id: Camera ID
            sprite_id: Sprite to follow
            speed: Follow speed (0.0-10.0)
            offset_x, offset_y: Camera offset from sprite
        
        Returns: True if successful
        
        Example: CAMFOLLOW 1, 5, 3.0, 0, 0
        """
        if len(args) < 5:
            raise PDSXCommandError("CAMFOLLOW: camera_id, sprite_id, speed, offset_x, offset_y gerekli")
        
        camera_id = int(self.evaluate_expression(args[0], context))
        sprite_id = int(self.evaluate_expression(args[1], context))
        speed = float(self.evaluate_expression(args[2], context))
        offset_x = float(self.evaluate_expression(args[3], context))
        offset_y = float(self.evaluate_expression(args[4], context))
        
        success = self.camera_system.follow_target(camera_id, sprite_id, speed, offset_x, offset_y)
        
        if self.interpreter.debug_mode:
            print(f"[CAMERA] Camera {camera_id} following sprite {sprite_id}")
        
        return success
    
    def cmd_camera_shake(self, args: List[str], context: Dict[str, Any] = None):
        """
        CAMSHAKE - Trigger camera shake
        
        Syntax: CAMSHAKE camera_id, intensity, duration
        
        Args:
            camera_id: Camera ID
            intensity: Shake intensity
            duration: Duration in seconds
        
        Returns: True if successful
        
        Example: CAMSHAKE 1, 10.0, 0.5
        """
        if len(args) < 3:
            raise PDSXCommandError("CAMSHAKE: camera_id, intensity, duration gerekli")
        
        camera_id = int(self.evaluate_expression(args[0], context))
        intensity = float(self.evaluate_expression(args[1], context))
        duration = float(self.evaluate_expression(args[2], context))
        
        success = self.camera_system.screen_shake(camera_id, intensity, duration)
        
        if self.interpreter.debug_mode:
            print(f"[CAMERA] Shake camera {camera_id} intensity={intensity} duration={duration}s")
        
        return success
    
    # Viewport Commands
    
    def cmd_viewport_create(self, args: List[str], context: Dict[str, Any] = None):
        """
        VIEWPORT - Create viewport
        
        Syntax: VIEWPORT x, y, width, height, camera_id
        
        Args:
            x, y: Viewport screen position
            width, height: Viewport size
            camera_id: Camera to use
        
        Returns: Viewport ID
        
        Example: vp = VIEWPORT 0, 0, 400, 600, 1
        """
        if len(args) < 5:
            raise PDSXCommandError("VIEWPORT: x, y, width, height, camera_id gerekli")
        
        x = int(self.evaluate_expression(args[0], context))
        y = int(self.evaluate_expression(args[1], context))
        width = int(self.evaluate_expression(args[2], context))
        height = int(self.evaluate_expression(args[3], context))
        camera_id = int(self.evaluate_expression(args[4], context))
        
        viewport_id = self.viewport_manager.create_viewport(x, y, width, height, camera_id)
        
        if self.interpreter.debug_mode:
            print(f"[VIEWPORT] Created viewport {viewport_id} at ({x}, {y}) size={width}x{height}")
        
        return viewport_id
    
    def cmd_viewport_camera(self, args: List[str], context: Dict[str, Any] = None):
        """
        VIEWCAM - Set viewport camera
        
        Syntax: VIEWCAM viewport_id, camera_id
        
        Args:
            viewport_id: Viewport ID
            camera_id: Camera ID
        
        Returns: True if successful
        
        Example: VIEWCAM 1, 2
        """
        if len(args) < 2:
            raise PDSXCommandError("VIEWCAM: viewport_id, camera_id gerekli")
        
        viewport_id = int(self.evaluate_expression(args[0], context))
        camera_id = int(self.evaluate_expression(args[1], context))
        
        success = self.viewport_manager.set_viewport_camera(viewport_id, camera_id)
        
        if self.interpreter.debug_mode:
            print(f"[VIEWPORT] Set viewport {viewport_id} camera to {camera_id}")
        
        return success
    
    def cmd_viewport_active(self, args: List[str], context: Dict[str, Any] = None):
        """
        VIEWACTIVE - Set viewport active state
        
        Syntax: VIEWACTIVE viewport_id, active
        
        Args:
            viewport_id: Viewport ID
            active: 1=active, 0=inactive
        
        Returns: True if successful
        
        Example: VIEWACTIVE 1, 1
        """
        if len(args) < 2:
            raise PDSXCommandError("VIEWACTIVE: viewport_id, active gerekli")
        
        viewport_id = int(self.evaluate_expression(args[0], context))
        active = bool(int(self.evaluate_expression(args[1], context)))
        
        success = self.viewport_manager.set_viewport_active(viewport_id, active)
        
        if self.interpreter.debug_mode:
            print(f"[VIEWPORT] Set viewport {viewport_id} active={active}")
        
        return success
    
    # Render Layer Commands
    
    def cmd_layer_create(self, args: List[str], context: Dict[str, Any] = None):
        """
        LAYERCREATE - Create render layer
        
        Syntax: LAYERCREATE name, order, blend_mode, opacity
        
        Args:
            name: Layer name
            order: Render order (0-100)
            blend_mode: "normal", "additive", "multiply", "screen", "overlay"
            opacity: Opacity (0.0-1.0)
        
        Returns: Layer ID
        
        Example: layer = LAYERCREATE "background", 0, "normal", 1.0
        """
        if len(args) < 4:
            raise PDSXCommandError("LAYERCREATE: name, order, blend_mode, opacity gerekli")
        
        name = str(self.evaluate_expression(args[0], context))
        order = int(self.evaluate_expression(args[1], context))
        blend_mode = str(self.evaluate_expression(args[2], context))
        opacity = float(self.evaluate_expression(args[3], context))
        
        layer_id = self.render_layer_manager.create_layer(name, order, blend_mode, opacity)
        
        if self.interpreter.debug_mode:
            print(f"[LAYER] Created layer {layer_id} '{name}' order={order} blend={blend_mode}")
        
        return layer_id
    
    def cmd_layer_add_sprite(self, args: List[str], context: Dict[str, Any] = None):
        """
        LAYERADD - Add sprite to layer
        
        Syntax: LAYERADD layer_id, sprite_id
        
        Args:
            layer_id: Layer ID
            sprite_id: Sprite ID
        
        Returns: True if successful
        
        Example: LAYERADD 1, 5
        """
        if len(args) < 2:
            raise PDSXCommandError("LAYERADD: layer_id, sprite_id gerekli")
        
        layer_id = int(self.evaluate_expression(args[0], context))
        sprite_id = int(self.evaluate_expression(args[1], context))
        
        success = self.render_layer_manager.add_sprite_to_layer(layer_id, sprite_id)
        
        if self.interpreter.debug_mode:
            print(f"[LAYER] Added sprite {sprite_id} to layer {layer_id}")
        
        return success
    
    def cmd_layer_visibility(self, args: List[str], context: Dict[str, Any] = None):
        """
        LAYERVIS - Set layer visibility
        
        Syntax: LAYERVIS layer_id, visible
        
        Args:
            layer_id: Layer ID
            visible: 1=visible, 0=hidden
        
        Returns: True if successful
        
        Example: LAYERVIS 1, 0
        """
        if len(args) < 2:
            raise PDSXCommandError("LAYERVIS: layer_id, visible gerekli")
        
        layer_id = int(self.evaluate_expression(args[0], context))
        visible = bool(int(self.evaluate_expression(args[1], context)))
        
        success = self.render_layer_manager.set_layer_visibility(layer_id, visible)
        
        if self.interpreter.debug_mode:
            print(f"[LAYER] Set layer {layer_id} visibility={visible}")
        
        return success
    
    def cmd_layer_opacity(self, args: List[str], context: Dict[str, Any] = None):
        """
        LAYEROPACITY - Set layer opacity
        
        Syntax: LAYEROPACITY layer_id, opacity
        
        Args:
            layer_id: Layer ID
            opacity: Opacity (0.0-1.0)
        
        Returns: True if successful
        
        Example: LAYEROPACITY 1, 0.5
        """
        if len(args) < 2:
            raise PDSXCommandError("LAYEROPACITY: layer_id, opacity gerekli")
        
        layer_id = int(self.evaluate_expression(args[0], context))
        opacity = float(self.evaluate_expression(args[1], context))
        
        success = self.render_layer_manager.set_layer_opacity(layer_id, opacity)
        
        if self.interpreter.debug_mode:
            print(f"[LAYER] Set layer {layer_id} opacity={opacity}")
        
        return success
    
    # Post-Processing Commands
    
    def cmd_effect_add(self, args: List[str], context: Dict[str, Any] = None):
        """
        EFFECTADD - Add post-processing effect
        
        Syntax: EFFECTADD effect_type, intensity
        
        Args:
            effect_type: "blur", "brightness", "contrast", "saturation", "vignette", "pixelate", "scanline", "crt", "bloom"
            intensity: Effect intensity (0.0-2.0)
        
        Returns: Effect ID
        
        Example: effect = EFFECTADD "blur", 0.5
        """
        if len(args) < 2:
            raise PDSXCommandError("EFFECTADD: effect_type, intensity gerekli")
        
        effect_type = str(self.evaluate_expression(args[0], context))
        intensity = float(self.evaluate_expression(args[1], context))
        
        effect_id = self.post_processor.add_effect(effect_type, intensity)
        
        if self.interpreter.debug_mode:
            print(f"[EFFECT] Added effect {effect_id} type={effect_type} intensity={intensity}")
        
        return effect_id
    
    def cmd_effect_set(self, args: List[str], context: Dict[str, Any] = None):
        """
        EFFECTSET - Set effect parameter
        
        Syntax: EFFECTSET effect_id, param_name, value
        
        Args:
            effect_id: Effect ID
            param_name: Parameter name
            value: Parameter value
        
        Returns: True if successful
        
        Example: EFFECTSET 1, "radius", 5
        """
        if len(args) < 3:
            raise PDSXCommandError("EFFECTSET: effect_id, param_name, value gerekli")
        
        effect_id = int(self.evaluate_expression(args[0], context))
        param_name = str(self.evaluate_expression(args[1], context))
        value = self.evaluate_expression(args[2], context)
        
        success = self.post_processor.set_effect_parameter(effect_id, param_name, value)
        
        if self.interpreter.debug_mode:
            print(f"[EFFECT] Set effect {effect_id} {param_name}={value}")
        
        return success
    
    def cmd_effect_clear(self, args: List[str], context: Dict[str, Any] = None):
        """
        EFFECTCLEAR - Clear all effects
        
        Syntax: EFFECTCLEAR
        
        Returns: True
        
        Example: EFFECTCLEAR
        """
        self.post_processor.clear_all_effects()
        
        if self.interpreter.debug_mode:
            print("[EFFECT] Cleared all effects")
        
        return True
    
    # ========== PHASE 6: COMPLETE GAME ENGINE COMMANDS ==========
    
    # Lighting Commands
    
    def cmd_light_point(self, args: List[str], context: Dict[str, Any] = None):
        """LIGHTPOINT - Add point light"""
        if len(args) < 7:
            raise PDSXCommandError("LIGHTPOINT: x, y, r, g, b, intensity, radius gerekli")
        
        x = float(self.evaluate_expression(args[0], context))
        y = float(self.evaluate_expression(args[1], context))
        r = int(self.evaluate_expression(args[2], context))
        g = int(self.evaluate_expression(args[3], context))
        b = int(self.evaluate_expression(args[4], context))
        intensity = float(self.evaluate_expression(args[5], context))
        radius = float(self.evaluate_expression(args[6], context))
        
        light_id = self.lighting_system.add_point_light(x, y, (r, g, b), intensity, radius)
        
        if self.interpreter.debug_mode:
            print(f"[LIGHT] Created point light {light_id}")
        
        return light_id
    
    def cmd_light_directional(self, args: List[str], context: Dict[str, Any] = None):
        """LIGHTDIR - Add directional light"""
        if len(args) < 5:
            raise PDSXCommandError("LIGHTDIR: direction, r, g, b, intensity gerekli")
        
        direction = float(self.evaluate_expression(args[0], context))
        r = int(self.evaluate_expression(args[1], context))
        g = int(self.evaluate_expression(args[2], context))
        b = int(self.evaluate_expression(args[3], context))
        intensity = float(self.evaluate_expression(args[4], context))
        
        light_id = self.lighting_system.add_directional_light(direction, (r, g, b), intensity)
        
        if self.interpreter.debug_mode:
            print(f"[LIGHT] Created directional light {light_id}")
        
        return light_id
    
    def cmd_light_spotlight(self, args: List[str], context: Dict[str, Any] = None):
        """LIGHTSPOT - Add spotlight"""
        if len(args) < 9:
            raise PDSXCommandError("LIGHTSPOT: x, y, direction, cone_angle, r, g, b, intensity, radius gerekli")
        
        x = float(self.evaluate_expression(args[0], context))
        y = float(self.evaluate_expression(args[1], context))
        direction = float(self.evaluate_expression(args[2], context))
        cone_angle = float(self.evaluate_expression(args[3], context))
        r = int(self.evaluate_expression(args[4], context))
        g = int(self.evaluate_expression(args[5], context))
        b = int(self.evaluate_expression(args[6], context))
        intensity = float(self.evaluate_expression(args[7], context))
        radius = float(self.evaluate_expression(args[8], context))
        
        light_id = self.lighting_system.add_spotlight(x, y, direction, cone_angle, (r, g, b), intensity, radius)
        
        if self.interpreter.debug_mode:
            print(f"[LIGHT] Created spotlight {light_id}")
        
        return light_id
    
    def cmd_light_position(self, args: List[str], context: Dict[str, Any] = None):
        """LIGHTPOS - Set light position"""
        if len(args) < 3:
            raise PDSXCommandError("LIGHTPOS: light_id, x, y gerekli")
        
        light_id = int(self.evaluate_expression(args[0], context))
        x = float(self.evaluate_expression(args[1], context))
        y = float(self.evaluate_expression(args[2], context))
        
        return self.lighting_system.set_light_position(light_id, x, y)
    
    def cmd_light_color(self, args: List[str], context: Dict[str, Any] = None):
        """LIGHTCOLOR - Set light color"""
        if len(args) < 4:
            raise PDSXCommandError("LIGHTCOLOR: light_id, r, g, b gerekli")
        
        light_id = int(self.evaluate_expression(args[0], context))
        r = int(self.evaluate_expression(args[1], context))
        g = int(self.evaluate_expression(args[2], context))
        b = int(self.evaluate_expression(args[3], context))
        
        return self.lighting_system.set_light_color(light_id, r, g, b)
    
    def cmd_ambient_light(self, args: List[str], context: Dict[str, Any] = None):
        """AMBIENT - Set ambient light"""
        if len(args) < 4:
            raise PDSXCommandError("AMBIENT: r, g, b, intensity gerekli")
        
        r = int(self.evaluate_expression(args[0], context))
        g = int(self.evaluate_expression(args[1], context))
        b = int(self.evaluate_expression(args[2], context))
        intensity = float(self.evaluate_expression(args[3], context))
        
        self.lighting_system.set_ambient_light((r, g, b), intensity)
        return True
    
    # Particle Commands
    
    def cmd_particle_emitter(self, args: List[str], context: Dict[str, Any] = None):
        """PEMIT - Create particle emitter"""
        if len(args) < 3:
            raise PDSXCommandError("PEMIT: x, y, rate gerekli")
        
        x = float(self.evaluate_expression(args[0], context))
        y = float(self.evaluate_expression(args[1], context))
        rate = float(self.evaluate_expression(args[2], context))
        
        emitter_id = self.particle_system.create_emitter(x, y, emission_rate=rate)
        
        if self.interpreter.debug_mode:
            print(f"[PARTICLE] Created emitter {emitter_id}")
        
        return emitter_id
    
    def cmd_particle_preset(self, args: List[str], context: Dict[str, Any] = None):
        """PPRESET - Create preset emitter"""
        if len(args) < 3:
            raise PDSXCommandError("PPRESET: preset_name, x, y gerekli")
        
        preset = str(self.evaluate_expression(args[0], context))
        x = float(self.evaluate_expression(args[1], context))
        y = float(self.evaluate_expression(args[2], context))
        
        emitter_id = self.particle_system.create_preset_emitter(preset, x, y)
        
        if self.interpreter.debug_mode:
            print(f"[PARTICLE] Created {preset} emitter {emitter_id}")
        
        return emitter_id
    
    def cmd_particle_burst(self, args: List[str], context: Dict[str, Any] = None):
        """PBURST - Emit particle burst"""
        if len(args) < 2:
            raise PDSXCommandError("PBURST: emitter_id, count gerekli")
        
        emitter_id = int(self.evaluate_expression(args[0], context))
        count = int(self.evaluate_expression(args[1], context))
        
        return self.particle_system.burst(emitter_id, count)
    
    def cmd_particle_update(self, args: List[str], context: Dict[str, Any] = None):
        """PUPDATE - Update particle system"""
        if len(args) < 1:
            raise PDSXCommandError("PUPDATE: delta_time gerekli")
        
        delta_time = float(self.evaluate_expression(args[0], context))
        self.particle_system.update(delta_time)
        return True
    
    # Audio Commands
    
    def cmd_sound_load(self, args: List[str], context: Dict[str, Any] = None):
        """SOUNDLOAD - Load sound effect"""
        if len(args) < 1:
            raise PDSXCommandError("SOUNDLOAD: filepath gerekli")
        
        filepath = str(self.evaluate_expression(args[0], context))
        sound_id = self.audio_system.load_sound(filepath)
        
        if self.interpreter.debug_mode:
            print(f"[AUDIO] Loaded sound {sound_id}: {filepath}")
        
        return sound_id
    
    def cmd_sound_play(self, args: List[str], context: Dict[str, Any] = None):
        """SOUNDPLAY - Play sound"""
        if len(args) < 1:
            raise PDSXCommandError("SOUNDPLAY: sound_id gerekli")
        
        sound_id = int(self.evaluate_expression(args[0], context))
        volume = float(self.evaluate_expression(args[1], context)) if len(args) > 1 else 1.0
        
        return self.audio_system.play_sound(sound_id, volume)
    
    def cmd_sound_play_3d(self, args: List[str], context: Dict[str, Any] = None):
        """SOUNDPLAY3D - Play 3D sound"""
        if len(args) < 4:
            raise PDSXCommandError("SOUNDPLAY3D: sound_id, x, y, volume gerekli")
        
        sound_id = int(self.evaluate_expression(args[0], context))
        x = float(self.evaluate_expression(args[1], context))
        y = float(self.evaluate_expression(args[2], context))
        volume = float(self.evaluate_expression(args[3], context))
        
        return self.audio_system.play_sound_3d(sound_id, x, y, volume)
    
    def cmd_music_load(self, args: List[str], context: Dict[str, Any] = None):
        """MUSICLOAD - Load music"""
        if len(args) < 1:
            raise PDSXCommandError("MUSICLOAD: filepath gerekli")
        
        filepath = str(self.evaluate_expression(args[0], context))
        return self.audio_system.load_music(filepath)
    
    def cmd_music_play(self, args: List[str], context: Dict[str, Any] = None):
        """MUSICPLAY - Play music"""
        loop = bool(int(self.evaluate_expression(args[0], context))) if len(args) > 0 else True
        fade_in = float(self.evaluate_expression(args[1], context)) if len(args) > 1 else 0.0
        
        return self.audio_system.play_music(loop, fade_in)
    
    def cmd_volume(self, args: List[str], context: Dict[str, Any] = None):
        """VOLUME - Set volume"""
        if len(args) < 2:
            raise PDSXCommandError("VOLUME: type, level gerekli")
        
        vol_type = str(self.evaluate_expression(args[0], context))
        level = float(self.evaluate_expression(args[1], context))
        
        if vol_type == "master":
            self.audio_system.set_master_volume(level)
        elif vol_type == "sfx":
            self.audio_system.set_sfx_volume(level)
        elif vol_type == "music":
            self.audio_system.set_music_volume(level)
        
        return True
    
    # Physics Commands
    
    def cmd_body_create(self, args: List[str], context: Dict[str, Any] = None):
        """BODYCREATE - Create rigid body"""
        if len(args) < 4:
            raise PDSXCommandError("BODYCREATE: sprite_id, type, x, y gerekli")
        
        sprite_id = int(self.evaluate_expression(args[0], context))
        body_type = str(self.evaluate_expression(args[1], context))
        x = float(self.evaluate_expression(args[2], context))
        y = float(self.evaluate_expression(args[3], context))
        
        body_id = self.physics_engine.create_body(sprite_id, body_type, x, y)
        
        if self.interpreter.debug_mode:
            print(f"[PHYSICS] Created {body_type} body {body_id}")
        
        return body_id
    
    def cmd_body_force(self, args: List[str], context: Dict[str, Any] = None):
        """BODYFORCE - Apply force"""
        if len(args) < 3:
            raise PDSXCommandError("BODYFORCE: body_id, fx, fy gerekli")
        
        body_id = int(self.evaluate_expression(args[0], context))
        fx = float(self.evaluate_expression(args[1], context))
        fy = float(self.evaluate_expression(args[2], context))
        
        self.physics_engine.apply_force(body_id, fx, fy)
        return True
    
    def cmd_body_impulse(self, args: List[str], context: Dict[str, Any] = None):
        """BODYIMPULSE - Apply impulse"""
        if len(args) < 3:
            raise PDSXCommandError("BODYIMPULSE: body_id, ix, iy gerekli")
        
        body_id = int(self.evaluate_expression(args[0], context))
        ix = float(self.evaluate_expression(args[1], context))
        iy = float(self.evaluate_expression(args[2], context))
        
        self.physics_engine.apply_impulse(body_id, ix, iy)
        return True
    
    def cmd_body_velocity(self, args: List[str], context: Dict[str, Any] = None):
        """BODYVEL - Set velocity"""
        if len(args) < 3:
            raise PDSXCommandError("BODYVEL: body_id, vx, vy gerekli")
        
        body_id = int(self.evaluate_expression(args[0], context))
        vx = float(self.evaluate_expression(args[1], context))
        vy = float(self.evaluate_expression(args[2], context))
        
        self.physics_engine.set_velocity(body_id, vx, vy)
        return True
    
    def cmd_physics_step(self, args: List[str], context: Dict[str, Any] = None):
        """PHYSSTEP - Update physics"""
        if len(args) < 1:
            raise PDSXCommandError("PHYSSTEP: delta_time gerekli")
        
        delta_time = float(self.evaluate_expression(args[0], context))
        self.physics_engine.step(delta_time)
        return True




