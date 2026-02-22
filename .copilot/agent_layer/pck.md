# pck.md (Programcinin Cep Kitabi) - append-only

## Modul Ozeti (Baslangic)

### 1) `src/main.jsx`
- Amac: 
- Onem: 



## Not
- Derin sinif/metot detaylari her degisiklikte buraya EKLENIR (silinmez).

---

## 2026-02-23 - PDSX Modul Haritasi (Duzenli Baslangic)

Bu bolum PDSX kok projesi icin eklendi. Mevcut anlami degistirmez, kapsam genisletir.

### Cekirdek Komut Mimarisi
1) `base_command.py`
- `PDSXCommandError`: Komut seviyesi hata sinifi.
- `BaseCommand`: Tum komut modullerinin ortak taban sinifi.

2) `pdsx_interpreter.py`
- Amac: Dil yorumlayici girisi, komut dispatch ve calisma akisi.

3) `pdsx_launcher.py`
- Amac: Yorumlayici baslatma ve calisma ortami acilisi.

### Komut Modulleri (Siniflar)
- `core_commands.py` -> `CoreCommands`
- `math_operations.py` -> `MathOperations`
- `string_operations.py` -> `StringOperations`
- `file_operations.py` -> `FileOperations`, `FileHandle`
- `network_operations.py` -> `NetworkOperations`, `SocketConnection`
- `database_operations.py` -> `DatabaseOperations`, `DatabaseConnection`
- `event_system.py` -> `EventSystem`, `EventBus`, `EventHandler`
- `memory_system.py` -> `MemorySystem`, `PointerManager`
- `debug_system.py` -> `DebugSystem`
- `exception_handling.py` -> `ExceptionHandling`
- `function_manager.py` -> `FunctionManager`, `FunctionParameter`, `ParameterMode`
- `data_structures.py` -> `DataStructures`, `PDSXStruct`, `PDSXUnion`, `PDSXEnum`, `PDSXTree`, `PDSXGraph`
- `meta_programming.py` -> `UnifiedMetaProgramming`, `MetaProcessor`, `MetaBlock`

### Alan Modulleri (Siniflar)
- `oop_system.py` -> `OOPSystem`
- `namespace_system.py` -> `NamespaceSystem`
- `flow_control.py` -> `FlowControl`
- `loop_control.py` -> `LoopControl`
- `graphics_system.py` -> `GraphicsSystem`
- `dll_system.py` -> `DLLSystem`
- `ml_system.py` -> `MLSystem`
- `nlp_system.py` -> `NLPSystem`
- `prolog_system.py` -> `PrologSystem`
- `rest_api_system.py` -> `RESTAPISystem`

### Islem Kurali
- Bu listedeki her modulde degisiklik yapildiginda:
  - Degisen sinif/metot bu dosyaya ek satir olarak yazilir.
  - Degisiklik nedeni `memory.md` kaydina eklenir.
  - Gorev durumu `todo.md` icinde guncellenir.

### Duzeltme Notu (2026-02-23)
- `oop_system.py` icindeki komut sinifi adi `OOPSystem` degil `OOPCommands` olarak gecmektedir.
- `rest_api_system.py` sinifi `RESTAPISystem` degil `RestAPISystem` olarak gecmektedir.

---

## 2026-02-23 - Interpreter Cozumleme Notlari

### Calisma Akisi
1. Giris: `pdsx_launcher.py` venv kontrolu yapar ve interpreter main cagrisina gecer.
2. Cekirdek: `PDSXInterpreter.__init__` context/registry kurar, sonra `_init_modules` ile tum modulleri yukler.
3. Kayit: Her modul `BaseCommand.register_command` ile komutlarini `interpreter.commands` uzerine kaydeder.
4. Parse: `parse_line` satiri komut + arguman formatina cevirir; multi-word komutlari normalize eder.
5. Calistirma: `execute_line` ve `execute_statement`, `_route_command` ile dogru module yonlendirip `handler.execute(...)` cagirir.
6. Program dongusu: `run` satir satir ilerler, skip-mode ile IF/ELSE/LOOP gibi blok kontrolunu yonetir.

### Router Davranisi (Kritik)
- `FUNCTION`: CLASS baglamindaysa `oop`, degilse `functions`.
- `FIELD`: TYPE/STRUCT baglamindaysa `advanced_types` handler, degilse `oop`.
- Cakisan komutlar (`CLS`, `SLEEP`, `INPUT`, `GETKEY`) her zaman `core` module override edilir.

### Cekirdek Modul Gruplari
- Temel: `CoreCommands`, `VariableManager`, `FlowControl`, `LoopControl`, `FunctionManager`, `OOPCommands`, `DataStructures`, `StringOperations`, `MathOperations`.
- Sistem/IO: `FileOperations`, `EventSystem`, `DatabaseOperations`, `NetworkOperations`, `DLLSystem`.
- Gelismis: `ExceptionHandling`, `NamespaceSystem`, `AdvancedTypes`, `ThreadingSystem`, `DebugSystem`, `MemorySystem`, `AdvancedOperators`, `RegexOperations`, `CastSystem`, `TypeFunctions`, `NestingValidator`.
- AI/API: `PrologSystem`, `NLPSystem`, `GitHubOperations`, `RestAPISystem`.
- Veri bilimi/grafik: `StatisticalTests`, `NumpyOperations`, `PandasOperations`, `LinqOperations`, `GraphicsSystem`.

### Komut Yuzeyi (register_command sayisi, ust moduller)
- `graphics_system.py`: 134
- `statistical_tests.py`: 133
- `pandas_operations.py`: 67
- `string_operations.py`: 56
- `numpy_operations.py`: 50
- `oop_system.py`: 50
- `math_operations.py`: 40
- `linq_operations.py`: 31

### Notlar
- Komut sayisi `register_command` cagri adedidir; alias/space-version nedeniyle efektif komut adedi daha farkli olabilir.
- `BaseCommand` underscore iceren komutlarin bosluklu aliaslarini da kaydeder.

---

## 2026-02-23 - Alt Ajan Paralel Derin Envanter

### Cekirdek Akis Modulleri
- `core_commands.py` / `CoreCommands`
  - Kritik metotlar: `cmd_print`, `cmd_print_using`, `cmd_input`, `cmd_cls`, `cmd_end`, `cmd_load`, `cmd_save`, `cmd_run`, `cmd_sleep`, `cmd_getkey`, `cmd_graphics_mode`, `cmd_alias`.
  - Rol: temel I/O, program yasam dongusu ve runtime yardimcilari.
- `variable_manager.py` / `VariableManager`
  - Kritik metotlar: `cmd_dim`, `cmd_let`, `cmd_const`, `cmd_global`, `cmd_local`, `cmd_redim`, `cmd_erase`, `cmd_swap`, `cmd_unset`.
  - Rol: degisken/scope/tip ve dizi yonetimi.
- `flow_control.py` / `FlowControl`
  - Kritik metotlar: `cmd_if`, `cmd_else`, `cmd_elseif`, `cmd_endif`, `cmd_select`, `cmd_case`, `cmd_case_else`, `cmd_end_select`, `cmd_goto`, `cmd_gosub`, `cmd_return`, `cmd_on`.
  - Rol: kosullu dallanma, SELECT CASE, etiket tabanli akis.
- `loop_control.py` / `LoopControl`
  - Kritik metotlar: `cmd_for`, `cmd_next`, `cmd_while`, `cmd_wend`, `cmd_do`, `cmd_loop`, `cmd_exit_for`, `cmd_exit_while`, `cmd_exit_do`, `cmd_continue_for`, `cmd_foreach`, `cmd_do_each`.
  - Rol: FOR/WHILE/DO ve koleksiyon dongu akisi.

### Function/OOP/Type Katmani
- `function_manager.py`
  - Siniflar: `ParameterMode`, `FunctionParameter`, `FunctionManager`.
  - Kayitlar: `FUNCTION`, `END_FUNCTION`, `SUB`, `END_SUB`, `CALL`, `RETURN`, `FN`, `PARAM`.
- `oop_system.py`
  - Ana komut sinifi: `OOPCommands`.
  - Kritik kayitlar: `YAPI/CLAZZ/CLASS`, `FIELD`, `SUB/FUNCTION`, `PROPERTY(GET/SET)`, `EVENT/RAISE`, `NEW`, `REACTIVE`, `MIXIN`, `CONFIG OOP_SYSTEM`.
- `advanced_types.py`
  - Sinif: `AdvancedTypes`.
  - Kayitlar: `TYPE`, `STRUCT`, `UNION`, `ENUM`, `TYPEDEF`, `FIELD` (type blok icinde).
- `data_structures.py`
  - Sinif: `DataStructures`.
  - Runtime komutlari: `XSTRUCTX/XUNIONX/XENUMX`, `ARRAY/LIST/DICT/SET/QUEUE/STACK`, `TREE/GRAPH`, `ADD_NODE/ADD_EDGE/TRAVERSE`.

### Router ile Etkilesim (onemli)
- `FUNCTION`: class baglaminda `oop`, aksi halde `function_manager`.
- `FIELD`: type blok baglaminda `advanced_types`, aksi halde `oop`.
- Cakisanlar (`CLS`, `SLEEP`, `INPUT`, `GETKEY`) her zaman `core`.

### Sistem + Veri Bilimi Modulleri (Yogunluk)
- Yuksek komut yuzeyi: `graphics_system` (134), `statistical_tests` (133), `pandas_operations` (67), `string_operations` (56), `numpy_operations` (50), `math_operations` (40).
- Orta: `linq_operations` (31), `file_operations` (26), `network_operations` (18).
- Dusuk: `event_system` (13), `database_operations` (11).

### Bakim Sicak Noktalari
- `graphics_system.py`: tek sinifta cok genis alan (3271+ satir, 150+ method).
- `statistical_tests.py`: cok yuksek komut yuku (2000+ satir, 140+ method), tekrar eden `MOOD` kaydi notu.
- `pandas_operations.py` / `numpy_operations.py`: tek dosya genis API yuzeyi.
