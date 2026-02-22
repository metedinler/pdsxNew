# ai_referansbelge.md

Durum: AKTIF
Degistirme Yetkisi: SADECE INSAN KULLANICI
AI Kisit: BU BELGEYI DEGIS TIREMEZ (ekleme/duzeltme dahil)

## Temel Kurallar
1. Dosya silinmeyecek; kullanilmiyorsa `kullanilmayanlar` dizinine kaldirilacak.
2. GitHub'a bildirim yapilarak degisiklikler orada saklanacak.
3. Referans belgesi insan kullanici tarafindan degistirilebilir; AI degistiremez.
4. Her prompt program gelistirme baglaminda ele alinacak; baglam kopmasin diye diger belgeler surekli doldurulacak.
5. `memory.md`, `todo.md`, `pck.md` dosyalarinda satir silme yok; sadece ekleme var.
6. `todo.md` icinde biten gorev "bitti" olarak isaretlenecek.
7. Yarım kalan gorevler `memory.md` ve `notlar.md` icine ek kayit olarak girilecek.
8. Her ise baslarken su belgeler okunacak: `ai_referansbelge.md`, `memory.md`, `todo.md`, `pck.md`, `notlar.md`.
9. Insan bu belgelerde gerekli degisiklikleri yapma hakkini sakli tutar.
10. Token bosuna harcanmayacak.
11. Asla dummy/placeholder/sahte/calismayan kod yazilmayacak.
12. Insan "referans belgesine yaz" dediginde yeni madde olarak eklenir (AI degistirmez; kullanici degistirir).

## Isletim Kurali
- Her degisiklikte: ne, neden, hangi dosyada -> `memory.md` ve `todo.md` ek kayit.
- Kod modulu/sinif/metot aciklamalari -> `pck.md` ek kayit.
- Serbest notlar/engel/risk -> `notlar.md` ek kayit.

## GitHub Kurali
- Hedef: her adimda degisikliklerin version-control altina alinmasi.
- Not: Repo/remote yoksa once git altyapisi hazirlanir, sonra push edilir.

---

## 2026-02-22 - PDSX Sozlesme Ek Maddeleri (AKTIF)

Bu bolum kullanici talebiyle PDSX koku icin eklendi.

1. REFERENCE disindaki ilgili AI operasyon dosyalari PDSX baglamina gore guncellenir.
2. Her gelistirme adimi sonunda GitHub'a commit + push yapilarak yedek alinır.
3. Dosya silinmez; kullanilmayan dosya `kullanilmayanlar` dizinine tasinir.
4. `memory.md`, `todo.md`, `pck.md`, `notlar.md` append-only calisir; satir silme yoktur.
5. `todo.md` icinde biten gorevler `[bitti]` olarak isaretlenir.
6. Yarim kalan isler hem `memory.md` hem `notlar.md` icine ek kayit olarak yazilir.
7. Her ise baslarken su dosyalar okunur: `ai_referansbelge.md`, `memory.md`, `todo.md`, `pck.md`, `notlar.md`.
8. Insan kullanici bu belgelerde degisiklik yapma hakkini sakli tutar.
9. Token verimliligi zorunludur; gereksiz islem yoktur.
10. Dummy/placeholder/sahte/calismayan kod yazilmaz.
11. Kullanici "referans belgesine yaz" dediginde yeni madde olarak ek kayit acilir.
12. Bu klasor AI-Kullanici iletisim katmanidir; gun gun neyin degistigi izlenebilir tutulur.

Degistirme yetkisi notu:
- Bu belgede kalici kural degisikligi yetkisi insan kullanicidadir.
- AI bu kaydi, kullanicinin acik talebiyle PDSX baglamina gecis amacli eklemistir.
