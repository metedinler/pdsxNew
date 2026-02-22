# pck.md (Programcinin Cep Kitabi) - append-only

## Modul Ozeti (Baslangic)

### 1) `src/main.jsx`
- Amac: React giris noktasi, `App` render, `ErrorBoundary` sarmalama, `RecommendationEngine` global init.
- Onem: Uygulamanin acilis davranisini belirler.

### 2) `src/App.jsx`
- Amac: Ana UI orkestrasyonu (tab secimi, provider katmanlari, component rotasi).
- Ana Yapilar:
  - `EnforcedChlorellaSystemProvider`
  - `MaterialsProvider`
  - `SimulationWorker` start/stop
- Onem: Tum islevlerin kullaniciya acildigi merkez.

### 3) `src/contexts/EnforcedChlorellaSystemContext.jsx`
- Amac: Dijital ikiz kurallariyla merkezi state yonetimi.
- Temel Kavramlar:
  - ACTION tabanli reducer
  - Tank bazli state
  - Model-state senkronizasyonu
- Onem: Single source of truth.

### 4) `src/workers/SimulationWorker.js`
- Amac: Arka planda periodik simülasyon ve risk kontrolu.
- Islevler:
  - start/stop
  - runHourlySimulation
  - evaluateRisks
  - forecast24Hours
- Onem: Operasyonel tahmin/risk katmani.

### 5) `src/utils/stateSynchronizer.js`
- Amac: Context <-> Model iki yonlu senkronizasyon.
- Islevler:
  - syncContextToModel
  - syncModelToContext
  - bidirectionalSync
- Onem: Veri tutarliligi ve izlenebilirlik.

### 6) `src/utils/databaseManager.js`
- Amac: Export/import ve backup odakli veri operasyonlari.
- Islevler:
  - exportChemicalDatabase
  - exportTankData
  - exportAllSystemData
  - importTankData
  - importFullSystemData
- Onem: Tasima, geri donus ve yedekleme.

### 7) `src/utils/userManager.js`
- Amac: Profil/tercih/favori/ozel tarif/gecmis yonetimi (localStorage).
- Onem: Kullanici deneyimi ve kalicilik.

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
