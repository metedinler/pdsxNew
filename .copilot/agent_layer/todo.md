# todo.md (append-only)

## Aktif Gorevler
- [ ] Git altyapisini dogrula ve GitHub remote bagla
- [ ] Her adim icin commit/push akisi standardi kur
- [ ] ChlorellaOS ana modullerinin pck kaydini derinlestir
- [ ] pdsX-disina tasinan klasorde build/saglik kontrolu

## Biten Gorevler
- [bitti] Agent iletisim katmani dosyalari olusturuldu (`ai_referansbelge.md`, `memory.md`, `todo.md`, `pck.md`, `notlar.md`)
- [bitti] Onceki AI tarafindan hazirlanan temel `.copilot` belgeleri tespit edildi
- [bitti] `agent_layer` dosyalari git commit ile kaydedildi (`914bab5`)
- [bitti] GitHub remote `origin` baglandi (`https://github.com/metedinler/pdsxNew.git`)
- [bitti] `main` dali ilk push ile GitHub'a gonderildi ve takip iliskisi kuruldu

## Bekleyen Kararlar
- [ ] GitHub repo URL/organizasyon hedefi
- [ ] Push yetkisi (token/credential)

## Yeni Eklenen Gorevler
- [ ] `git remote add origin <repo-url>` ile GitHub remote baglamak
- [ ] `git push -u origin master` ile ilk yedegi GitHub'a gondermek

## Yeni Eklenen Gorevler (Guncel)
- [ ] Her is adimi sonunda `add/commit/push` standardini uygulamak

## 2026-02-23 - PDSX Duzenleme Paketi (Tek Seferlik)

### Aktif Gorevler (PDSX)
- [ ] `.copilot/agent_layer` dosyalarini anlam koruyarak daha duzenli hale getir
- [ ] PDSX modullerinin sinif/metot envanterini `pck.md` icine standart formatta ekle
- [ ] Root git repository olustur ve sadece agent-layer degisikliklerini commitle
- [ ] Her adim sonunda GitHub'a push et (branch bazli yedek)

### Biten Gorevler (PDSX)
- [bitti] `ai_referansbelge.md` icine PDSX sozlesme maddeleri append edildi
- [bitti] PDSX koku icin class/def taramasi baslatildi (ilk cikti alindi)

### Not
- Onceki ChlorellaOS odakli gorev kayitlari silinmemis, tarihsel iz olarak korunmustur.

## 2026-02-23 - Durum Guncellemesi

### Biten Gorevler
- [bitti] `agent_layer` duzenleme paketi tamamlandi (anlam/amac korunarak)
- [bitti] Root repo init + branch (`pdsx-root-backup`) tamamlandi
- [bitti] GitHub push tamamlandi (`origin/pdsx-root-backup`)

### Sonraki Gorevler
- [ ] PDSX tum modullerinin sinif ve temel metotlarini parca parca `pck.md` icine derinlestir
- [ ] Her yeni degisiklik adiminda commit + push rutini surdur

## 2026-02-23 - Interpreter Inceleme Durumu

### Biten Gorevler
- [bitti] Interpreter yapisi (init/parse/router/execute/run) cozuldu
- [bitti] Komut/module haritasi cikarildi ve `pck.md` kaydi yapildi

### Sonraki Gorevler
- [ ] Modul bazli sinif-metot seviyesinde detaylandirma (ilk hedef: `core_commands`, `variable_manager`, `flow_control`, `loop_control`)

## 2026-02-23 - Paralel Alt Ajan Durumu

### Biten Gorevler
- [bitti] Uc alt ajan ile moduller paralel cozuldu (cekirdek, oop/function/type, sistem+veri bilimi)
- [bitti] `pck.md` icine sinif/metot/modul derin envanteri append edildi

### Sonraki Gorevler
- [ ] Kritik modullerde metod seviyesinde davranis ozetini (girdi/cikti/yan etki) eklemeye basla

## 2026-02-23 - Devam Durumu

### Biten Gorevler
- [bitti] Kritik moduller icin metod davranis sozlugu eklendi (`core/variable/flow/loop`)

### Sonraki Gorevler
- [ ] Method-level sozlugu `function_manager` + `oop_system` + `advanced_types` icin devam ettir

## 2026-02-23 - Coklu Gorev Arkadaslari Durumu

### Biten Gorevler
- [bitti] `function_manager` method-level sozluk
- [bitti] `oop_system` method-level sozluk
- [bitti] `advanced_types` + `data_structures` method-level sozluk

### Sonraki Gorevler
- [ ] Data science ve graphics modullerinde ayni method-level sozlugu tamamla

## 2026-02-23 - Derin Inceleme Faz 2 Durumu

### Biten Gorevler
- [bitti] Data-science modulleri method-level sozluk kaydi
- [bitti] Graphics modulu method-level sozluk kaydi
- [bitti] Sistem modulleri (file/network/db/event/linq/string/math) method-level sozluk kaydi

### Sonraki Gorevler
- [ ] Kritik riskler icin teknik borc/backlog maddelerini dosya-bazli ac (oncelik: graphics, statistical, pandas/numpy)

## 2026-02-23 - Teknik Borc Durumu

### Biten Gorevler
- [bitti] Dosya-bazli teknik borc maddeleri acildi (P0/P1/P2)
- [bitti] `TECH_DEBT_BACKLOG.md` olusturuldu

### Sonraki Gorevler
- [ ] P0 maddelerini tek tek uygulama adimina cevir (ilk hedef: `graphics_system.py` init/stub temizligi)

## 2026-02-23 - P0 Icra Durumu (Graphics)

### Biten Gorevler
- [bitti] `graphics_system.py` cift init temizligi
- [bitti] Stub/placeholder komutlarin calisan minimum implementasyonu
- [bitti] Dosya sentaks dogrulamasi

### Sonraki Gorevler
- [ ] Graphics komutlarini test .pdsx dosyalariyla syntax-uyumlu sekilde dogrula (sprite/ascii/collision)

## 2026-02-23 - Legacy Syntax Uyumluluk Durumu

### Biten Gorevler
- [bitti] `pdsx_interpreter.py` multi-word parser listesine legacy sprite/collision komutlari eklendi
- [bitti] `graphics_system.py` icinde legacy komutlar icin compatibility wrapper kayitlari eklendi
- [bitti] Parse smoke test ile `CREATE IMAGE SPRITE`, `DRAW SPRITE`, `COLLISION ON/OFF` parse ciktilari dogrulandi

### Sonraki Gorevler
- [ ] Legacy komutlarin `execute_line` seviyesinde mini runtime akisini dogrula (ortam bagimli)

## 2026-02-23 - Execute-Line Dogrulama Durumu

### Biten Gorevler
- [bitti] `execute_line` uzerinden `COLLISION ON/OFF` runtime akisi dogrulandi
- [bitti] `execute_line` uzerinden `CREATE ASCII SPRITE` + `DRAW SPRITE` runtime akisi dogrulandi
- [bitti] `CREATE ASCII SPRITE` icin iki legacy arguman sirasi destegi eklendi
- [bitti] Yanlis `pdsxu_venv` auto-install akisina koruma eklendi

### Sonraki Gorevler
- [ ] `CREATE IMAGE SPRITE ... AS IMAGE` icin dosya-yok/dosya-var senaryolu kisa runtime kontrolu yap

## 2026-02-27 - Image Sprite Runtime Durumu

### Biten Gorevler
- [bitti] `CREATE IMAGE SPRITE ... AS IMAGE` dosya-var runtime senaryosu dogrulandi
- [bitti] `CREATE IMAGE SPRITE ... AS IMAGE` dosya-yok runtime hata senaryosu dogrulandi
- [bitti] Legacy dusuk image sprite ID'leri ic image araligina maplenerek (`129-256`) calisma dogrulandi

### Sonraki Gorevler
- [ ] Legacy `DRAW SPRITE id AT x,y` (dosya argumansiz) kullanimlarini .pdsx oyun dosyalarinda tarayip uyum denetimi yap

## 2026-02-27 - Legacy DRAW Tarama Durumu

### Biten Gorevler
- [bitti] `.pdsx` oyun dosyalarinda `DRAW SPRITE` kullanimlari tarandi
- [bitti] `DRAW SPRITE id AT x,y` (dosya argumansiz) kullanim vakasi bulunmadi

### Sonraki Gorevler
- [ ] `graphics_system.py` icin tip-anotasyon odakli kademeli temizlik plani cikar (Optional context imzalari oncelikli)

## 2026-02-27 - Graphics Tip Temizligi Faz-1 Durumu

### Biten Gorevler
- [bitti] `graphics_system.py` uyumluluk metotlarinda `Optional context` gecisi
- [bitti] `None context` icin `ctx` normalize akisi eklendi
- [bitti] Hata sayisinda ilk dusus dogrulandi (405 -> 374)

### Sonraki Gorevler
- [ ] Faz-2: dosya genelinde `context: Dict[str, Any] = None` imzalarini toplu normalize et (davranis degistirmeden)
