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
