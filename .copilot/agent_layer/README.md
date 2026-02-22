# agent_layer README

Durum: AKTIF
Amac: AI-Kullanici iletisim katmanini tek noktadan izlemek.

## Dosya Rolleri
- `ai_referansbelge.md`: AI icin calisma kurallari (sozlesme niteligi).
- `memory.md`: Gun gun degisiklik hafizasi (append-only).
- `todo.md`: Gorev listesi, aktif/biten durumlar (append-only).
- `pck.md`: Programcinin cep kitabi; modul/sinif/metot aciklamalari (append-only).
- `notlar.md`: Risk/engel/yarim kalan notlari (append-only).
- `found_previous_agent_assets.md`: Onceki ajan dosya varliklari envanteri.

## Isleyis
1. Her ise baslarken: `ai_referansbelge.md`, `memory.md`, `todo.md`, `pck.md`, `notlar.md` okunur.
2. Her degisiklikten sonra en az su kayitlar guncellenir:
   - Teknik degisiklik: `pck.md`
   - Islem kaydi: `memory.md`
   - Durum/gorev: `todo.md`
   - Risk/yarim kalan: `notlar.md`
3. Dosya silinmez; kullanilmiyorsa `kullanilmayanlar` dizinine tasinir.

## Not
- Bu README anlam degisikligi yaratmaz; sadece gezinme ve devamlilik kolayligi saglar.
