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

---

## 2026-02-23 - Metod Davranis Sozlugu (Kritik Moduller)

### `core_commands.py` (`CoreCommands`)
- `cmd_print`: girdi=`args, context` | cikti=`None` | yan etki=konsola yazdirir, expression cozer, Windows UTF-8 codepage ayarlamayi dener.
- `cmd_input`: girdi=`args, context` | cikti=`None` | yan etki=kullanicidan input alip degiskenlere yazar (`set_variable`).
- `cmd_cls`: girdi=`args` | cikti=`None` | yan etki=terminal temizler (`cls/clear`).
- `cmd_end`: girdi=`args` | cikti=sureci sonlandirir | yan etki=`interpreter.running=False`, `sys.exit(0)`.
- `cmd_load`: girdi=`filename` | cikti=`None` | yan etki=dosya okur, interpreter program alanina yukler.
- `cmd_save`: girdi=`filename` | cikti=`None` | yan etki=interpreter programini dosyaya yazar.
- `cmd_run`: girdi=`opsiyonel filename` | cikti=`None` | yan etki=load+execute tetikler (`execute_program`/`run`).
- `cmd_sleep`: girdi=`ms` | cikti=`None` | yan etki=calismayi bekletir (`time.sleep`).
- `cmd_debug`: girdi=`ON/OFF` | cikti=`None` | yan etki=`interpreter.debug_mode` degistirir.
- `cmd_trace`: girdi=`ON/OFF` | cikti=`None` | yan etki=`interpreter.trace_mode` degistirir.
- `cmd_getkey`: girdi=`opsiyonel hedef tuslar` | cikti=`str` | yan etki=bloklayici tus bekleme.
- `cmd_alias`: girdi=`new_name, existing_command` | cikti=`None` | yan etki=`interpreter.command_aliases` uzerine alias yazar.

### `variable_manager.py` (`VariableManager`)
- `cmd_dim`: girdi=`DIM ...` | cikti=`None` | yan etki=degisken/dizi olusturur, `var_types` kaydi acilir.
- `cmd_let`: girdi=`var = expr` | cikti=`None` | yan etki=ifadeyi cozer ve degiskene yazar.
- `cmd_const`: girdi=`CONST ... = ...` | cikti=`None` | yan etki=`constants` ve `global_vars` guncellenir.
- `cmd_global`: girdi=`GLOBAL var [=expr]` | cikti=`None` | yan etki=global scope yazimi.
- `cmd_local`: girdi=`LOCAL var [=expr]` | cikti=`None` | yan etki=local scope yazimi.
- `cmd_redim`: girdi=`REDIM [PRESERVE] arr(size)` | cikti=`None` | yan etki=dizi yeniden boyutlanir.
- `cmd_erase`: girdi=`var/array` | cikti=`None` | yan etki=local/global'dan silme.
- `cmd_swap`: girdi=`var1,var2` | cikti=`None` | yan etki=iki degisken degerini degistirir.
- `cmd_unset`: girdi=`var` | cikti=`None` | yan etki=`cmd_erase` delege edilir.

### `flow_control.py` (`FlowControl`)
- `cmd_if`: girdi=`condition THEN ...` | cikti=`bool/None/statement result` | yan etki=`if_stack` ve `__skip_*` bayraklarini yonetir.
- `cmd_else`: girdi=`ELSE` | cikti=`True/False` | yan etki=aktif IF state'i ve skip hedefleri guncellenir.
- `cmd_elseif`: girdi=`condition THEN` | cikti=`True/False` | yan etki=if state (`executed/condition`) ve skip alanlari guncellenir.
- `cmd_endif`: girdi=`ENDIF` | cikti=`None` | yan etki=`if_stack.pop()`, skip reset.
- `cmd_select`: girdi=`SELECT CASE expr` | cikti=`value` | yan etki=`select_stack` push.
- `cmd_case`: girdi=`CASE ...` | cikti=`True/False` | yan etki=son select state `matched/in_case` gunceller.
- `cmd_end_select`: girdi=`END SELECT` | cikti=`None` | yan etki=`select_stack.pop()`.
- `cmd_goto`: girdi=`label` | cikti=`label` | yan etki=`context['goto_label']` set.
- `cmd_gosub`: girdi=`label` | cikti=`label` | yan etki=donus adresini stack'e yazar, `goto_label` set.
- `cmd_return`: girdi=`opsiyonel expr` | cikti=`None/expr` | yan etki=GOSUB donusu veya `function_return` bayragi.

### `loop_control.py` (`LoopControl`)
- `cmd_for`: girdi=`FOR var=start TO end [STEP inc]` | cikti=`start_value` | yan etki=loop state push, gerekirse `skip_to_next`.
- `cmd_next`: girdi=`NEXT [var]` | cikti=`next value/None` | yan etki=iterasyonu ilerletir, gerekiyorsa `program_counter/current_line` geri sarar.
- `cmd_while`: girdi=`condition` | cikti=`bool` | yan etki=`WHILE` state push, false ise `skip_to_wend`.
- `cmd_wend`: girdi=`WEND` | cikti=`True/False` | yan etki=kosula gore donguye geri doner veya pop eder.
- `cmd_do`: girdi=`DO [WHILE/UNTIL cond]` | cikti=`bool` | yan etki=`DO` state push, on-test fail ise `skip_to_loop`.
- `cmd_loop`: girdi=`LOOP [WHILE/UNTIL cond]` | cikti=`True/False/next item` | yan etki=DO/DO_EACH akisini ilerletir veya geri sarar.
- `cmd_exit_for`: girdi=`EXIT FOR` | cikti=`None` | yan etki=en yakin FOR state'i silinir, `exit_loop_type` set.
- `cmd_continue_for`: girdi=`CONTINUE FOR` | cikti=`None` | yan etki=`continue_loop_type`/`continue_to_pc` set.

### Not
- Bu sozluk kod davranisina dayali cikartilmistir; metot imzalari ve yan etkiler interpreter context alanlariyla birlikte okunmalidir.
