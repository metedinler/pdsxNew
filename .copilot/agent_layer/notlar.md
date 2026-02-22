# notlar.md (append-only)

## 2026-02-22 - Operasyon Notlari
- Mevcut klasor bir git repository degil (`git rev-parse` hatasi alinmisti).
- GitHub'a adim adim gonderim icin once repo init + remote set + auth gerekecek.
- `chlorellaOS` kokunde cok sayida arsiv/rapor dosyasi var; cekirdek app `src/` + config dosyalari.
- Kullanici talebine gore backup dosyalari silinmedi, sistematik arsive alindi.

## 2026-02-22 - Ek Notlar
- Git repository baslatildi ve ilk commit alindi: `914bab5`.
- Bu commit sadece `.copilot/agent_layer` dosyalarini icerir.
- GitHub push denemesi yapilmadi; cunku remote URL verilmedi.

## 2026-02-22 - GitHub Senkron Notu
- Kullanici tarafindan verilen yeni repo adresi tanimlandi: `https://github.com/metedinler/pdsxNew.git`.
- `main` dalina push basarili oldu.
- Bundan sonra her prompt/degisiklik adiminda commit+push rutini uygulanacak.

## 2026-02-23 - Duzenleme Notu (PDSX)
- Kullanici talebi: `REFERENCE` haric dosyalar duzenlenecek, anlam/amac korunacak.
- Uygulama sekli: append-only dosyalarda satir silmeden yeni duzen bolumleri eklenecek.
- Kapsam: `.copilot/agent_layer/*` dosyalari.

## 2026-02-23 - Yarim Kalanlar
- Root klasor (`pdsx_commands`) henuz git repo degil; bu nedenle adim-bazli push rutini burada aktif degil.
- Cozum adimi: root repo init + branch + remote + ilk push.

## 2026-02-23 - Cozuldu
- Root klasorde git aktif edildi ve branch acildi: `pdsx-root-backup`.
- Uzak yedek basarili: `origin/pdsx-root-backup`.
- Bundan sonraki adimlar ayni branch uzerinden atomik commit+push olarak ilerletilecek.

## 2026-02-23 - Interpreter Inceleme Notlari
- Router logic kritik: `FUNCTION` ve `FIELD` komutlari context'e gore farkli modullere yonleniyor.
- Cakisan komut override kurali var (`CLS`, `SLEEP`, `INPUT`, `GETKEY` -> core).
- Alias/space-version kayitlari sebebiyle komut adedi ve register sayisi birebir ayni olmayabilir.

## 2026-02-23 - Paralel Alt Ajan Risk Notlari
- `graphics_system.py` ve `statistical_tests.py` bakim maliyeti yuksek gorunuyor (tek dosyada cok genis komut yuzeyi).
- Router bagimli komutlar (`FUNCTION`, `FIELD`) context flag'lerine hassas; yanlis flag akisi davranis farki uretebilir.
- register sayisi ile gercek efektif komut adedi birebir ayni degil (alias/space kayitlari).

## 2026-02-23 - Devam Notu
- Method-level sozlukte context yan etkileri acik yazildi; debugger ve router ariza analizinde dogrudan kullanilabilir.
- Sonraki derinlestirme hedefi OOP/function/type katmani.
