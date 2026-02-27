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

---

## 2026-02-23 - Paralel Derinlestirme (Function + OOP + Advanced Types)

### `function_manager.py` Method Sozlugu (kritik)
- `_call_function`: girdi=`func_name,args,context` | cikti=`Any/None` | yan etki=`local_vars` gecici scope, `function_return`/`return_value` tuketimi, satirlar `execute_statement` ile calistirilir.
- `cmd_call`: girdi=`CALL ...` | cikti=`function/lambda sonucu veya None` | yan etki=argumanlari evaluate eder, hedefi `functions/subs/lambdas` arasinda route eder.
- `cmd_function`: girdi=`FUNCTION ...` | cikti=`func_name` | yan etki=`self.functions` kaydi + `context['defining_function']` set.
- `cmd_sub`: girdi=`SUB ...` | cikti=`sub_name` | yan etki=`self.subs` kaydi + `context['defining_sub']` set.
- `_call_subroutine`: girdi=`sub_name,args,context` | cikti=`None` | yan etki=local scope gecici degisir, `function_return` gorulurse erken cikis.
- `cmd_return_value`: girdi=`RETURN [expr]` | cikti=`None` | yan etki=`return_value` yazimi + `function_return=True`.
- `cmd_fn`: girdi=`FN ...` | cikti=`lambda_name` | yan etki=closure uretip `self.lambdas` kaydeder.
- `_call_lambda`: girdi=`lambda_name,args,context` | cikti=`lambda result` | yan etki=hata durumunu `PDSXCommandError`'a sarar.
- `cmd_end_function`: girdi=`END FUNCTION` | cikti=`None` | yan etki=aktif function tanimini kapatir, context flag temizler.
- `cmd_end_sub`: girdi=`END SUB` | cikti=`None` | yan etki=aktif sub tanimini kapatir, context flag temizler.
- `cmd_param`: girdi=`PARAM ...` | cikti=`param_name` | yan etki=`context['current_params']` listesine ekler.

### `oop_system.py` Method Sozlugu (kritik)
- `execute_yapi`: girdi=`YAPI ...` | cikti=`None` | yan etki=`__current_yapi__` set, registry kaydi.
- `execute_clazz`: girdi=`CLAZZ ...` | cikti=`None` | yan etki=`__current_clazz__` set, registry kaydi.
- `execute_class`: girdi=`CLASS ...` | cikti=`None` | yan etki=`__current_class__` set, class registry kaydi.
- `execute_inherits`: girdi=`INHERITS/EXTENDS ...` | cikti=`None` | yan etki=parent list ve MRO guncellenir.
- `execute_field`: girdi=`FIELD ...` | cikti=`None` | yan etki=current_yapi fields mutasyonu.
- `execute_class_field`: girdi=`<FIELD> ...` | cikti=`None` | yan etki=current_clazz class_fields mutasyonu.
- `execute_sub`: girdi=`SUB ...` | cikti=`None` | yan etki=`__current_method__` olusturur.
- `execute_end_sub`: girdi=`END SUB` | cikti=`None` | yan etki=current_class'a method baglar, `__current_method__` temizler.
- `execute_function`: girdi=`FUNCTION ...` | cikti=`None` | yan etki=`execute_sub` delege + return_type set.
- `execute_property`: girdi=`PROPERTY ...` | cikti=`None` | yan etki=`__current_property__` olusturur.
- `execute_end_property`: girdi=`END PROPERTY` | cikti=`None` | yan etki=property class'a eklenir, context temizlenir.
- `execute_new`: girdi=`NEW class(args)` | cikti=`PDSXInstance` | yan etki=instance registry kaydi.
- `execute_reactive`: girdi=`REACTIVE ...` | cikti=`None` | yan etki=current_class reactive_vars mutasyonu.
- `execute_hybrid_class`: girdi=`HYBRID CLASS ...` | cikti=`None` | yan etki=hybrid class acilisi.

### `advanced_types.py` + `data_structures.py` Method Sozlugu (kritik)
- `AdvancedTypes.execute`: girdi=`command,args,context` | cikti=`execute_* sonucu` | yan etki=komut normalize ve dispatch.
- `execute_type`: girdi=`TYPE name` | cikti=`None` | yan etki=type_stack push.
- `execute_end_type`: girdi=`END TYPE` | cikti=`None` | yan etki=user_types kaydi + factory.
- `execute_struct`: girdi=`STRUCT name` | cikti=`None` | yan etki=type_stack push + `__in_type_block__/__type_block_handler__` set.
- `execute_field_in_type`: girdi=`FIELD ...` | cikti=`None` | yan etki=aktif tip alanlarina ekleme.
- `execute_end_struct`: girdi=`END STRUCT` | cikti=`None` | yan etki=struct kaydi/factory + type-block flag temizligi.
- `execute_union`: girdi=`UNION name` | cikti=`None` | yan etki=type_stack push.
- `execute_end_union`: girdi=`END UNION` | cikti=`None` | yan etki=union kaydi/factory.
- `add_field_to_current_type`: girdi=`field_name,type/default` | cikti=`None` | yan etki=current type schema mutasyonu.
- `_create_type_factory`: girdi=`type_name,type_def` | cikti=`factory closure` | yan etki=`interpreter.user_types` + `function_table` kaydi.
- `DataStructures.execute_struct`: girdi=`XSTRUCTX name` | cikti=`None` | yan etki=`current_struct` + `__defining_struct__`.
- `DataStructures.execute_end_struct`: girdi=`END XSTRUCTX` | cikti=`None` | yan etki=`context['__structs__']` kaydi, flag kapama.

### Router-Context Bagimliligi
- `FUNCTION`: class baglaminda `oop`, aksi halde `function_manager`.
- `FIELD`: type blok baglaminda (`__in_type_block__` + `__type_block_handler__`) `advanced_types`, aksi halde `oop`.

### Koddan Gelen Risk Notlari
- `function_manager`: `FunctionParameter` nesnesi ile dict benzeri erisim kullanan cagri akisinda uyumsuzluk riski.
- `oop_system`: BaseCommand execute imzasi ile bazi `execute_*` metot imzalari arasinda kirilganlik riski.

---

## 2026-02-23 - Legacy Graphics Syntax Koprusu (Parser + Graphics)

### Parser Genisletmesi (`pdsx_interpreter.py`)
- Multi-word parse listesine eklendi:
  - `CREATE IMAGE SPRITE`
  - `CREATE ASCII SPRITE`
  - `DRAW SPRITE`
  - `COLLISION ON`
  - `COLLISION OFF`
- Etki: legacy `.pdsx` satirlari tek token komut anahtarina normalize oluyor:
  - `CREATE_IMAGE_SPRITE`, `CREATE_ASCII_SPRITE`, `DRAW_SPRITE`, `COLLISION_ON`, `COLLISION_OFF`.

### Graphics Compatibility Wrapper'lari (`graphics_system.py`)
- Register edilen uyumluluk komutlari:
  - `CREATE_IMAGE_SPRITE`
  - `CREATE_ASCII_SPRITE`
  - `DRAW_SPRITE`
  - `COLLISION_ON`
  - `COLLISION_OFF`
- Wrapper davranislari:
  - Legacy arguman formatini parse edip mevcut engine metotlarina delege eder.
  - `COLLISION ON/OFF` komutlarini mevcut collision state toggling akisina baglar.
  - CSV + quote iceren argumanlar icin `_split_csv_quoted` yardimcisi kullanilir.

### Dogrulama Notu
- Parse smoke test sonucu (gercek satirlarla):
  - `CREATE IMAGE SPRITE ...` => `('CREATE_IMAGE_SPRITE', [...])`
  - `DRAW SPRITE ...` => `('DRAW_SPRITE', [...])`
  - `COLLISION ON` => `('COLLISION_ON', [])`
  - `COLLISION OFF` => `('COLLISION_OFF', [])`

### Execute-Line Runtime Dogrulama (2026-02-23)
- `COLLISION ON/OFF` komutlari execute seviyesinde dogrulandi:
  - `COLLISION ON` => `True`
  - `COLLISION OFF` => `False`
  - context bayragi: `__collision_enabled__` beklendigi gibi guncelleniyor.
- `CREATE ASCII SPRITE` + `DRAW SPRITE` komutlari execute seviyesinde dogrulandi:
  - sprite olusumu ve `DRAW` sonrasi koordinat guncellemesi dogrulandi (`x,y`).
- `CREATE ASCII SPRITE` wrapper davranisi genisletildi:
  - normalize edilen iki format: `id, "chars", x, y` ve `id, x, y, "chars"`.

### Runtime Ortam Koruma Notu
- `PDSXInterpreter._setup_virtual_environment` artik `pdsxu_venv` yoksa auto paket kontrolunu atliyor.
- Opsiyonel bypass: `PDSX_DISABLE_AUTO_DEP_INSTALL=1`.
- Etki: yanlis/olmayan legacy venv path'e otomatik pip denemesi ve gürültulu cikti engellenir.

### Legacy Image Sprite ID Koprusu (2026-02-27)
- Problem: `SpriteManager` image ID araligini `129-256` ile sinirliyor; legacy scriptler `CREATE IMAGE SPRITE 1...` gibi dusuk ID kullaniyor.
- Cozum (`graphics_system.py`):
  - `_legacy_image_sprite_ids` esleme tablosu eklendi.
  - `_map_legacy_image_sprite_id(requested_id)` yardimcisi ile legacy ID -> ic image ID esleniyor.
  - `cmd_create_image_sprite_compat` ic ID ile `cmd_sprite_load` cagirip legacy ID donuyor.
  - `cmd_draw_sprite_compat` legacy ID ile cagrilsa da maplenmis ic sprite uzerinden pozisyon guncelliyor.

### Runtime Sonucu
- Dosya var senaryosu: `CREATE IMAGE SPRITE 1, "...", x, y AS IMAGE` -> basarili.
- Dosya yok senaryosu: beklenen hata (`PDSXCommandError: Image file not found`).
- Dogrulanan esleme: `1 -> 129`.

### Legacy DRAW SPRITE Tarama Sonucu (2026-02-27)
- `**/*.pdsx` taramasinda `DRAW SPRITE` cagrilari bulundu; pratik kullanimlar dosya argumanli formda:
  - `DRAW SPRITE id, "file" AT x, y`
- Dosya argumansiz form (`DRAW SPRITE id AT x, y`) vakasi bulunmadi.
- Sonuc: mevcut uyumluluk katmaninda ID mapping sonrasi sahadaki scriptler icin ek zorunlu yama gerektiren vaka tespit edilmedi.
- `oop_system`: bazi ileri komut metotlari `pass` durumunda (stub).
- `advanced_types`: `TYPE/UNION` acilislarinda type-block flag yonetimi field routing icin kritik/kirilgan.

---

## 2026-02-23 - Derin Inceleme (Data-Science + Graphics + Sistem)

### Data-Science Katmani
- `statistical_tests.py` / `StatisticalTests`
  - Kritik metotlar: `cmd_mean`, `cmd_shapiro`, `cmd_ttest`, `cmd_anova`, `cmd_bonferroni`, `cmd_permtest`, `cmd_ols`, `cmd_arima`.
  - Yan etki paterni: test/model sonucu context degiskenlerine yazim + stdout raporlama.
- `numpy_operations.py` / `NumpyOperations`
  - Kritik metotlar: `cmd_arange`, `cmd_meshgrid`, `cmd_reshape`, `cmd_dot`, `cmd_histogram`, `cmd_concatenate`, `cmd_interp`, `cmd_gradient`.
  - Yan etki paterni: hesap sonucu context'e yazim, cogu komutta print ciktisi.
- `pandas_operations.py` / `PandasOperations`
  - Kritik metotlar: `cmd_dataframe`, `cmd_read_csv`, `cmd_to_csv`, `cmd_groupby`, `cmd_merge`, `cmd_fillna`, `cmd_rolling`, `cmd_resample`, `cmd_query`, `cmd_loc`.
  - Yan etki paterni: DataFrame donusleri + dosya I/O (`read_csv/to_csv`).

### Graphics Katmani
- `graphics_system.py` / `GraphicsSystem` (monolitik ana sinif)
  - Alt sistemler: sprite, font/text, collision/z-order, animation/tween/timeline, camera/viewport/layer/postprocess, lighting/particle/audio/physics.
  - Kritik metotlar: `cmd_screen`, `cmd_get_image`, `cmd_input`, `cmd_sprite_create_ascii`, `cmd_sprite_load`, `cmd_sprite_move`, `cmd_sprite_info`, `cmd_font_load`, `cmd_text_draw`, `cmd_collision_list`, `cmd_sprite_sort`, `cmd_animation_create`, `cmd_tween_create`, `cmd_tween_update`, `cmd_timeline_create`, `cmd_timeline_update`, `cmd_camera_follow`, `cmd_effect_add`, `cmd_sound_play_3d`, `cmd_body_create`.

### Sistem Katmani (I/O ve Altyapi)
- `file_operations.py` / `FileOperations`
  - Kritik metotlar: `cmd_open`, `cmd_close`, `cmd_write`, `cmd_read`, `cmd_line_input`, `cmd_seek`, `execute_tell`, `cmd_delete`, `cmd_rename`, `cmd_copy`, `cmd_mkdir`, `cmd_rmdir`, `cmd_chdir`.
- `network_operations.py` / `NetworkOperations`
  - Kritik metotlar: `cmd_http_get/post/put/delete`, `cmd_http_header`, `cmd_socket_open/connect/send/receive/listen/accept`, `execute_url_encode/decode`, `execute_json_encode/decode`.
- `database_operations.py` / `DatabaseOperations`
  - Kritik metotlar: `cmd_db_connect`, `cmd_db_use`, `cmd_db_query`, `cmd_db_execute`, `cmd_db_fetch`, `execute_db_fetchall`, `cmd_db_commit`, `cmd_db_rollback`, `execute_db_rowcount`, `execute_db_lastid`.
- `event_system.py` / `EventSystem`
  - Kritik metotlar: `cmd_on_event`, `cmd_subscribe`, `cmd_trigger`, `cmd_emit`, `cmd_unsubscribe`, `cmd_queue_event`, `cmd_process_events`, `execute_event_count`, `cmd_clear_event`, `cmd_clear_all_events`.
- `linq_operations.py` / `LinqOperations`
  - Kritik metotlar: `cmd_map`, `cmd_filter`, `cmd_reduce`, `cmd_orderby`, `cmd_orderbydesc`, `cmd_groupby`, `cmd_join`, `cmd_union`, `cmd_intersect`, `cmd_except`, `cmd_chunk`, `cmd_partition`.
- `string_operations.py` / `StringOperations`
  - Kritik metotlar: `execute_mid`, `execute_instr`, `execute_replace`, `execute_format`, `execute_val`, `execute_strarray`, `execute_strget`, `execute_strset`, `execute_strmatch`, `execute_strswap`.
- `math_operations.py` / `MathOperations`
  - Kritik metotlar: `execute_sqr`, `execute_rnd`, `execute_log`, `execute_log10`, `execute_pow`, `execute_mod`, `execute_factorial`, `execute_gcd`, `execute_lcm`.

### Derin Risk Ozeti (kod kanitli)
- `graphics_system.py`: cift `super().__init__` cagrisi + cok buyuk tek sinif + bazi stub komutlar.
- Data-science modullerinde handler imza/yardimci metod sozlesmesi kirilganligi riski (BaseCommand execute sozlesmesi ile uyum hassas).
- `network_operations.py`: timeout/retry politikasi zayifsa bloklama riski.
- `database_operations.py`: `DB.QUERY` dogrudan SQL birlestirmede enjeksiyon riski; `DB.EXECUTE` daha guvenli yol.
- `event_system.py`: kuyruk isleme ve hata yutma modeli uzun kuyruk/hata gozlenebilirligini etkileyebilir.

---

## 2026-02-23 - Dosya Bazli Teknik Borc Backlog (Oncelikli)

### P0 (hemen ele alinacak)
- `graphics_system.py`
  - Sorun: cift init cagrisi, monolitik boyut, stub komutlar.
  - Ilk adim: cift `super().__init__` temizligi + stub komutlari `NotImplementedError` veya net fallback ile standartlastirma.
- `statistical_tests.py`, `numpy_operations.py`, `pandas_operations.py`
  - Sorun: BaseCommand handler sozlesmesiyle imza/yardimci API kirilganligi riski.
  - Ilk adim: command handler imzalarini `handler(args, context)` uyumunda dogrulama ve duzeltme listesi.

### P1 (kisa vadeli)
- `database_operations.py`
  - Sorun: `DB.QUERY` tarafinda SQL birlestirme kaynakli guvenlik riski.
  - Ilk adim: parametreli sorgu yolunu varsayilan hale getirme, `DB.QUERY` icin uyarili/guvenli mod.
- `network_operations.py`
  - Sorun: timeout/retry eksikligi nedeniyle bloklama ve dayaniklilik riski.
  - Ilk adim: varsayilan timeout + sinirli retry politikasi.
- `event_system.py`
  - Sorun: kuyruk performansi ve hata gozlenebilirligi.
  - Ilk adim: FIFO veri yapisi iyilestirme ve structured error kaydi.

### P2 (orta vadeli)
- `linq_operations.py`
  - Sorun: eval tabanli ifade calistirma ve O(n*m) join maliyeti.
  - Ilk adim: guvenli expression subset + buyuk koleksiyonlarda guard/limit.
- `string_operations.py`
  - Sorun: cok genis API yuzeyi ve davranis tutarsizlik riski.
  - Ilk adim: komut sozlesme tablosu (girdi/cikti/hata) ve test matrisi.

---

## 2026-02-23 - P0 Icra Baslangici (`graphics_system.py`)

### Yapilanlar
- Cift `super().__init__(interpreter)` cagrisi tekilleştirildi.
- Placeholder komutlar calisan minimum davranisa cevrildi:
  - `cmd_point`: bellek tabanli piksel tamponundan deger dondurur.
  - `cmd_wait`: emule port kosulu icin timeout'lu bekleme uygular.
  - `cmd_inkey`: non-blocking tus okuma (platforma gore).
  - `cmd_getkey`: blocking tus okuma (platforma gore).
  - `cmd_kbhit`: klavye durumunu 0/1 dondurur.
- Grafik verisi icin `_pixel_buffer` eklendi; `cmd_pset/cmd_preset/cmd_get_image/cmd_put_image` bu tamponla calisacak sekilde guncellendi.
- Interpreter degisken erisim kirilganligini azaltmak icin `_set_variable` ve `_get_variable` yardimcilari eklendi.

### Davranis Notu
- Stub komutlar disari alinmadi; yerinde calisan kod tercih edildi.
- Donanim-port WAIT gercek donanim yerine `context['__ports__']` uzerinden emule edildi (timeout korumali).
