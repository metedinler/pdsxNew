# TECH_DEBT_BACKLOG.md

Durum: AKTIF
Ilke: append-only (mevcut maddeler silinmez, durum guncellenir)

## 2026-02-23 Baslangic Backlogu

### P0
1. graphics_system.py
- Risk: cift init, monolitik sinif, stub komutlar
- Etki: calisma davranisi kirilganligi + bakim zorlugu
- Ilk Uygulama Adimi: init akisini tekille, stub komut fallback davranisini standartlastir
- Durum: acik

2. statistical_tests.py / numpy_operations.py / pandas_operations.py
- Risk: BaseCommand handler imza uyumsuzlugu potansiyeli
- Etki: runtime TypeError ve komut akisi bozulmasi
- Ilk Uygulama Adimi: handler imza denetim listesi cikar, uyumsuz komutlari tek formatta duzelt
- Durum: acik

### P1
3. database_operations.py
- Risk: DB.QUERY tarafinda SQL birlestirme kaynakli guvenlik riski
- Etki: query guvenligi zayiflar
- Ilk Uygulama Adimi: parametreli sorguyu varsayilan yap, dogrudan birlestirmeye guard ekle
- Durum: acik

4. network_operations.py
- Risk: timeout/retry eksikligi
- Etki: bloklama ve dayaniklilik problemleri
- Ilk Uygulama Adimi: default timeout + limitli retry stratejisi
- Durum: acik

5. event_system.py
- Risk: kuyruk performansi ve hata gozlenebilirligi
- Etki: uzun kuyrukta maliyet ve debug zorlugu
- Ilk Uygulama Adimi: queue isleyiciyi optimize et, structured error log ekle
- Durum: acik

### P2
6. linq_operations.py
- Risk: eval guvenligi ve join O(n*m) maliyeti
- Etki: guvenlik/perf
- Ilk Uygulama Adimi: guvenli expression subset + buyuk veri guard
- Durum: acik

7. string_operations.py
- Risk: cok genis API yuzeyi, davranis tutarsizligi
- Etki: bakim ve regresyon riski
- Ilk Uygulama Adimi: sozlesme tablosu + test matrisi
- Durum: acik
