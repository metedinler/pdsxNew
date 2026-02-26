#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDSX-X Modular Interpreter
===========================
Modern BASIC interpreter with modular command system.

Date: 22 Ekim 2025
Author: GitHub Copilot + Human
"""

# ============================================================================
# KRITIK: VENV KONTROLÜ - İMPORT'LARDAN ÖNCE!
# ============================================================================
# Eğer venv varsa ve şu an venv içinde DEĞİLsek, önce venv'e geç!
# Yoksa import sırasında ModuleNotFoundError alırız.
# ============================================================================

import os
import sys
from pathlib import Path

# Venv kontrolü
if __name__ == '__main__':
    project_dir = Path(__file__).parent.absolute()
    venv_dir = project_dir / "pdsxu_venv"
    
    # Windows ve Linux için venv Python path'leri
    if sys.platform == "win32":
        venv_python = venv_dir / "Scripts" / "python.exe"
    else:
        venv_python = venv_dir / "bin" / "python"
    
    # Eğer venv var VE şu an venv içinde DEĞİLsek
    if venv_python.exists() and not sys.executable.startswith(str(venv_dir)):
        # Unicode karakterler yerine ASCII (Windows konsol uyumluluğu)
        print(">> Sanal ortam tespit edildi, yeniden baslatiliyor...")
        print(f"   Global Python: {sys.executable}")
        print(f"   Venv Python:   {venv_python}")
        print()
        
        import subprocess
        
        # Tüm argümanları al (script adı hariç)
        args_to_pass = sys.argv[1:]
        
        # Venv Python ile yeniden başlat
        cmd = [str(venv_python), __file__] + args_to_pass
        
        try:
            # subprocess.run ile çalıştır ve çıkış kodunu al
            result = subprocess.run(cmd)
            sys.exit(result.returncode)
        except KeyboardInterrupt:
            print("\n⚠️  Program durduruldu")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Venv başlatma hatası: {e}")
            sys.exit(1)

# ============================================================================
# NORMAL IMPORT'LAR (artık venv içindeyiz veya venv yok)
# ============================================================================

import re
from typing import Dict, Any, List, Optional, Callable
from collections import defaultdict

# Pygame mesajını gizle (import öncesi)
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

# Import modular commands
from pdsx_commands import (
    BaseCommand,
    PDSXCommandError,
    CoreCommands,
    VariableManager,
    FlowControl,
    LoopControl,
    FunctionManager,
    OOPCommands,
    DataStructures,
    StringOperations,
    MathOperations,
    FileOperations,
    EventSystem,
    DatabaseOperations,
    NetworkOperations
)


class PDSXInterpreter:
    """PDSX-X Ana Interpreter Sınıfı"""
    
    def __init__(self):
        """Interpreter'ı başlat"""
        # Komut registry
        self.commands: Dict[str, Any] = {}
        
        # Context (paylaşılan state)
        self.context = {
            # Değişkenler
            'variables': {
                'PI': 3.141592653589793,
                'E': 2.718281828459045,
            },
            'constants': {},
            'global_vars': {},  # Dict olmalı, set değil!
            
            # Fonksiyonlar
            'functions': {},
            'def_fns': {},
            
            # Akış kontrolü
            'labels': {},
            'gosub_stack': [],
            
            # Döngüler
            'for_loops': [],
            'while_loops': [],
            'do_loops': [],
            'loop_stack': [],  # FOR-NEXT için loop stack
            
            # OOP
            '__oop_mode__': 'OOP1',
            '__current_yapi__': None,
            '__current_clazz__': None,
            '__current_class__': None,
            '__yapiler__': {},
            '__clazzlar__': {},
            '__classes__': {},
            '__instances__': {},
            '__mixins__': {},
            
            # Veri yapıları
            '__structs__': {},
            '__unions__': {},
            '__enums__': {},
            
            # Grafik sistemi modu (PHASE 0 - 24 Ekim 2025)
            '__graphics_mode__': 0,  # 0=OFF, 1=LEGACY (terminal), 2=ADVANCED (pygame)
            
            # Diğer
            '__line_number__': 0,
            '__program_lines__': [],
            '__running__': True,
        }
        
        # Program state
        self.program_lines: List[str] = []
        self.current_line: int = 0
        self.running: bool = False
        
        # Debug/Trace modes
        self.debug_mode: bool = False
        self.trace_mode: bool = False
        
        # Test directory
        self.test_directory: str = os.path.join(os.path.dirname(__file__), 'tests')
        
        # Virtual Environment Manager'ı başlat (paket yönetimi için)
        self._setup_virtual_environment()
        
        # Modülleri başlat
        self._init_modules()
    
    def _setup_virtual_environment(self):
        """Virtual Environment Manager ile eksik paketleri kontrol et"""
        try:
            if os.environ.get('PDSX_DISABLE_AUTO_DEP_INSTALL', '').strip() in ('1', 'true', 'TRUE', 'yes', 'YES'):
                return

            # Bu noktada zaten sanal ortamdayız (main() kontrol etti)
            # Sadece eksik paketleri kontrol et ve cache'den kur
            from pdsx_commands.virtual_env_manager import VirtualEnvironmentManager
            
            project_dir = os.path.dirname(os.path.abspath(__file__))
            legacy_venv_dir = os.path.join(project_dir, 'pdsxu_venv')

            if not os.path.isdir(legacy_venv_dir):
                if self.debug_mode:
                    print(f"[DEBUG] Legacy venv bulunamadi, auto paket kontrolu atlandi: {legacy_venv_dir}")
                return

            venv_manager = VirtualEnvironmentManager(project_dir=project_dir)
            
            # Eksik paketleri sessizce kontrol et ve kur
            venv_manager.validate_and_install_missing()
                    
        except Exception as e:
            # Hata sadece debug modda göster
            if self.debug_mode:
                print(f"⚠️  Paket kontrolü hatası: {e}")
        
    def _init_modules(self):
        """Tüm komut modüllerini başlat"""
        if self.debug_mode:
            print("Moduller yukleniyor...")
        
        # Her modülü başlat
        self.core = CoreCommands(self)
        if self.debug_mode:
            print("  [OK] CoreCommands yuklendi")
        
        self.variables = VariableManager(self)
        if self.debug_mode:
            print("  [OK] VariableManager yuklendi")
        
        self.flow = FlowControl(self)
        if self.debug_mode:
            print("  [OK] FlowControl yuklendi")
        
        self.loops = LoopControl(self)
        if self.debug_mode:
            print("  [OK] LoopControl yuklendi")
        
        self.functions = FunctionManager(self)
        if self.debug_mode:
            print("  [OK] FunctionManager yuklendi")
        
        self.oop = OOPCommands(self)
        if self.debug_mode:
            print("  [OK] OOPCommands yuklendi")
        
        self.data_structures = DataStructures(self)
        if self.debug_mode:
            print("  [OK] DataStructures yuklendi")
        
        self.strings = StringOperations(self)
        if self.debug_mode:
            print("  [OK] StringOperations yuklendi")
        
        self.math = MathOperations(self)
        if self.debug_mode:
            print("  [OK] MathOperations yuklendi")
        
        # YENİ MODÜLLER
        self.files = FileOperations(self)
        if self.debug_mode:
            print("  [OK] FileOperations yuklendi")
        
        self.events = EventSystem(self)
        if self.debug_mode:
            print("  [OK] EventSystem yuklendi")
        
        self.database = DatabaseOperations(self)
        if self.debug_mode:
            print("  [OK] DatabaseOperations yuklendi")
        
        self.network = NetworkOperations(self)
        if self.debug_mode:
            print("  [OK] NetworkOperations yuklendi")
        
        # Advanced modules from pdsxextra.py (23 Ekim 2025)
        try:
            from pdsx_commands.exception_handling import ExceptionHandling
            from pdsx_commands.namespace_system import NamespaceSystem
            from pdsx_commands.advanced_types import AdvancedTypes
            from pdsx_commands.threading_system import ThreadingSystem
            from pdsx_commands.debug_system import DebugSystem
            from pdsx_commands.memory_system import MemorySystem
            from pdsx_commands.ml_system import MLSystem
            from pdsx_commands.advanced_operators import AdvancedOperators
            from pdsx_commands.regex_operations import RegexOperations
            
            # NEW: Type System Enhancements (29 Ekim 2025)
            from pdsx_commands.type_functions import TypeFunctions
            from pdsx_commands.cast_system import CastSystem
            from pdsx_commands.nesting_validator import NestingValidator
            
            self.exceptions = ExceptionHandling(self)
            if self.debug_mode:
                print("  [OK] ExceptionHandling yuklendi")
            
            self.namespaces = NamespaceSystem(self)
            if self.debug_mode:
                print("  [OK] NamespaceSystem yuklendi")
            
            self.advanced_types = AdvancedTypes(self)
            if self.debug_mode:
                print("  [OK] AdvancedTypes yuklendi")
            
            self.threading = ThreadingSystem(self)
            if self.debug_mode:
                print("  [OK] ThreadingSystem yuklendi")
            
            self.debug = DebugSystem(self)
            if self.debug_mode:
                print("  [OK] DebugSystem yuklendi")
            
            self.memory = MemorySystem(self)
            if self.debug_mode:
                print("  [OK] MemorySystem yuklendi")
            
            # NEW: Type introspection functions
            try:
                self.type_functions = TypeFunctions(self)
                if self.debug_mode:
                    print("  [OK] TypeFunctions yuklendi")
            except Exception as e:
                if self.debug_mode:
                    print(f"  [WARN] TypeFunctions yuklenemedi: {e}")
            
            # NEW: Cast system
            try:
                self.cast_system = CastSystem(self)
                if self.debug_mode:
                    print("  [OK] CastSystem yuklendi")
            except Exception as e:
                if self.debug_mode:
                    print(f"  [WARN] CastSystem yuklenemedi: {e}")
            
            # NEW: Nesting validator
            try:
                self.nesting_validator = NestingValidator(self)
                if self.debug_mode:
                    print("  [OK] NestingValidator yuklendi")
            except Exception as e:
                if self.debug_mode:
                    print(f"  [WARN] NestingValidator yuklenemedi: {e}")
            
            try:
                self.ml = MLSystem(self)
                if self.debug_mode:
                    print("  [OK] MLSystem yuklendi")
            except Exception as e:
                if self.debug_mode:
                    print(f"  [WARN] MLSystem yuklenemedi: {e}")
            
            try:
                self.advanced_ops = AdvancedOperators(self)
                if self.debug_mode:
                    print("  [OK] AdvancedOperators yuklendi")
            except Exception as e:
                if self.debug_mode:
                    print(f"  [WARN] AdvancedOperators yuklenemedi: {e}")
            
            self.regex = RegexOperations(self)
            if self.debug_mode:
                print("  [OK] RegexOperations yuklendi")
        except ImportError as e:
            if self.debug_mode:
                print(f"  [WARN] Advanced modules kısmen yüklendi: {e}")
        
        # AI/Logic Programming and API Integration (23 Ekim 2025)
        try:
            from pdsx_commands.prolog_system import PrologSystem
            from pdsx_commands.nlp_system import NLPSystem
            from pdsx_commands.github_operations import GitHubOperations
            from pdsx_commands.rest_api_system import RestAPISystem
            from pdsx_commands.dll_system import DLLSystem
            
            try:
                self.prolog = PrologSystem(self)
                if self.debug_mode:
                    print("  [OK] PrologSystem yuklendi")
            except Exception as e:
                if self.debug_mode:
                    print(f"  [WARN] PrologSystem yuklenemedi: {e}")
            
            try:
                self.nlp = NLPSystem(self)
                if self.debug_mode:
                    print("  [OK] NLPSystem yuklendi")
            except Exception as e:
                if self.debug_mode:
                    print(f"  [WARN] NLPSystem yuklenemedi: {e}")
            
            try:
                self.github = GitHubOperations(self)
                if self.debug_mode:
                    print("  [OK] GitHubOperations yuklendi")
            except Exception as e:
                if self.debug_mode:
                    print(f"  [WARN] GitHubOperations yuklenemedi: {e}")
            
            try:
                self.rest_api = RestAPISystem(self)
                if self.debug_mode:
                    print("  [OK] RestAPISystem yuklendi")
            except Exception as e:
                if self.debug_mode:
                    print(f"  [WARN] RestAPISystem yuklenemedi: {e}")
            
            try:
                self.dll = DLLSystem(self)
                if self.debug_mode:
                    print("  [OK] DLLSystem yuklendi")
            except Exception as e:
                if self.debug_mode:
                    print(f"  [WARN] DLLSystem yuklenemedi: {e}")
        except ImportError as e:
            if self.debug_mode:
                print(f"  [WARN] AI/API modules kısmen yüklendi: {e}")
        
        # Data Science and Functional Programming (23 Ekim 2025)
        try:
            from pdsx_commands.statistical_tests import StatisticalTests
            from pdsx_commands.numpy_operations import NumpyOperations
            from pdsx_commands.pandas_operations import PandasOperations
            from pdsx_commands.linq_operations import LinqOperations
            from pdsx_commands.graphics_system import GraphicsSystem
            
            self.statistical_tests = StatisticalTests(self)
            if self.debug_mode:
                print("  [OK] StatisticalTests yuklendi (131 komut)")
            
            self.numpy_operations = NumpyOperations(self)
            if self.debug_mode:
                print("  [OK] NumpyOperations yuklendi (60 komut)")
            
            self.pandas_operations = PandasOperations(self)
            if self.debug_mode:
                print("  [OK] PandasOperations yuklendi (65 komut)")
            
            self.linq_operations = LinqOperations(self)
            if self.debug_mode:
                print("  [OK] LinqOperations yuklendi (31 komut)")
            
            self.graphics_system = GraphicsSystem(self)
            if self.debug_mode:
                print("  [OK] GraphicsSystem yuklendi (72 komut)")
        except ImportError as e:
            if self.debug_mode:
                print(f"  [WARN] Data Science modules kısmen yüklendi: {e}")
        
        if self.debug_mode:
            print(f"[OK] Toplam {len(self.commands)} komut kaydedildi")
            print()
        
    def register_command(self, name: str, handler: Any, description: str = "", syntax: str = ""):
        """Komut kaydet (flexible signature for compatibility)"""
        self.commands[name.upper()] = handler
        
    def load_program(self, filename: str):
        """Program dosyasını yükle"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.program_lines = [line.rstrip() for line in f.readlines()]
            self.context['__program_lines__'] = self.program_lines
            if self.debug_mode:
                print(f"[OK] Program yuklendi: {filename} ({len(self.program_lines)} satir)")
            return True
        except FileNotFoundError:
            print(f"[HATA] Dosya bulunamadi: {filename}")
            return False
        except Exception as e:
            print(f"[HATA] {e}")
            return False
    
    def parse_line(self, line: str) -> Optional[tuple]:
        """Satırı parse et ve komut + argümanları döndür"""
        # Boş satır veya yorum
        line = line.strip()
        if not line or line.startswith('REM') or line.startswith("'"):
            return None
            
        # Satır numarasını kaldır (eski BASIC tarzı)
        if line and line[0].isdigit():
            parts = line.split(None, 1)
            if len(parts) > 1:
                line = parts[1]
            else:
                return None
        
        # Komut ve argümanları ayır
        
        # İlk kelimeyi al
        first_word = line.split()[0].upper() if line.split() else ''
        
        # Eğer PRINT, REM, IF gibi bilinen komutlarla başlıyorsa, özel işlem yapma
        skip_operator_check = ['PRINT', 'REM', 'IF', 'WHILE', 'FOR', 'DIM', 'INPUT', 'CLS', 'END']
        
        # Önce increment/decrement operatörlerini kontrol et (++, --)
        # ANCAK sadece başka komut değilse
        if first_word not in skip_operator_check:
            if '++' in line or '--' in line:
                # A++, ++A, A--, --A formatları
                line_stripped = line.strip()
                if line_stripped.endswith('++'):
                    # Postfix: A++
                    var_name = line_stripped[:-2].strip()
                    return ('INCREMENT', [var_name, 'post'])
                elif line_stripped.startswith('++'):
                    # Prefix: ++A
                    var_name = line_stripped[2:].strip()
                    return ('INCREMENT', [var_name, 'pre'])
                elif line_stripped.endswith('--'):
                    # Postfix: A--
                    var_name = line_stripped[:-2].strip()
                    return ('DECREMENT', [var_name, 'post'])
                elif line_stripped.startswith('--'):
                    # Prefix: --A
                    var_name = line_stripped[2:].strip()
                    return ('DECREMENT', [var_name, 'pre'])
            
            # Compound assignment operatörlerini kontrol et (+=, -=, *=, /=, %=, etc.)
            # ANCAK sadece başka komut değilse
            compound_ops = ['+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', '<<=', '>>=']
            for op in compound_ops:
                if op in line:
                    parts = line.split(op, 1)
                    if len(parts) == 2:
                        var_name = parts[0].strip()
                        expression = parts[1].strip()
                        # Operator ismini al (+=, -= vs)
                        return ('COMPOUND_ASSIGN', [var_name, op, expression])
        
        # Önce = işaretini kontrol et (assignment)
        # ANCAK FOR, IF, WHILE, DIM, PRINT gibi özel komutları hariç tut
        excluded_starts = ('IF', 'ELSEIF', 'ELSE', 'WHILE', 'FOR', 'DIM', 'PRINT', 'INPUT', 'LINE', 'UNTIL', 'DO')
        line_upper_start = line.upper().split()[0] if line.split() else ''
        
        if '=' in line and line_upper_start not in excluded_starts:
            # LET x = 5 veya x = 5
            if line.upper().startswith('LET '):
                # LET komutunu koru, sadece expression'ı birleştir
                parts = line.split(None, 1)  # ['LET', 'x = 5']
                if len(parts) > 1:
                    assignment = parts[1]  # 'x = 5'
                    var_parts = assignment.split('=', 1)
                    if len(var_parts) == 2:
                        var_name = var_parts[0].strip()
                        expression = var_parts[1].strip()
                        return ('LET', [var_name, '=', expression])
            else:
                # Direkt assignment: x = 5
                parts = line.split('=', 1)
                var_name = parts[0].strip()
                expression = parts[1].strip()
                return ('LET', [var_name, '=', expression])
        
        # Multi-word komutları kontrol et
        line_upper = line.upper()
        multi_word_commands = [
            'FOR EACH', 'LINE INPUT', 'END IF', 'END FUNCTION', 'END SUB', 'END CLASS',
            'END WHILE', 'END FOR', 'END SELECT', 'CASE ELSE', 'END YAPI',
            'END CLAZZ', 'END STRUCT', 'END UNION', 'END ENUM', 'END TYPE', 'END METHOD',
            'CREATE IMAGE SPRITE', 'CREATE ASCII SPRITE', 'DRAW SPRITE', 'COLLISION ON', 'COLLISION OFF',
            'END_IF', 'END_FUNCTION', 'END_SUB', 'END_CLASS', 'END_WHILE', 'END_FOR',
            'END_SELECT', 'END_YAPI', 'END_CLAZZ', 'END_STRUCT', 'END_UNION', 'END_ENUM', 'END_TYPE', 'END_METHOD',
            'EXIT FOR', 'EXIT WHILE', 'EXIT DO', 'CONTINUE FOR', 'CONTINUE WHILE',
            'CONTINUE DO', 'ON EVENT', 'ON ERROR', 'DO EACH', 'ELSE IF', 'ELSEIF'
        ]
        
        command = None
        args_str = ""
        
        # Multi-word command kontrolü
        for multi_cmd in multi_word_commands:
            if line_upper.startswith(multi_cmd):
                command = multi_cmd.replace(' ', '_')  # FOR EACH -> FOR_EACH
                args_str = line[len(multi_cmd):].strip()
                break
        
        # Multi-word değilse, tek kelime komut
        if command is None:
            parts = line.split(None, 1)
            if not parts:
                return None
            command = parts[0].upper()
            args_str = parts[1] if len(parts) > 1 else ""
        
        # Argümanları parse et
        args = self._parse_arguments(args_str)
        
        return (command, args)
    
    def _parse_arguments(self, args_str: str) -> List[str]:
        """Argüman string'ini liste olarak parse et"""
        if not args_str:
            return []
        
        # INPUT ve PRINT için özel durum - tüm argümanı tek parça olarak döndür
        # Çünkü bu komutlar noktalı virgül ve virgül ayrımını kendileri yapıyor
        # Örnek: INPUT "prompt"; var1, var2 -> ["prompt"; var1, var2] olarak kalmalı
        
        # Basit yaklaşım: Sadece boşluklarla ayır, virgül ve noktalı virgülü koru
        # ANCAK tırnak içindeki ve parantez içindeki kısımları koruyarak
        args = []
        current_arg = ""
        in_quotes = False
        in_parens = 0
        
        for char in args_str:
            if char == '"' and (not current_arg or current_arg[-1] != '\\'):
                in_quotes = not in_quotes
                current_arg += char
            elif char == '(' and not in_quotes:
                in_parens += 1
                current_arg += char
            elif char == ')' and not in_quotes:
                in_parens -= 1
                current_arg += char
            elif char == ' ' and not in_quotes and in_parens == 0 and not current_arg.strip():
                # Boşluk - ama sadece başta/sonda değilse atla
                continue
            else:
                current_arg += char
        
        # Tüm argümanı tek parça olarak döndür (INPUT, PRINT vs için)
        if current_arg.strip():
            # Ama bazı komutlar için virgülle ayırmak gerekebilir
            # Şimdilik tüm argümanı tek string olarak dön
            return [current_arg.strip()]
        
        return []
    
    def evaluate_expression(self, expr: str, context: Optional[Dict] = None) -> Any:
        """
        İfadeyi değerlendir (matematik, string, değişken, fonksiyon çağrısı, vb.)
        """
        if context is None:
            context = self.context
        
        expr = str(expr).strip()
        
        # Boş expression
        if not expr:
            return ""
        
        # String literal
        if expr.startswith('"') and expr.endswith('"'):
            return expr[1:-1]
        
        # Sayı
        try:
            if '.' in expr:
                return float(expr)
            else:
                return int(expr)
        except ValueError:
            pass
        
        # Boolean
        if expr.upper() == 'TRUE':
            return True
        elif expr.upper() == 'FALSE':
            return False
        
        # Fonksiyon çağrısı (gelişmiş - önce kontrol et)
        if '(' in expr and ')' in expr:
            # Fonksiyon adını ve argümanları ayır
            paren_pos = expr.index('(')
            func_name = expr[:paren_pos].strip().upper()
            
            # Parantez içini bul
            paren_start = paren_pos
            paren_count = 0
            paren_end = -1
            for i in range(paren_start, len(expr)):
                if expr[i] == '(':
                    paren_count += 1
                elif expr[i] == ')':
                    paren_count -= 1
                    if paren_count == 0:
                        paren_end = i
                        break
            
            if paren_end > paren_start:
                args_str = expr[paren_start + 1:paren_end]
                
                # Argümanları parse et (virgülle ayır ama parantez/tırnak içindekiler hariç)
                args = []
                if args_str.strip():
                    current_arg = ""
                    in_quotes = False
                    in_parens = 0
                    
                    for char in args_str:
                        if char == '"':
                            in_quotes = not in_quotes
                            current_arg += char
                        elif char == '(' and not in_quotes:
                            in_parens += 1
                            current_arg += char
                        elif char == ')' and not in_quotes:
                            in_parens -= 1
                            current_arg += char
                        elif char == ',' and not in_quotes and in_parens == 0:
                            args.append(self.evaluate_expression(current_arg.strip(), context))
                            current_arg = ""
                        else:
                            current_arg += char
                    
                    if current_arg.strip():
                        args.append(self.evaluate_expression(current_arg.strip(), context))
                
                # Komut veya fonksiyon olarak çağır
                if func_name in self.commands:
                    handler = self.commands[func_name]
                    try:
                        result = handler.execute(func_name, [str(a) for a in args], context)
                        return result if result is not None else 0
                    except:
                        pass
                
                # Kullanıcı tanımlı fonksiyon - şimdilik basit destek
                if func_name in context.get('functions', {}):
                    # TODO: Implement user function call
                    return 0
        
        # Değişken - önce local_vars, sonra global_vars
        if expr in context.get('local_vars', {}):
            return context['local_vars'][expr]
        
        if expr in context.get('global_vars', {}):
            return context['global_vars'][expr]
        
        # Eski format için variables dictionary kontrolü (backward compatibility)
        if expr in context.get('variables', {}):
            return context['variables'][expr]
        
        # Matematiksel ifade
        try:
            # Değişkenleri değerlerle değiştir
            eval_expr = expr
            
            # Local vars'dan değiştir (öncelik)
            for var_name, var_value in context.get('local_vars', {}).items():
                if var_name in eval_expr:
                    if isinstance(var_value, str):
                        eval_expr = eval_expr.replace(var_name, f'"{var_value}"')
                    else:
                        eval_expr = eval_expr.replace(var_name, str(var_value))
            
            # Global vars'dan değiştir
            for var_name, var_value in context.get('global_vars', {}).items():
                if var_name in eval_expr:
                    if isinstance(var_value, str):
                        eval_expr = eval_expr.replace(var_name, f'"{var_value}"')
                    else:
                        eval_expr = eval_expr.replace(var_name, str(var_value))
            
            # Eski format variables (backward compatibility)
            for var_name, var_value in context.get('variables', {}).items():
                if var_name in eval_expr:
                    if isinstance(var_value, str):
                        eval_expr = eval_expr.replace(var_name, f'"{var_value}"')
                    else:
                        eval_expr = eval_expr.replace(var_name, str(var_value))
            
            # PDSX'de = comparison operatörüdür, Python'da == gerekir
            # Ama dikkatli olmalıyız - <= >= != gibi operatörleri bozmamamız lazım
            # Çözüm: = işaretini == ile değiştir, ama önce diğer operatörleri koru
            eval_expr = eval_expr.replace('<=', '##LE##')  # Temporary placeholder
            eval_expr = eval_expr.replace('>=', '##GE##')
            eval_expr = eval_expr.replace('<>', '##NE##')
            eval_expr = eval_expr.replace('!=', '##NE2##')
            
            # Şimdi kalan = işaretlerini == yap
            eval_expr = eval_expr.replace('=', '==')
            
            # Placeholders'ları geri al
            eval_expr = eval_expr.replace('##LE##', '<=')
            eval_expr = eval_expr.replace('##GE##', '>=')
            eval_expr = eval_expr.replace('##NE##', '!=')
            eval_expr = eval_expr.replace('##NE2##', '!=')
            
            # Güvenli eval (sadece matematik operatörleri)
            allowed_names = {"abs": abs, "min": min, "max": max, "pow": pow}
            return eval(eval_expr, {"__builtins__": {}}, allowed_names)
        except:
            pass
        
        # Hiçbiri değilse string olarak döndür
        return expr
    
    def execute_statement(self, statement: str, context: Optional[Dict] = None) -> Any:
        """
        Tek bir statement'ı çalıştır (IF THEN içinde kullanım için)
        """
        if context is None:
            context = self.context
            
        parsed = self.parse_line(statement)
        if not parsed:
            return None
            
        command, args = parsed
        
        # PHASE 0: Command Router (24 Ekim 2025)
        handler = self._route_command(command, args)
        
        # Komutu çalıştır
        if handler:
            return handler.execute(command, args, context)
        else:
            raise PDSXCommandError(f"Bilinmeyen komut: {command}")
    
    def execute_line(self, line: str):
        """Tek bir satırı çalıştır"""
        parsed = self.parse_line(line)
        if not parsed:
            return
        
        command, args = parsed
        
        # Özel operatör komutlarını işle
        if command == 'INCREMENT':
            # A++ veya ++A
            var_name = args[0]
            mode = args[1]  # 'pre' veya 'post'
            
            # Değişkeni context'ten al (global_vars veya local_vars'dan)
            current_value = None
            if 'global_vars' in self.context and var_name in self.context['global_vars']:
                current_value = self.context['global_vars'][var_name]
            elif 'local_vars' in self.context and var_name in self.context['local_vars']:
                current_value = self.context['local_vars'][var_name]
            elif var_name in self.context:
                current_value = self.context[var_name]
            
            if current_value is not None:
                old_value = current_value
                new_value = current_value + 1
                # Değişkeni güncelle
                if 'global_vars' in self.context and var_name in self.context['global_vars']:
                    self.context['global_vars'][var_name] = new_value
                elif 'local_vars' in self.context and var_name in self.context['local_vars']:
                    self.context['local_vars'][var_name] = new_value
                else:
                    self.context[var_name] = new_value
                return old_value if mode == 'post' else new_value
            else:
                # Değişken yoksa 1 yap
                if 'global_vars' not in self.context:
                    self.context['global_vars'] = {}
                self.context['global_vars'][var_name] = 1
                return 0 if mode == 'post' else 1
        
        elif command == 'DECREMENT':
            # A-- veya --A
            var_name = args[0]
            mode = args[1]  # 'pre' veya 'post'
            
            # Değişkeni context'ten al
            current_value = None
            if 'global_vars' in self.context and var_name in self.context['global_vars']:
                current_value = self.context['global_vars'][var_name]
            elif 'local_vars' in self.context and var_name in self.context['local_vars']:
                current_value = self.context['local_vars'][var_name]
            elif var_name in self.context:
                current_value = self.context[var_name]
            
            if current_value is not None:
                old_value = current_value
                new_value = current_value - 1
                # Değişkeni güncelle
                if 'global_vars' in self.context and var_name in self.context['global_vars']:
                    self.context['global_vars'][var_name] = new_value
                elif 'local_vars' in self.context and var_name in self.context['local_vars']:
                    self.context['local_vars'][var_name] = new_value
                else:
                    self.context[var_name] = new_value
                return old_value if mode == 'post' else new_value
            else:
                # Değişken yoksa -1 yap
                if 'global_vars' not in self.context:
                    self.context['global_vars'] = {}
                self.context['global_vars'][var_name] = -1
                return 0 if mode == 'post' else -1
        
        elif command == 'COMPOUND_ASSIGN':
            # A += 5, A *= 3, etc.
            var_name = args[0]
            operator = args[1]
            expression = args[2]
            
            # Expression'ı evaluate et
            value = self.evaluate_expression(expression, self.context)
            
            # Sayıya çevir (gerekirse)
            if isinstance(value, str):
                try:
                    if '.' in value:
                        value = float(value)
                    else:
                        value = int(value)
                except (ValueError, TypeError):
                    # Sayı değilse string olarak bırak
                    pass
            
            # Değişkeni al (global_vars veya local_vars'dan)
            current_value = None
            if 'global_vars' in self.context and var_name in self.context['global_vars']:
                current_value = self.context['global_vars'][var_name]
            elif 'local_vars' in self.context and var_name in self.context['local_vars']:
                current_value = self.context['local_vars'][var_name]
            elif var_name in self.context:
                current_value = self.context[var_name]
            else:
                current_value = 0
            
            # Operatöre göre işlem yap
            new_value = None
            if operator == '+=':
                new_value = current_value + value
            elif operator == '-=':
                new_value = current_value - value
            elif operator == '*=':
                new_value = current_value * value
            elif operator == '/=':
                new_value = current_value / value
            elif operator == '%=':
                new_value = current_value % value
            elif operator == '&=':
                new_value = int(current_value) & int(value)
            elif operator == '|=':
                new_value = int(current_value) | int(value)
            elif operator == '^=':
                new_value = int(current_value) ^ int(value)
            elif operator == '<<=':
                new_value = int(current_value) << int(value)
            elif operator == '>>=':
                new_value = int(current_value) >> int(value)
            
            # Değişkeni güncelle
            if 'global_vars' in self.context and var_name in self.context['global_vars']:
                self.context['global_vars'][var_name] = new_value
            elif 'local_vars' in self.context and var_name in self.context['local_vars']:
                self.context['local_vars'][var_name] = new_value
            else:
                if 'global_vars' not in self.context:
                    self.context['global_vars'] = {}
                self.context['global_vars'][var_name] = new_value
            
            return new_value
        
        # PHASE 0: Command Router Logic (24 Ekim 2025)
        # Çakışan komutlar için yönlendirme
        if self.debug_mode:
            print(f"[DEBUG execute_statement] command='{command}', args type={type(args)}, args={repr(args)}")
        
        handler = self._route_command(command, args)
        
        if self.debug_mode:
            print(f"[DEBUG execute_statement] handler={handler}, type={type(handler)}")
        
        # Komutu çalıştır
        if handler:
            try:
                if self.debug_mode:
                    print(f"[DEBUG execute_statement] Calling handler.execute...")
                
                result = handler.execute(command, args, self.context)
                
                if self.debug_mode:
                    print(f"[DEBUG execute_statement] Result: {repr(result)}")
                
                return result
            except Exception as e:
                print(f"[HATA] Hata (satir {self.current_line + 1}): {e}")
                print(f"  Komut: {command} {args}")
                if self.debug_mode:
                    import traceback
                    traceback.print_exc()
                raise
        else:
            print(f"[HATA] Bilinmeyen komut: {command}")
    
    def _route_command(self, command: str, args: List[str]) -> Any:
        """
        Command Router - Çakışan komutları doğru modüle yönlendirir
        
        Çakışan Komutlar (6 adet):
            - CLS: core_commands daha gelişmiş (gerçek terminal clear)
            - SLEEP: core_commands QBasic uyumlu (milisaniye)
            - INPUT: core_commands çok daha gelişmiş (çoklu değişken, format)
            - GETKEY: core_commands tam özellikli (platform bağımsız)
            - FUNCTION: context'e göre OOP (CLASS method) veya functions (standalone)
            - FIELD: context'e göre advanced_types (STRUCT/TYPE) veya oop (CLASS field)
        
        Router Kuralı:
            - Çakışan komutlar HER ZAMAN core_commands'tan çalışır
            - Grafik-özel komutlar mode'a göre yönlendirilir
            - FUNCTION/FIELD context'e göre yönlendirilir
        """
        command_upper = command.upper()
        
        # FUNCTION routing - context'e göre
        if command_upper == 'FUNCTION':
            # Inside CLASS block?
            if (self.context.get('__current_class__') or 
                self.context.get('defining_class') or
                self.context.get('__in_class_block__')):
                if self.debug_mode:
                    print(f"[ROUTER] FUNCTION -> oop (CLASS method)")
                return self.oop  # CLASS method
            else:
                if self.debug_mode:
                    print(f"[ROUTER] FUNCTION -> functions (standalone)")
                return self.functions  # Standalone function
        
        # FIELD routing - context'e göre
        if command_upper == 'FIELD':
            # Inside TYPE/STRUCT/ENUM/UNION block?
            if (self.context.get('__in_type_block__') and 
                self.context.get('__type_block_handler__')):
                if self.debug_mode:
                    print(f"[ROUTER] FIELD -> advanced_types (TYPE/STRUCT field)")
                return self.context['__type_block_handler__']  # advanced_types.py
            else:
                if self.debug_mode:
                    print(f"[ROUTER] FIELD -> oop (CLASS field)")
                return self.oop  # CLASS field
        
        # Çakışan komutlar listesi
        CONFLICTING_COMMANDS = {'CLS', 'SLEEP', 'INPUT', 'GETKEY'}
        
        # Çakışan komut mu?
        if command_upper in CONFLICTING_COMMANDS:
            # Her zaman core_commands kullan (daha gelişmiş oldukları için)
            if self.debug_mode:
                print(f"[ROUTER] {command} -> core_commands (override)")
            
            return self.core
        
        # Normal komut routing (mevcut davranış)
        if command in self.commands:
            return self.commands[command]
        
        return None
    
    def run(self):
        """Programı çalıştır"""
        if not self.program_lines:
            print("[HATA] Program yuklenmedi!")
            return
        
        if self.debug_mode:
            print("\n" + "="*50)
            print("DEBUG MODE: Program Starting")
            print("="*50 + "\n")
        
        self.running = True
        self.current_line = 0
        self.program_counter = 0  # FOR-NEXT için gerekli
        self.context['__running__'] = True
        
        try:
            while self.running and self.current_line < len(self.program_lines):
                self.context['__line_number__'] = self.current_line
                self.program_counter = self.current_line  # FOR-NEXT için senkronize et
                line = self.program_lines[self.current_line]
                
                # Trace mode
                if self.trace_mode:
                    print(f"[TRACE {self.current_line}] {line}")
                
                # END komutu kontrolü
                if not self.context.get('__running__', True):
                    break
                
                # Skip mode kontrolü (IF/ELSE bloklarını atlamak için)
                if self.context.get('__skip_mode__', False):
                    # Bu satırın komutunu kontrol et
                    parsed = self.parse_line(line)
                    if parsed:
                        command, _ = parsed
                        skip_targets = self.context.get('__skip_target__', [])
                        
                        # İç içe blok yapılarını kontrol et
                        # Skip depth ile TÜM iç içe blokları sayıyoruz (IF, DO, WHILE, FOR, SELECT)
                        if '__skip_depth__' not in self.context:
                            self.context['__skip_depth__'] = 0
                        
                        # BLOK BAŞLANGICI komutları - depth artır
                        if command.upper() == 'IF':
                            # İç içe IF başladı - tek satırlık mı multi-line mı kontrol et
                            line_upper = line.upper()
                            if 'THEN' in line_upper:
                                # THEN'den sonraki kısmı al
                                then_pos = line_upper.find('THEN')
                                after_then = line[then_pos + 4:].strip()
                                
                                if not (after_then and not after_then.startswith('REM') and not after_then.startswith("'")):
                                    # THEN'den sonra kod yok - multi-line IF, ENDIF var
                                    self.context['__skip_depth__'] += 1
                            else:
                                # THEN yok - multi-line IF
                                self.context['__skip_depth__'] += 1
                            
                            self.current_line += 1
                            continue
                        elif command.upper() in ['DO', 'WHILE', 'SELECT']:
                            # DO, WHILE, SELECT blok başlangıcı
                            self.context['__skip_depth__'] += 1
                            self.current_line += 1
                            continue
                        elif command.upper() == 'FOR':
                            # FOR döngüsü başlangıcı
                            self.context['__skip_depth__'] += 1
                            self.current_line += 1
                            continue
                        elif command.upper() in ['STRUCT', 'TYPE', 'ENUM', 'UNION', 'CLASS', 'YAPI', 'CLAZZ']:
                            # STRUCT/TYPE/ENUM/UNION/CLASS blok başlangıcı
                            self.context['__skip_depth__'] += 1
                            self.current_line += 1
                            continue
                        
                        # BLOK SONU komutları - depth azalt
                        elif command.upper() == 'ENDIF':
                            # ENDIF görüldü - depth kontrolü yap
                            if self.context['__skip_depth__'] > 0:
                                # İç içe IF'in ENDIF'i - depth azalt ve skip et
                                # ÖNEMLİ: if_stack'e dokunma, sadece depth azalt!
                                self.context['__skip_depth__'] -= 1
                                self.current_line += 1
                                continue
                            else:
                                # Ana IF-ELSEIF bloğunun ENDIF'i (depth=0)
                                # Bu ENDIF'i execute etmeliyiz (if_stack'i pop etmek için)
                                # ama önce skip mode'u kapatalım
                                self.context['__skip_mode__'] = False
                                self.context['__skip_target__'] = []
                                self.context['__skip_depth__'] = 0
                                # ENDIF'i execute et (if_stack pop edilecek)
                                self.execute_line(line)
                                self.current_line += 1
                                continue
                        elif command.upper() in ['LOOP', 'WEND', 'NEXT']:
                            # DO-LOOP, WHILE-WEND, FOR-NEXT sonu
                            if self.context['__skip_depth__'] > 0:
                                # İç içe döngünün sonu - depth azalt ve skip et
                                self.context['__skip_depth__'] -= 1
                                self.current_line += 1
                                continue
                            # depth=0 ise bu ana döngünün sonu (IF bloğunun dışındaki)
                            # Bu LOOP'u execute etmeliyiz (loop_stack'ten pop için)
                            self.execute_line(line)
                            # LOOP komutu current_line'ı değiştirir (loop başına döner veya ilerler)
                            # Execute sonrası zaten doğru yerdeyiz, continue
                            continue
                        elif command.upper() == 'END':
                            # END SELECT gibi blok sonları
                            # Sonraki kelimeyi kontrol et (line'dan parse et)
                            line_upper = line.upper().strip()
                            end_block_keywords = ['SELECT', 'IF', 'SUB', 'FUNCTION', 'STRUCT', 'TYPE', 'ENUM', 'UNION', 'CLASS', 'YAPI', 'CLAZZ']
                            if line_upper.startswith('END ') and any(x in line_upper for x in end_block_keywords):
                                if self.context['__skip_depth__'] > 0:
                                    self.context['__skip_depth__'] -= 1
                                    self.current_line += 1
                                    continue
                            # Normal END komutu - programı bitir (ama skip mode'dayız, atla)
                            self.current_line += 1
                            continue
                        
                        # ARA DALLANMA komutları (ELSE, ELSEIF, CASE)
                        elif command.upper() in ['ELSE', 'ELSEIF']:
                            # ELSE veya ELSEIF görüldü
                            if self.context['__skip_depth__'] > 0:
                                # İç içe IF'in ELSE/ELSEIF'i - skip et
                                self.current_line += 1
                                continue
                            # else: Ana IF'in ELSE/ELSEIF'i (depth=0) - aşağıda execute edilecek
                        elif command.upper() == 'CASE':
                            # SELECT CASE içindeki CASE dalı
                            if self.context['__skip_depth__'] > 0:
                                # İç içe SELECT'in CASE'i - skip et
                                self.current_line += 1
                                continue
                            # depth=0 ise ana IF'in içinde değiliz ama yine de skip
                            self.current_line += 1
                            continue
                        
                        # Ana IF bloğunun skip target'ına ulaştık (depth=0)
                        if command.upper() in skip_targets and command.upper() != 'ENDIF':
                            # Bu satırı execute et - komut kendisi skip mode'u kontrol edecek
                            self.execute_line(line)
                            
                            # Skip depth'i sıfırla (yeni bir IF bloğu başlayabilir)
                            self.context['__skip_depth__'] = 0
                            
                            # Execute sonrası skip mode tekrar kontrol et
                            self.current_line += 1
                            continue
                        
                        # Diğer satırları atla (skip mode devam)
                        self.current_line += 1
                        continue
                else:
                    # Normal execution
                    self.execute_line(line)
                
                self.current_line += 1
                
        except KeyboardInterrupt:
            print("\n\n[HATA] Program kullanici tarafindan durduruldu!")
        except Exception as e:
            print(f"\n[HATA] Program hatasi: {e}")
            if self.debug_mode:
                import traceback
                traceback.print_exc()
        finally:
            if self.debug_mode:
                print("\n" + "="*50)
                print("DEBUG MODE: Program Finished")
                print("="*50)
    
    def interactive_mode(self):
        """Interactive mode (REPL) - Multi-line support"""
        print("\n" + "="*50)
        print("PDSX-X INTERACTIVE MODE")
        print("="*50)
        print("Type 'EXIT' to quit")
        print("Multi-line mode: Type commands, then 'RUN' to execute")
        print("Single line mode: Type command and press Enter (executes immediately)")
        print("")
        
        # Multi-line buffer
        program_buffer = []
        multiline_mode = False
        multiline_msg_shown = False  # Mesajın gösterilip gösterilmediğini takip et
        
        while True:
            try:
                # Prompt değiştir (multi-line modunda farklı)
                if multiline_mode:
                    prompt = "PDSX> "
                    line = input(prompt).strip()
                else:
                    prompt = "PDSX> "
                    line = input(prompt).strip()
                
                if not line:
                    continue
                
                # EXIT kontrolü
                if line.upper() == 'EXIT' or line.upper() == 'QUIT':
                    if multiline_mode and program_buffer:
                        print("⚠️  Buffer temizleniyor...")
                        program_buffer.clear()
                        multiline_mode = False
                        multiline_msg_shown = False
                        continue
                    print("İnteraktif mod kapatılıyor...")
                    break
                
                # RUN komutu - bufferdeki tüm komutları AYNI ANDA çalıştır
                if line.upper() == 'RUN':
                    if not program_buffer:
                        print("⚠️  Buffer boş. Önce komut yazın.")
                        continue
                    
                    # Başlık kaldırıldı - sessiz mod
                    
                    # BUFFER'DAKİ TÜM SATIRLARI BİRLEŞTİREREK TEK PROGRAM OLARAK ÇALIŞTIR
                    full_program = '\n'.join(program_buffer)
                    
                    try:
                        # Programı satırlara böl ve çalıştır
                        self.program_lines = [line.strip() for line in full_program.split('\n') if line.strip()]
                        self.current_line = 0
                        self.program_counter = 0  # FOR-NEXT için
                        executed_lines = set()  # Hangi satırlar gösterildi
                        
                        while self.current_line < len(self.program_lines):
                            self.program_counter = self.current_line  # FOR-NEXT senkronizasyonu
                            line = self.program_lines[self.current_line]
                            
                            # Sadece ilk çalıştırmada satırı göster (FOR loop tekrarlarında gösterme)
                            if self.current_line not in executed_lines:
                                if self.trace_mode:  # TRACE mode'da göster
                                    print(f">>> {line}")
                                executed_lines.add(self.current_line)
                            
                            self.execute_line(line)
                            self.current_line += 1
                            
                    except Exception as e:
                        print(f"✗ Hata: {e}")
                    
                    # Bitiş mesajı kaldırıldı - sessiz mod
                    
                    # Buffer'ı temizle
                    program_buffer.clear()
                    multiline_mode = False
                    multiline_msg_shown = False
                    continue
                
                # LIST komutu - buffer içeriğini göster
                if line.upper() == 'LIST':
                    if not program_buffer:
                        print("Buffer boş.")
                    else:
                        print("\n=== BUFFER İÇERİĞİ ===")
                        for i, cmd in enumerate(program_buffer, 1):
                            print(f"{i:3d}: {cmd}")
                        print(f"\nToplam: {len(program_buffer)} satır")
                    continue
                
                # CLEAR komutu - buffer'ı temizle
                if line.upper() == 'CLEAR' or line.upper() == 'NEW':
                    if program_buffer:
                        program_buffer.clear()
                        print("✓ Buffer temizlendi")
                        multiline_mode = False
                        multiline_msg_shown = False
                    else:
                        print("Buffer zaten boş.")
                    continue
                
                # SAVE komutu - buffer'ı dosyaya kaydet
                if line.upper().startswith('SAVE '):
                    filename = line[5:].strip()
                    if not filename:
                        print("✗ Dosya adı belirtilmedi. Kullanım: SAVE dosya.pdsx")
                        continue
                    
                    try:
                        with open(filename, 'w', encoding='utf-8') as f:
                            for cmd in program_buffer:
                                f.write(cmd + '\n')
                        print(f"✓ {len(program_buffer)} satır '{filename}' dosyasına kaydedildi")
                    except Exception as e:
                        print(f"✗ Kaydetme hatası: {e}")
                    continue
                
                # LOAD komutu - dosyadan buffer'a yükle
                if line.upper().startswith('LOAD '):
                    filename = line[5:].strip()
                    if not filename:
                        print("✗ Dosya adı belirtilmedi. Kullanım: LOAD dosya.pdsx")
                        continue
                    
                    try:
                        with open(filename, 'r', encoding='utf-8') as f:
                            loaded_lines = [l.strip() for l in f.readlines() if l.strip() and not l.strip().startswith('REM')]
                        
                        program_buffer.clear()
                        program_buffer.extend(loaded_lines)
                        multiline_mode = True
                        multiline_msg_shown = False
                        print(f"✓ {len(program_buffer)} satır '{filename}' dosyasından yüklendi")
                        print("  'LIST' ile göster, 'RUN' ile çalıştır")
                    except FileNotFoundError:
                        print(f"✗ Dosya bulunamadı: {filename}")
                    except Exception as e:
                        print(f"✗ Yükleme hatası: {e}")
                    continue
                
                # Multi-line mode tetikleyicileri
                multiline_triggers = ['FOR', 'WHILE', 'IF', 'FUNCTION', 'SUB', 'CLASS', 'DO']
                first_word = line.split()[0].upper() if line.split() else ''
                
                # Eğer multi-line tetikleyici varsa veya zaten multi-line modundaysak
                if first_word in multiline_triggers or multiline_mode:
                    program_buffer.append(line)
                    multiline_mode = True
                    # Multi-line mesajı kaldırıldı - sessiz mod
                else:
                    # Tek satırlık komut - hemen çalıştır
                    self.execute_line(line)
                
            except KeyboardInterrupt:
                print("\n✗ Ctrl+C - Çıkmak için EXIT yazın")
                if program_buffer:
                    print(f"  Buffer: {len(program_buffer)} satır (CLEAR ile temizle)")
            except Exception as e:
                print(f"✗ Hata: {e}")


def main():
    """Ana program (venv kontrolü script başında yapıldı)"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PDSX-X Modular Interpreter')
    parser.add_argument('file', nargs='?', help='PDSX program dosyası')
    parser.add_argument('-i', '--interactive', action='store_true', 
                       help='İnteraktif mod (basit REPL)')
    parser.add_argument('-r', '--repl', action='store_true',
                       help='Curses REPL modu (gelişmiş çok satırlı IDE arayüzü)')
    parser.add_argument('--debug', action='store_true',
                       help='Debug modu (detaylı çıktı)')
    parser.add_argument('--trace', action='store_true',
                       help='Trace modu (satır satır takip)')
    parser.add_argument('--testfile', type=str,
                       help='Test dosyası adı (tests/ klasöründen)')
    parser.add_argument('--testdir', type=str,
                       help='Test klasörü yolu')
    
    args = parser.parse_args()
    
    # Interpreter oluştur
    interpreter = PDSXInterpreter()
    
    # Debug/Trace modlarını ayarla
    if args.debug:
        interpreter.debug_mode = True
    if args.trace:
        interpreter.trace_mode = True
    
    # Test dizinini ayarla
    if args.testdir:
        interpreter.test_directory = args.testdir
    
    # Test dosyası varsa yolu oluştur
    file_to_run = args.file
    if args.testfile:
        file_to_run = os.path.join(interpreter.test_directory, args.testfile)
    
    if file_to_run:
        # Dosya çalıştır
        if interpreter.load_program(file_to_run):
            interpreter.run()
    elif args.repl:
        # Curses REPL modu (gelişmiş IDE)
        try:
            from pdsx_commands.curses_repl import CursesREPL
            repl = CursesREPL(interpreter)
            repl.run()
        except ImportError as e:
            print(f"✗ Curses REPL yüklenemedi: {e}")
            print("  Windows'ta: pip install windows-curses")
        except Exception as e:
            print(f"✗ Curses REPL hatası: {e}")
    elif args.interactive:
        # Basit İnteraktif mod (eski REPL)
        interpreter.interactive_mode()
    else:
        # Yardım göster
        parser.print_help()
        print("\nÖrnek kullanım:")
        print("  python pdsx_interpreter.py program.pdsx")
        print("  python pdsx_interpreter.py -i          # Basit REPL")
        print("  python pdsx_interpreter.py -r          # Curses REPL (IDE)")


if __name__ == '__main__':
    main()
