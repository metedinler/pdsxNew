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

## 2026-02-23 - Coklu Ajan Tur Notu
- OOP/function/type katmani method-level olarak haritalandi.
- Router bagimli akislarda (`FUNCTION`/`FIELD`) context flag tutarliligi kritik olarak not edildi.
- Stub metotlar ve imza kirilganligi sonraki teknik borc listesine alinmali.

## 2026-02-23 - Derin Inceleme Faz 2 Notu
- Graphics katmani tek dosyada asiri buyuk ve bakim maliyeti yuksek.
- Data-science modullerinde method imza/yardimci API uyumunun dikkatle dogrulanmasi gerekiyor.
- DB ve network tarafinda guvenlik/dayaniklilik (query kullanimi, timeout/retry) iyilestirme adayi.

## 2026-02-23 - Teknik Borc Plan Notu
- Backlog dosyasi acildi ve oncelikler sabitlendi (P0/P1/P2).
- Uygulama sirasinda once P0 maddeleri, sonra P1/P2 alinacak.

## 2026-02-23 - Graphics Uygulama Notu
- Stub komutlari cikarmak yerine yerinde calisan kod yazimi tercih edildi.
- WAIT komutu emulasyon temelli oldugu icin donanim semantigi sinirli, ama bloklama/timeout kontrollu.
- Klavye komutlarinda platforma gore (Windows/curses/fallback) katmanli davranis kullanildi.

## 2026-02-23 - Legacy Syntax Uyumluluk Notu
- Legacy `.pdsx` scriptlerdeki `CREATE IMAGE SPRITE`, `DRAW SPRITE`, `COLLISION ON/OFF` komutlari parser seviyesinde taninmiyordu; parser listesi genisletilerek cozuldu.
- Graphics tarafinda compatibility wrapper eklenerek mevcut engine fonksiyonlarina kopru kuruldu.
- Parse smoke test basarili; ancak interpreter import sirasinda ortamda eksik paket uyarilari goruldu (`pygame`, `windows-curses`) ve otomatik kurulum yolu yerel venv path hatasi verdi.
- Bu paket uyarilari parse dogrulamasini engellemedi; runtime/GUI davranisi dogrulamasi icin ortam paketlerinin saglam kurulumu gerekir.

## 2026-02-23 - Execute-Line ve Venv Koruma Notu
- Auto paket kontrolu `pdsxu_venv` yokken calisiyordu ve yanlis path'e pip cagrisi yapiyordu; interpreter tarafinda koruma eklendi.
- Bu degisiklik execute-line smoke testin gürültü/kilitlenme riskini azaltti.
- Halen bilinen durum: bazi moduller import sirasinda eksik opsiyonel paket uyari metinleri basiyor (`nltk`, `GitPython`, `requests`, `flask`, `pygame`).
- Fonksiyonel etki: legacy komutlar execute seviyesinde calisiyor; GUI/ileri ozelliklerde paket bagimliliklari ayrica ele alinmali.

## 2026-02-27 - Image Sprite Uyum Notu
- Legacy image komutlari dusuk ID ile geldiginde (`1..`) artik ic image araligina mapleniyor (`129..256`).
- Risk notu: diger komutlar dogrudan `sprite_id` bekliyorsa legacy->internal map bilgisini bilmeyebilir; bu nedenle legacy uyumluluk komutlari uzerinden kullanimi korunmali.
- Test edilen durumlar:
	- dosya var -> basarili olusum ve draw
	- dosya yok -> kontrollu hata (beklenen)
