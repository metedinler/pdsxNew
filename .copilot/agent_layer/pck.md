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
